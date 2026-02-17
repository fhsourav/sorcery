import re
import random
import time
from typing import Union

import discord
import lavalink

from discord.ext import commands

from bot import LavalinkVoiceClient, Utils


class MusicCoreService:

	async def create_player(ctx: discord.ApplicationContext):
		"""
		A check that is invoked before any commands marked with `@discord.Bot.check(create_player)` can run.

		This function will try to create a player for the guild associated with this Context, or raise an error which will be relayed to the user if one cannot be created.
		
		:param ctx:
		:type ctx: discord.ApplicationContext
		"""

		if ctx.guild is None:
			raise commands.NoPrivateMessage()
		
		player: lavalink.DefaultPlayer = ctx.bot.lavalink.player_manager.create(ctx.guild.id)

		# Create returns a player if one exists, otherwise creates.
		# This line is important because it ensures that a player always exists for a guild.
		
		# Most people might consider this a waste of resources for guilds that aren't playing, but this is the easiest and simplest way of ensuring players are created.

		# These are commands that require the bot to join a voicechannel (i.e. initiating playback).
		should_connect = ctx.command.name in ('play',)

		voice_client = ctx.voice_client

		if not ctx.author.voice or not ctx.author.voice.channel:
			# Check if we're in a voice channel. If we are, tell the user to join our voice channel.
			if voice_client is not None:
				message = f'Please join {voice_client.channel} to use this command'
				await ctx.respond(message, ephemeral=True)
				raise discord.errors.ApplicationCommandInvokeError(message)
			
			# Otherwise, tell them to join any voice channel to begin playing music.
			message = 'Please join a voice channel first.'
			await ctx.respond(message, ephemeral=True)
			raise discord.errors.ApplicationCommandInvokeError(message)

		voice_channel = ctx.author.voice.channel

		if voice_client is None:
			if not should_connect:
				await ctx.respond("I'm not playing music.", ephemeral=True)
				raise discord.errors.ApplicationCommandInvokeError("I'm not playing music.")
			
			permissions = voice_channel.permissions_for(ctx.me)

			if not permissions.connect or not permissions.speak:
				await ctx.respond("I need the `CONNECT` and `SPEAK` permissions.", ephemeral=True)
				raise discord.errors.ApplicationCommandInvokeError("I need the `CONNECT` and `SPEAK` permissions.")
			
			if voice_channel.user_limit > 0:
				# A limit of 0 means no limit. Anything higher means that there is a member limit which we need to check.
				# If it's full, and we don't have `move members` permissions, then we cannot join it.
				if len(voice_channel.members) >= voice_channel.user_limit and not ctx.me.guild_permissions.move_members:
					await ctx.respond("Your voice channel is full!", ephemeral=True)
					raise discord.ApplicationCommandInvokeError("Your voice channel is full!")
				
			player.store('channel', ctx.channel.id)
			player.store('autoplay', False)
			player.store('history', [])
			player.volume = 30
			await ctx.author.voice.channel.connect(cls=LavalinkVoiceClient)

		elif voice_client.channel.id != voice_channel.id:
			message = f'Please join {voice_client.channel} to use this command'
			await ctx.respond(message, ephemeral=True)
			raise discord.errors.ApplicationCommandInvokeError(message)
		
		return True
	

	async def autocomplete_query(self, ctx: discord.AutocompleteContext):
		"""
		Docstring for autocomplete_query
		
		:param self: Description
		:param ctx: Description
		:type ctx: discord.AutocompleteContext
		"""

		if not ctx.interaction.user.id in self.search_results:
			self.search_results[ctx.interaction.user.id] = {}
		else:
			self.search_results[ctx.interaction.user.id].clear() # clear previous query info (if any) from the self.search_results dictionary

		src = "" if ctx.options["source"] is None else ctx.options["source"]

		search_result: lavalink.LoadResult = await ctx.bot.lavalink.get_tracks(f"{src}{ctx.value}") # generating tracklist from the value of the query

		if search_result.load_type == lavalink.LoadType.PLAYLIST:
			self.search_results[ctx.interaction.user.id][search_result.playlist_info.name[:100]] = search_result

		if search_result.load_type == lavalink.LoadType.EMPTY or search_result.load_type == lavalink.LoadType.ERROR:
			return ["Could not find anything for that query."]
		
		for track in search_result.tracks:
			track_str = f"[{Utils.milli_to_minutes(track.duration)}] {track.title[:50]} by {track.author[:20]} ({track.source_name})"
			self.search_results[ctx.interaction.user.id][track_str] = track
		
		return [
			result for result in self.search_results[ctx.interaction.user.id]
		]
	

	async def play(ctx: discord.ApplicationContext, chosenResult: Union[lavalink.AudioTrack, lavalink.DeferredAudioTrack, lavalink.LoadResult]):
		"""
		Docstring for play
		
		:param ctx: Description
		:type ctx: discord.ApplicationContext
		:param chosenResult: Description
		:type chosenResult: Union[lavalink.AudioTrack, lavalink.DeferredAudioTrack, lavalink.LoadResult]
		"""
		# Get the player for this guild from cache
		player: lavalink.DefaultPlayer = ctx.bot.lavalink.player_manager.get(ctx.guild.id)

		added_at = int(time.time())

		if isinstance(chosenResult, lavalink.LoadResult): # check if the chosenResult is a playlist
			tracks = chosenResult.tracks
			# Add all of the tracks from the playlist to the queue
			for track in tracks:
				# requester isn't necessary but it helps keep track of who queued what
				# you can store additional metadata by passing it as a kwarg (i.e. key=value)
				track.extra['added_at'] = added_at
				track.extra['albumName'] = chosenResult.playlist_info.name
				player.add(track=track, requester=ctx.author.id)
				
			await ctx.respond(f"Added the playlist **`{chosenResult.playlist_info.name} ({len(chosenResult.tracks)} tracks)`** to the queue.")
		
		else:
			track = chosenResult
			track.extra['added_at'] = added_at
			player.add(track=track, requester=ctx.author.id)

			await ctx.respond(f"Added **`{chosenResult.title} ({chosenResult.source_name})`** to the queue.")
		
		if not player.is_playing:
			await player.play()
	

	async def pausetoggle(ctx: discord.ApplicationContext):
		player: lavalink.DefaultPlayer = ctx.bot.lavalink.player_manager.get(ctx.guild.id)

		if not player.current:
			return await ctx.respond("Player is idle.")
		
		await player.set_pause(not player.paused)

		await ctx.respond(f"Playback {'paused' if player.paused else 'resumed'}.")
	

	async def disconnect(ctx: discord.ApplicationContext):
		"""
		Docstring for disconnect
		
		:param ctx: Description
		"""
		player: lavalink.DefaultPlayer = ctx.bot.lavalink.player_manager.get(ctx.guild.id)
		# The necessary voice channel checks are handled in "create_player"
		# We don't need to duplicate code checking them again

		# Clear the queue to ensure old tracks don't start playing when someone else queues something
		player.queue.clear()
		# Stop the current track so Lavalink consumes less resource
		await player.stop()
		# Disconnect from the voice channel
		await ctx.voice_client.disconnect(force=True)
		await ctx.respond(f"{ctx.bot.user.name} has gracefully left the stage. See you next time!")
	

	async def autoplay(ctx: discord.ApplicationContext, set: bool):
		"""
		Docstring for autoplay
		
		:param ctx: Description
		:type ctx: discord.ApplicationContext
		:param set: Description
		:type set: bool
		"""
		player: lavalink.DefaultPlayer = ctx.bot.lavalink.player_manager.get(ctx.guild_id)
		
		if not player.current and not player.queue:
			await ctx.voice_client.disconnect(force=True)
			return await ctx.respond("Player is idle.")

		player.store('autoplay', set)

		await ctx.respond(f"Autoplay has been {'disabled' if set == 0 else 'enabled'}.")
	

	async def add_autoplay_track(player: lavalink.DefaultPlayer, last_track_id: str):
		search_query = f"https://music.youtube.com/watch?v={last_track_id}&list=RDAMVM{last_track_id}"
		search_result: lavalink.LoadResult = await player.node.get_tracks(search_query)

		min = 0
		max = len(search_result.tracks)
		
		idx = random.randint(min, max)
		while search_result.tracks[idx].identifier == last_track_id:
			idx = random.randint(min, max)
		
		track = search_result.tracks[idx]
		player.add(track=track)
		
		if not player.is_playing:
			await player.play()
	

	async def nowplaying(ctx: discord.ApplicationContext):
		player: lavalink.DefaultPlayer = ctx.bot.lavalink.player_manager.get(ctx.guild.id)

		track = player.current

		embed = discord.Embed(
			title=track.title,
			url=track.uri,
			image=track.artwork_url,
		)

		embed.set_author(name=f"{ctx.author.nick if ctx.author.nick else ctx.author.display_name}", icon_url=ctx.author.avatar)

		embed.add_field(name="Artist", value=f"{track.extra['artistName'] if 'artistName' in track.extra.keys() else track.author}", inline=True)
		embed.add_field(name="Duration", value=Utils.milli_to_minutes(track.duration), inline=True)

		if player:
			embed.set_footer(text=MusicCoreService.get_player_state(player))
			if player.is_playing and player.current == track:
				embed.add_field(name="Elapsed", value=Utils.milli_to_minutes(player.position), inline=True)

		if track.requester:
			embed.add_field(name="Added", value=f"<t:{track.extra['added_at']}:f>", inline=True)
			embed.add_field(name="Requested by", value=f"<@{track.requester}>", inline=True)
		
		if track.extra["albumName"]:
			album = track.extra["albumName"]
			embed.add_field(name="Album", value=album, inline=True)

		embed.add_field(name="Source", value=track.source_name, inline=True)

		await ctx.respond(embed=embed)
	

	def get_player_state(player: lavalink.DefaultPlayer):
		"""
		Docstring for get_player_state
		
		:param player: Description
		:type player: lavalink.DefaultPlayer
		"""
		if not player:
			return
		
		player_state = f"{'🔁' if player.loop == player.LOOP_QUEUE else '🔂' if player.loop == player.LOOP_SINGLE else '🚫'} Loop: {'all' if player.loop == player.LOOP_QUEUE else 'one' if player.loop == player.LOOP_SINGLE else 'off'}\t\t"
		player_state += f"{'🚨' if player.volume > 100 else '🔊' if player.volume > 67 else '🔉' if player.volume > 33 else '🔈' if player.volume > 0 else '🔇'} Volume: {player.volume}\t\t\t"
		player_state += f"{'♾️' if player.fetch('autoplay') else '❎'} Autoplay: {'on' if player.fetch('autoplay') else 'off'}"

		return player_state

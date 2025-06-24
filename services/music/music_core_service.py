import re
from typing import Union

import discord
import lavalink

from discord.ext import commands

from bot import LavalinkVoiceClient, Utils


# url_rx = re.compile(r'https?://(?:www\.)?.+')


class MusicCoreService:
	
	async def create_player(ctx: discord.ApplicationContext):
		"""
		A check that is invoked before any commands marked with `@discord.Bot.check(create_player)` can run.
		
		This function will try to create a player for the guild associated with this Context, or raise
		an error which will be relayed to the user if one cannot be created.
		"""
		if ctx.guild is None:
			raise commands.NoPrivateMessage()
			return
		
		player: lavalink.DefaultPlayer = ctx.bot.lavalink.player_manager.create(ctx.guild.id)

		# Create returns a player if one exists, otherwise creates.
		# This line is important because it ensures that a player always exists for a guild.

		# Most people might consider this a waste of resources for guilds that aren't playing, but this is
		# the easiest and simplest way of ensuring players are created.

		# These are commands that require the bot to join a voicechannel (i.e. initiating playback).
		# Commands such as volume/skip etc don't require the bot to be in a voicechannel so don't need listing here.
		should_connect = ctx.command.name in ('play', 'pausetoggle', 'skip', 'volume')

		voice_client = ctx.voice_client

		if not ctx.author.voice or not ctx.author.voice.channel:
			# Check if we're in a voice channel. If we are, tell the user to join our voice channel.
			if voice_client is not None:
				ctx.respond('You need to join my voice channel first.', ephemeral=True)
				raise discord.errors.ApplicationCommandInvokeError('You need to join my voice channel first.')
			
			# Otherwise, tell them to join any voice channel to begin playing music.
			ctx.respond('Join a voice channel first.', ephemeral=True)
			raise discord.errors.ApplicationCommandInvokeError("Join a voice channel first.")
		
		voice_channel = ctx.author.voice.channel

		if voice_client is None:
			if not should_connect:
				ctx.respond("I'm not playing music.", ephemeral=True)
				raise discord.errors.ApplicationCommandInvokeError("I'm not playing music.")
			
			permissions = voice_channel.permissions_for(ctx.me)

			if not permissions.connect or not permissions.speak:
				ctx.respond("I need the `CONNECT` and `SPEAK` permissions.", ephemeral=True)
				raise discord.errors.ApplicationCommandInvokeError('I need the `CONNECT` and `SPEAK` permissions.')
			
			if voice_channel.user_limit > 0:
				# A limit of 0 means no limit. Anything higher means that there is a member limit which we need to check.
				# If it's full, and we don't have "move members" permissions, then we cannot join it.
				if len(voice_channel.members) >= voice_channel.user_limit and not ctx.me.guild_permissions.move_members:
					ctx.respond("Your voice channel is full!", ephemeral=True)
					raise discord.errors.ApplicationCommandInvokeError("Your voice channel is full!")
				
			player.store('channel', ctx.channel.id)
			await ctx.author.voice.channel.connect(cls=LavalinkVoiceClient)
		
		elif voice_client.channel.id != voice_channel.id:
			ctx.respond("You need to be in my voice channel!", ephemeral=True)
			raise discord.errors.ApplicationCommandInvokeError("You need to be in my voice channel!")
		
		return True
	

	async def autocomplete_query(self, ctx: discord.AutocompleteContext):
		"""
		Autocompletes a `/play` query based on the user's input.

		This method is used to provide autocomplete suggestions for a `/play` command
		by searching for tracks or playlists based on the user's query.

		Params:
			ctx (discord.AutocompleteContext): The context of the autocomplete interaction,
				containing user input and options.

		Returns:
			list[str]: A list of strings representing the autocomplete suggestions. If no
			results are found, the list contains a message indicating no matches.

		Behavior:
			- Extracts the `source` and `playlist` options from the context.
			- Searches for tracks or playlists using the `wavelink.Playable.search` method.
			- If no results are found, returns the user's query or a default message.
			- Stores the search results in `self.search_results` for the user, clearing any
			  previous results for the same user.
			- If the query is a playlist and the result is a playlist, stores the playlist
			  in `self.search_results`. Otherwise, stores individual tracks with formatted
			  strings as keys.
			- Limits track title and author strings to 50 and 20 characters respectively
			  for display purposes.
		"""
		if not ctx.interaction.user.id in self.search_results:
			self.search_results[ctx.interaction.user.id] = {}
		else:
			self.search_results[ctx.interaction.user.id].clear() # clear previous query info (if any) from the self.tracks dictionary

		src = "" if ctx.options["source"] is None else ctx.options["source"]

		# print(f'{src}{ctx.value}')

		search_result: lavalink.LoadResult = await ctx.bot.lavalink.get_tracks(f'{src}{ctx.value}') # generating tracklist from the value of the query
		
		# if tracklist is empty, return the value of the query
		if search_result.load_type == lavalink.LoadType.EMPTY or search_result.load_type == lavalink.LoadType.ERROR:
			return ["Could not find anything for that query."]
		
		if search_result.load_type == lavalink.LoadType.PLAYLIST: # check if the result is also a playlist
			self.search_results[ctx.interaction.user.id][search_result.playlist_info.name[:100]] = search_result
		# else:
		# 	# if not, create separate entry for all the tracks
		for track in search_result.tracks:
			track_str = f"[{Utils.milli_to_minutes(track.duration)}] {track.title[:50]} by {track.author[:20]} ({track.source_name})" # length of name must be between 0 to 100; slicing title and author to 50 and 20 characters respectively
			self.search_results[ctx.interaction.user.id][track_str] = track # store the track

		return [
			track_str for track_str in self.search_results[ctx.interaction.user.id]
		]


	async def play(ctx: discord.ApplicationContext, results: Union[lavalink.AudioTrack, lavalink.DeferredAudioTrack, lavalink.LoadResult]):
		"""
		Searches and plays a song from a given query.
		"""
		# Get the player for this gild from cache.
		player: lavalink.DefaultPlayer = ctx.bot.lavalink.player_manager.get(ctx.guild.id)
		# Remove leading and trailing <>. <> may be used to suppress embedding links in Discord.
		# query = f'{source}{query}'
		# print(query)

		# Check if the user input might be a URL. If it isn't, we can Lavalink do a YouTube search for it instead.
		# SoundCloud searching is possible by prefixing "scsearch:" instead.
		# if not url_rx.match(query):
		# 	query = f'ytsearch:{query}'
		
		# Get the results for the query from Lavalink.
		# results = await player.node.get_tracks(query)

		# embed = discord.Embed(color=discord.Color.blurple())
		# response_msg = ""

		# Valid load_types are:
		# 	TRACK		- direct URL to a track
		# 	PLAYLIST	- direct URL to playlist
		# 	SEARCH		- query prefixed with either "ytsearch:" or "scsearch:". This could possibly be expanded with plugins.
		# 	EMPTY		- no results for the query (result.tracks will be empty)
		# 	ERROR		- the track encountered an exception during loading
		# if results.load_type == lavalink.LoadType.EMPTY:
		# 	return await ctx.respond("I couldn't find any tracks for that query.")
		# elif results.load_type == lavalink.LoadType.PLAYLIST:
		# 	tracks = results.tracks

		if isinstance(results, lavalink.LoadResult):
			tracks = results.tracks
			# Add all of the tracks from the playlist to the queue.
			for track in tracks:
				# requester isn't necessary but it helps keep track of who queued what.
				# You can store additional metadata by passing it as a kwarg (i.e. key=value)
				player.add(track=track, requester=ctx.author.id)
			
			# embed.title = 'Playlist Enqueued!'
			# embed.description = f'{results.playlist_info.name} - {len(tracks)} tracks'
			response_msg = f"Added the playlist **`{results.playlist_info.name}`** ({len(tracks)} tracks) to the queue."

		else:
			track = results
			# embed.title = 'Track Enqueued!'
			# embed.description = f'[{track.title}]({track.uri})'
			response_msg = f"Added **`{track.title}`** to the queue."

			player.add(track=track, requester=ctx.author.id)
		
		await ctx.respond(response_msg)

		# We don't want to call .play() if the player is playing as that will effectively
		# skip the current track
		if not player.is_playing:
			await player.play()
	

	async def disconnect(ctx):
		"""
		Disconnects the player from the voice channel and clears its queue.
		"""
		player: lavalink.BasePlayer = ctx.bot.lavalink.player_manager.get(ctx.guild.id)
		# The necessary voice channel checks are handled in "create_player".
		# We don't need to duplicate code checking them again.

		# Clear the queue to ensure old tracks don't start playing
		# when someone else queues something.
		player.queue.clear()
		# Stop the current track so Lavalink consumes less resource.
		await player.stop()
		# Disconnect from the voice channel.
		await ctx.voice_client.disconnect(force=True)
		await ctx.respond('* | Disconnected.')

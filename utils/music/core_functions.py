"""
Common functionalities that are shared by two or more cog functions.
"""
import requests
import time
from typing import cast

import discord

import wavelink


class CoreFunctions():
	"""
	Core music functions.
	"""

	def milli_to_minutes(milli: int) -> str:
		"""
		Converting milliseconds to understandable output (mm:ss)

		Wavelink track lengths are given as milliseconds. So, we need to convert it.

		params:
			milli (int): milliseconds
		returns:
			(str): A string representation of the converted time
		"""
		seconds = (milli // 1000) % 60
		minutes = milli // (1000 * 60)
		return f"{minutes:02}:{seconds:02}"


	async def check_voice(ctx: discord.ApplicationContext, disconnect: bool = False) -> bool:
		"""
		Checks if the command can be executed.

		Checks if a player exists.
		Checks if the command has been issued from a valid channel.
		Checks if the user is connected to the same voice channel as the player.
		if True is passed in disconnect, checks if the channel is empty.

		params:
			ctx (discord.ApplicationContext): the context of the issued command
			disconnect (bool):
		returns:
			(bool): True if the command can be executed, False otherwise.
		"""
		
		player: wavelink.Player = cast(wavelink.Player, ctx.voice_client)

		if not player:
			await ctx.respond("The bot is not connected to a voice channel.", ephemeral=True)
			return False
		
		if player.home != ctx.channel:
			await ctx.respond(f"The player is linked to {player.home.mention}.", ephemeral=True)
			return False
		
		if ctx.author.voice is None or ctx.author.voice.channel != player.channel:
			msg = ""
			if disconnect: # check if there is no users in the voice channel that the bot is connected to
				if False in [member.bot for member in player.channel.members]:
					msg += "The channel is not empty. "
				else:
					return True
			await ctx.respond(f"{msg}Please join {player.channel.mention} to use this command.", ephemeral=True)
			return False
		
		return True


	async def play(ctx: discord.ApplicationContext, playable_item: wavelink.Playable | wavelink.Playlist):
		"""
		Join a voice channel (if not in a voice channel) and play

		params:
			ctx (discord.ApplicationContext): the context of the issued command
			playable_item (wavelink.Playable | wavelink.Playlist): the track or playlist to be played
		returns:
			void
		"""
		# First we may define our voice client,
		# for this, we are going to use typing.cast()
		# function just for the type checker know that
		# `ctx.voice_client` is going to be from type
		# `wavelink.Player`
		player: wavelink.Player = cast(wavelink.Player, ctx.voice_client)

		if not player:
			try:
				player = await ctx.author.voice.channel.connect(cls=wavelink.Player) # type: ignore
			except AttributeError:
				return await ctx.respond("Please join a voice channel first before using this command.", ephemeral=True)
			except discord.ClientException:
				return await ctx.respond("I was unable to join this voice channel. Please try again.", ephemeral=True)
			
		if not hasattr(player, "home"):
			# lock the player to this channel
			player.home = ctx.channel
		elif player.home != ctx.channel:
			# already locked somewhere else
			return await ctx.respond(f"The player is linked to {player.home.mention}.", ephemeral=True)
		elif not ctx.author.voice or ctx.author.voice.channel != player.channel:
			# the author is not connected to player's voice channel
			return await ctx.respond(f"Join {player.channel} to use this command.", ephemeral=True)

		# # `player.user_*` attributes are default attributes set by me
		# # `player.home` is also such an attribute
		# if not hasattr(player, "user_autoplaymode"):
		# 	player.user_autoplaymode = CoreFunctions.DEFAULT_AUTOPLAYMODE

		# if not hasattr(player, "user_volume"):
		# 	player.user_volume = CoreFunctions.DEFAULT_VOLUME

		# player.autoplay = player.user_autoplaymode # setting autoplay mode. if not set, it is disabled
		# disabled will not be a function of my bot, so this will tell me if the player is joining for the first time
		if player.autoplay == wavelink.AutoPlayMode.disabled:
			player.autoplay = wavelink.AutoPlayMode.partial
			await player.set_volume(30)

		if isinstance(playable_item, wavelink.Playlist):
			# playable_item is a playlist...
			for track in playable_item:
				CoreFunctions.add_track_extras(track, ctx.author.id)
			added: int = await player.queue.put_wait(playable_item)
			await ctx.respond(f"Added the playlist **`{playable_item.name}`** ({added} tracks) to the queue.")
		else:
			# tracks is not a playlist, it's a single track
			CoreFunctions.add_track_extras(playable_item, ctx.author.id)
			await player.queue.put_wait(playable_item)
			await ctx.respond(f"Added **`{playable_item} ({playable_item.source})`** to the queue.")

		if not player.playing:
			# Play now since we aren't playing anything...
			# await player.play(player.queue.get(), volume=player.user_volume)
			await player.play(player.queue.get())

	
	async def stop(ctx: discord.ApplicationContext):
		"""
		Stops playback, clears the queue.

		params:
			ctx (discord.ApplicationContext): the context of the issued command
		returns:
			(bool): True if stopped successfully, False otherwise
		"""
		if not await CoreFunctions.check_voice(ctx):
			return
		
		player: wavelink.Player = cast(wavelink.Player, ctx.voice_client)

		prev_autoplay_value = player.autoplay

		player.autoplay = wavelink.AutoPlayMode.partial # changing the autoplaymode to be able to stop playback (not sure what disable would do)

		player.queue.clear()

		if player.playing:
			await player.skip(force=True)

		player.autoplay = prev_autoplay_value

		await ctx.respond("Playback has stopped.")


	async def set_autoplay_mode(ctx: discord.ApplicationContext, mode: int):
		"""
		Sets autoplay mode

		params:
			ctx (discord.ApplicationContext): the context of the issued command
			mode (int): the autoplay mode; 0 = wavelink.AutoPlayMode.partial; 1 = wavelink.AutoPlayMode.enabled
		"""

		if not await CoreFunctions.check_voice(ctx=ctx):
			return
		
		player: wavelink.Player = cast(wavelink.Player, ctx.voice_client)
		
		if mode == 0:
			player.autoplay = wavelink.AutoPlayMode.partial
		else:
			player.autoplay = wavelink.AutoPlayMode.enabled

		await ctx.respond(f"Autoplay has been {'disabled' if mode == 0 else 'enabled'}.")


	async def set_volume(ctx: discord.ApplicationContext, value: int):
		"""
		Sets the volume.

		params:
			ctx (discord.ApplicationContext): the context of the issued command
			value (int): the value of the desired volume [0 - 100]
		"""

		if not await CoreFunctions.check_voice(ctx=ctx):
			return
		
		player: wavelink.Player = cast(wavelink.Player, ctx.voice_client)
		
		# player.user_volume = value # player.user_volume is initialized in `play`
		await player.set_volume(value)
		await ctx.respond(f"Volume set to {value}.")


	def get_player_state(player: wavelink.Player):
		if not player:
			return

		player_state = f"{'🔁' if player.queue.mode == wavelink.QueueMode.loop_all else '🔂' if player.queue.mode == wavelink.QueueMode.loop else '🚫'} Loop: {'all' if player.queue.mode == wavelink.QueueMode.loop_all else 'one' if player.queue.mode == wavelink.QueueMode.loop else 'off'}\t\t"
		player_state += f"{'🚨' if player.volume > 100 else '🔊' if player.volume > 67 else '🔉' if player.volume > 33 else '🔈' if player.volume > 0 else '🔇'} Volume: {player.volume}\t\t"
		player_state += f"{'♾️' if player.autoplay == wavelink.AutoPlayMode.enabled else '❎'} Autoplay: {'on' if player.autoplay == wavelink.AutoPlayMode.enabled else 'off' if player.autoplay == wavelink.AutoPlayMode.partial else 'play one and stop'}"

		return player_state


	def add_track_extras(track: wavelink.Playable, author_id: int, autoplay: bool = False):
		selected_info = {}
		if not autoplay:
			selected_info["requester_id"] = author_id
			selected_info["added_at"] = int(time.time())

		more_info = requests.get(f"https://lrclib.net/api/get?artist_name={track.author}&track_name={track.title}")
		if more_info.status_code == 200:
			more_info = more_info.json()
			track.album.name = more_info["albumName"]
			selected_info["artist_name"] = more_info["artistName"]
			selected_info["lyrics"] = more_info["plainLyrics"] if not more_info["instrumental"] else "[instrumental]"

		track.extras = selected_info


	def get_track_info_embed(ctx: discord.ApplicationContext, track: wavelink.Playable):

		player: wavelink.Player = cast(wavelink.Player, ctx.voice_client)

		embed = discord.Embed(
			title=track.title,
			url=track.uri,
			image=track.artwork,
		)

		embed.set_author(name=f"{ctx.author.nick if ctx.author.nick else ctx.author.display_name}", icon_url=ctx.author.avatar)

		embed.add_field(name="Artist", value=f"{track.extras.artist_name if 'artist_name' in dict(track.extras) else track.author}", inline=True)
		embed.add_field(name="Duration", value=CoreFunctions.milli_to_minutes(track.length), inline=True)

		if player:
			embed.set_footer(text=CoreFunctions.get_player_state(player))
			if player.playing and player.current == track:
				embed.add_field(name="Position", value=CoreFunctions.milli_to_minutes(player.position), inline=True)
				embed.add_field(name="Played", value=f"<t:{track.extras.played_at}:R>", inline=True)

		if not track.recommended:
			embed.add_field(name="Added", value=f"<t:{track.extras.added_at}:f>", inline=True)
			embed.add_field(name="Requested by", value=f"<@{track.extras.requester_id}>", inline=True)
		
		if track.album.name:
			if track.album.url:
				album = f"[{track.album.name}]({track.album.url})"
			else:
				album = track.album.name
			embed.add_field(name="Album", value=album, inline=True)
		
		if track.playlist:
			if track.playlist.url:
				pvalue = f"[{track.playlist.name}]({track.playlist.url})"
			else:
				pvalue = track.playlist.name
			embed.add_field(name="Playlist", value=pvalue, inline=True)

		embed.add_field(name="AutoRec", value=str(track.recommended), inline=True)
		embed.add_field(name="Source", value=track.source, inline=True)

		return embed

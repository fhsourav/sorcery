"""
Common functionalities that are shared by two or more cog functions.
"""
import time
from typing import cast

import discord

import wavelink


class CoreFunctions():
	"""
	CoreFunctions

	This class contains core music-related functions for a Discord bot using Wavelink. 
	It provides utilities for managing playback, interacting with voice channels, 
	and handling tracks and playlists.
	"""

	def milli_to_minutes(milli: int) -> str:
		"""
		Converts a duration from milliseconds to a formatted string in the format mm:ss.

		This function is useful for converting track lengths or other time durations 
		provided in milliseconds into a more human-readable format.

		(Wavelink track lengths are given in milliseconds.)

		Params:
			milli (int): The duration in milliseconds.

		Returns:
			str: The formatted time string in the format mm:ss, where mm represents 
				 minutes and ss represents seconds, both zero-padded to two digits.
		"""
		seconds = (milli // 1000) % 60
		minutes = milli // (1000 * 60)
		return f"{minutes:02}:{seconds:02}"


	async def check_voice(ctx: discord.ApplicationContext, disconnect: bool = False) -> bool:
		"""
		Checks if the command can be executed in the current context.

		This function performs several checks to ensure the command can be executed:
		1. Verifies if a player exists and is connected to a voice channel.
		2. Ensures the command is issued from the channel linked to the player.
		3. Confirms the user is connected to the same voice channel as the player.
		4. If `disconnect` is True, checks if the voice channel is empty.

		Params:
			ctx (discord.ApplicationContext): The context of the issued command.
			disconnect (bool, optional): If True, checks if the voice channel is empty. Defaults to False.

		Returns:
			bool: True if the command can be executed, False otherwise.
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
		Plays a track or playlist in a voice channel.

		This function ensures the bot is connected to a voice channel, locks the player to the current text channel, 
		and adds the provided track or playlist to the queue. If the player is not already playing, it starts playback.

		Params:
			ctx (discord.ApplicationContext): The context of the issued command.
			playable_item (wavelink.Playable | wavelink.Playlist): The track or playlist to be played.

		Returns:
			void: This function does not return a value.

		Behavior:
			- If the bot is not connected to a voice channel, it attempts to connect to the author's current voice channel.
			- Ensures the player is locked to the current text channel and prevents usage from other channels.
			- Adds the provided track or playlist to the queue.
			- If the player is idle, starts playback with the first item in the queue.
			- Sets default autoplay mode and volume if the player is joining for the first time.
			- Responds with appropriate messages for various scenarios, such as the user not being in a voice channel or the bot being unable to join.

		Raises:
			AttributeError: If the author is not in a voice channel.
			discord.ClientException: If the bot fails to join the voice channel.
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
		Stops playback and clears the queue.

		This function halts the current playback in the voice channel, clears the 
		entire queue of tracks, and temporarily adjusts the autoplay mode to ensure 
		playback is stopped. It then restores the previous autoplay mode after 
		stopping.

		Params:
			ctx (discord.ApplicationContext): The context of the issued command.

		Returns:
			bool: True if playback was stopped successfully, False otherwise.
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
		Sets the autoplay mode for the music player.

		Params:
			ctx (discord.ApplicationContext): The context of the issued command.
			mode (int): The autoplay mode to set. 
						Use 0 for `wavelink.AutoPlayMode.partial` (autoplay disabled) 
						or 1 for `wavelink.AutoPlayMode.enabled` (autoplay enabled).

		Returns:
			None: Sends a response message indicating whether autoplay has been enabled or disabled.

		Notes:
			This function checks if the user is in a valid voice channel before proceeding.
			It modifies the `autoplay` attribute of the `wavelink.Player` instance associated with the voice client.
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
		Sets the volume for the music player.

		This function adjusts the playback volume of the music player associated with the 
		current voice client in the Discord context. It ensures that the user is connected 
		to a voice channel and that the bot is properly configured before setting the volume.

		Params:
			ctx (discord.ApplicationContext): The context of the issued command.
			value (int): The desired volume level, ranging from 0 (mute) to 100 (maximum volume).

		Returns:
			None: This function sends a response to the user indicating the new volume level.
		"""

		if not await CoreFunctions.check_voice(ctx=ctx):
			return
		
		player: wavelink.Player = cast(wavelink.Player, ctx.voice_client)
		
		# player.user_volume = value # player.user_volume is initialized in `play`
		await player.set_volume(value)
		await ctx.respond(f"Volume set to {value}.")


	def get_player_state(player: wavelink.Player):
		"""
		Retrieve the current state of the music player, including loop mode, volume, and autoplay status.

		Params:
			player (wavelink.Player): The music player instance to retrieve the state from.

		Returns:
			str: A formatted string representing the player's state, including:
				- Loop mode (🔁 for loop all, 🔂 for loop one, 🚫 for no loop)
				- Volume level (🔇 for muted, 🔈 for low, 🔉 for medium, 🔊 for high, 🚨 for above 100%)
				- Autoplay status (♾️ for enabled, ❎ for disabled, or "play one and stop" for partial mode)
			None: If the player instance is not provided.
		"""
		if not player:
			return

		player_state = f"{'🔁' if player.queue.mode == wavelink.QueueMode.loop_all else '🔂' if player.queue.mode == wavelink.QueueMode.loop else '🚫'} Loop: {'all' if player.queue.mode == wavelink.QueueMode.loop_all else 'one' if player.queue.mode == wavelink.QueueMode.loop else 'off'}\t\t"
		player_state += f"{'🚨' if player.volume > 100 else '🔊' if player.volume > 67 else '🔉' if player.volume > 33 else '🔈' if player.volume > 0 else '🔇'} Volume: {player.volume}\t\t"
		player_state += f"{'♾️' if player.autoplay == wavelink.AutoPlayMode.enabled else '❎'} Autoplay: {'on' if player.autoplay == wavelink.AutoPlayMode.enabled else 'off' if player.autoplay == wavelink.AutoPlayMode.partial else 'play one and stop'}"

		return player_state


	def add_track_extras(track: wavelink.Playable, author_id: int):
		"""
		Adds additional metadata to a track object.

		This function attaches extra information to a track object, including
		the ID of the user who requested the track and the timestamp when the
		track was added.

		Params:
			track (wavelink.Playable): The track object to which extras will be added.
			author_id (int): The ID of the user who requested the track.

		Returns:
			None
		"""
		track.extras = {"requester_id": author_id, "added_at": int(time.time())}


	def get_track_info_embed(ctx: discord.ApplicationContext, track: wavelink.Playable):
		"""
		Generates a Discord embed containing detailed information about a track.

		Params:
			ctx (discord.ApplicationContext): The context of the Discord command.
			track (wavelink.Playable): The track object containing metadata about the track.

		Returns:
			discord.Embed: A Discord embed object populated with track information.
		"""

		player: wavelink.Player = cast(wavelink.Player, ctx.voice_client)

		embed = discord.Embed(
			title=track.title,
			url=track.uri,
			image=track.artwork,
		)

		embed.set_author(name=f"{ctx.author.nick if ctx.author.nick else ctx.author.display_name}", icon_url=ctx.author.avatar)

		embed.add_field(name="Artist", value=f"{track.extras.artistName if 'artistName' in dict(track.extras) else track.author}", inline=True)
		embed.add_field(name="Duration", value=CoreFunctions.milli_to_minutes(track.length), inline=True)

		if player:
			embed.set_footer(text=CoreFunctions.get_player_state(player))
			if player.playing and player.current == track:
				embed.add_field(name="Position", value=CoreFunctions.milli_to_minutes(player.position), inline=True)

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

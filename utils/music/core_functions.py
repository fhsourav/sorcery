"""
Common functionalities that are shared by two or more cog functions.
"""


from typing import cast

import discord

import wavelink


class CoreFunctions():
	"""
	Core music functions.
	"""

	DEFAULT_AUTOPLAYMODE = wavelink.AutoPlayMode.partial
	DEFAULT_VOLUME = 30


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

		# `player.user_*` attributes are default attributes set by me
		# `player.home` is also such an attribute
		if not hasattr(player, "user_autoplaymode"):
			player.user_autoplaymode = CoreFunctions.DEFAULT_AUTOPLAYMODE

		if not hasattr(player, "user_volume"):
			player.user_volume = CoreFunctions.DEFAULT_VOLUME

		player.autoplay = player.user_autoplaymode # setting autoplay mode. if not set, it is disabled

		if isinstance(playable_item, wavelink.Playlist):
			# playable_item is a playlist...
			added: int = await player.queue.put_wait(playable_item)
			await ctx.respond(f"Added the playlist **`{playable_item.name}`** ({added} songs) to the queue.")
		else:
			# tracks is not a playlist, it's a single track
			await player.queue.put_wait(playable_item)
			await ctx.respond(f"Added **`{playable_item} ({playable_item.source})`** to the queue.")

		if not player.playing:
			# Play now since we aren't playing anything...
			await player.play(player.queue.get(), volume=player.user_volume)

	
	async def stop(ctx: discord.ApplicationContext):
		"""
		Stops playback, clears the queue.

		params:
			ctx: (discord.ApplicationContext): the context of the issued command
		"""
		if not await CoreFunctions.check_voice(ctx):
			return
		
		player: wavelink.Player = cast(wavelink.Player, ctx.voice_client)

		player.autoplay = wavelink.AutoPlayMode.partial # changing the autoplaymode to be able to stop playback (not sure what disable would do)

		player.queue.clear()

		if player.playing:
			await player.skip(force=True)

		player.autoplay = player.user_autoplaymode

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
			player.user_autoplaymode = wavelink.AutoPlayMode.partial # player.user_autoplaymode is initialized in `play`
		else:
			player.user_autoplaymode = wavelink.AutoPlayMode.enabled

		player.autoplay = player.user_autoplaymode

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
		
		player.user_volume = value # player.user_volume is initialized in `play`
		await player.set_volume(player.user_volume)
		await ctx.respond(f"Volume set to {value}.")

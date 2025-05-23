from typing import cast

import discord

import wavelink

from utils.music import CoreFunctions, QueueFunctions


class MusicQueue(discord.Cog):
	"""
	A discord cog that provides various commands to manage wavelink player queue.	
	"""

	def __init__(self, bot: discord.Bot):
		self.bot = bot

	
	@discord.slash_command(name="queue")
	async def queue(self, ctx: discord.ApplicationContext):
		"""
		Display the current queue.

		This command retrieves and displays the current queue for the voice channel
		the user is connected to. It checks if the user is in a valid voice channel, retrieves
		the queue from the voice client's player, and uses a paginator to display the queue
		interactively.

		Params:
			ctx (discord.ApplicationContext): The context of the issued command.

		Returns:
			None
		"""
		if not await CoreFunctions.check_voice(ctx):
			return
		
		player: wavelink.Player = cast(wavelink.Player, ctx.voice_client)

		queue: wavelink.Queue = player.queue

		paginator = QueueFunctions.get_queue_paginator(ctx, queue, 0)

		await paginator.respond(ctx.interaction)

	
	@discord.slash_command(name="history")
	async def history(self, ctx: discord.ApplicationContext):
		"""
		Display the queue history.

		This command retrieves and displays the history of tracks that have been played
		in the current voice channel session. It uses a paginator to handle the display
		of the history in a user-friendly format.

		Params:
			ctx (discord.ApplicationContext): The context of the issued command.

		Returns:
			None
		"""
		if not await CoreFunctions.check_voice(ctx):
			return
		
		player: wavelink.Player = cast(wavelink.Player, ctx.voice_client)

		paginator = QueueFunctions.get_queue_paginator(ctx, player.queue.history, 1)

		await paginator.respond(ctx.interaction)

	
	@discord.slash_command(name="loop")
	@discord.option(
		name="mode",
		description="Choose a mode.",
		choices=[
			discord.OptionChoice(name="off", value=0),
			discord.OptionChoice(name="current track", value=1),
			discord.OptionChoice(name="all", value=2),
		]
	)
	async def loop(self, ctx: discord.ApplicationContext, mode: int):
		"""
		Adjust the loop mode.

		Params:
			ctx (discord.ApplicationContext): The context of the issued command.
			mode (int): The loop mode to set.
						0 - Disable looping.
						1 - Loop the current track.
						2 - Loop all tracks in the queue.

		Returns:
			None
		"""
		if not await CoreFunctions.check_voice(ctx):
			return
		
		player: wavelink.Player = cast(wavelink.Player, ctx.voice_client)
		
		if mode == 0:
			player.queue.mode = wavelink.QueueMode.normal
			return await ctx.respond("Player loop is set to `off`.")
		if mode == 1:
			player.queue.mode = wavelink.QueueMode.loop
			return await ctx.respond("Player loop is set to `current track`.")
		if mode == 2:
			player.queue.mode = wavelink.QueueMode.loop_all
			return await ctx.respond("Player loop is set to `all`.")
	

	autoplay = discord.SlashCommandGroup(name="autoplay")


	@autoplay.command(name="mode")
	@discord.option(
		name="mode",
		description="If autoplay is enabled, player will play recommended tracks.",
		choices=[
			discord.OptionChoice(
				name="Enable",
				value="1"
			),
			discord.OptionChoice(
				name="Disable",
				value="0"
			)
		]
	)
	async def set_autoplay(self, ctx: discord.ApplicationContext, mode: int):
		"""
		Set the autoplay mode.

		Params:
			ctx (discord.ApplicationContext): The context of the issued command.
			mode (int): The autoplay mode to set. This could represent different modes
						(e.g., 0 for off, 1 for on, etc.).

		Returns:
			None
		"""
		await CoreFunctions.set_autoplay_mode(ctx, mode)


	@autoplay.command(name="queue")
	async def autoqueue(self, ctx: discord.ApplicationContext):
		"""
		Display the autoplay queue.

		This command retrieves the autoplay queue associated with the current voice client.
		The queue is displayed using a paginator for better readability.
		
		Params:
			ctx (discord.ApplicationContext): The context of the issued command.
		
		Returns:
			None
		"""
		if not await CoreFunctions.check_voice(ctx):
			return
		
		player: wavelink.Player = cast(wavelink.Player, ctx.voice_client)

		paginator = QueueFunctions.get_queue_paginator(ctx, player.auto_queue, 2)

		await paginator.respond(ctx.interaction)
	

	@autoplay.command(name="history")
	async def autohistory(self, ctx: discord.ApplicationContext):
		"""
		Display the autoplay queue history.

		This command retrieves and displays the history of tracks that have been 
		played in the autoplay queue. It uses a paginator to format the history 
		into pages for easier navigation.

		Params:
			ctx (discord.ApplicationContext): The context of the issued command.

		Returns:
			None
		"""
		if not await CoreFunctions.check_voice(ctx):
			return
		
		player: wavelink.Player = cast(wavelink.Player, ctx.voice_client)

		paginator = QueueFunctions.get_queue_paginator(ctx, player.auto_queue.history, 3)

		await paginator.respond(ctx.interaction)


	@discord.slash_command(name="replay")
	@discord.option(
		name="index",
		description="Index of the song from queue/autoplay history",
		min_value=1,
	)
	@discord.option(
		name="autoplay",
		description="If replaying from the autoplay history.",
	)
	async def replay(self, ctx: discord.ApplicationContext, index: int, autoplay: bool = False):
		"""
		Replay a song from the playback history or autoplay history.

		This method allows the user to replay a specific song from the history
		of previously played tracks or the autoplay history. It skips the 
		currently playing song and starts playing the selected track.

		Params:
			ctx (discord.ApplicationContext): The context of the issued command.
			index (int): The 1-based index of the song in the history to replay.
			autoplay (bool, optional): Whether to replay from the autoplay history. Defaults to False.

		Returns:
			None
		"""
		if not await CoreFunctions.check_voice(ctx):
			return
		
		player: wavelink.Player = cast(wavelink.Player, ctx.voice_client)

		if autoplay:
			history = player.auto_queue.history
		else:
			history = player.queue.history

		if not history:
			return await ctx.respond(f"{'Autoplay history' if autoplay else 'History'} is empty!", ephemeral=True)
		
		history_reversed = list(reversed(history)) # reversed gives us a list_reverseiterator object which is not subscriptable. so we are typecasting it to a list.

		track = history_reversed[index - 1]

		player.queue.put_at(0, track)

		if not player.playing:
			await player.play(player.queue.get())
		else:
			await player.skip(force=True)
		
		await ctx.respond(f"Replaying `{track.title}`.")
	

	@discord.slash_command(name="swap")
	@discord.option(
		name="index1",
		description="Index of the first track.",
		min_index=1,
	)
	@discord.option(
		name="index2",
		description="Index of the second track.",
		min_index=1,
	)
	async def swap(self, ctx: discord.ApplicationContext, index1: int, index2: int):
		"""
		Swap two tracks in the music queue by their indices.

		Params:
			ctx (discord.ApplicationContext): The context of the issued command.
			index1 (int): The 1-based index of the first track to swap.
			index2 (int): The 1-based index of the second track to swap.

		Returns:
			None
		"""
		if not await CoreFunctions.check_voice(ctx):
			return
		
		player: wavelink.Player = cast(wavelink.Player, ctx.voice_client)

		track_count = len(player.queue)
		if index1 > track_count or index2 > track_count:
			return await ctx.respond("She never told you a number this big. You know what I'm talking about.", ephemeral=True)
		
		if index1 == index2:
			return await ctx.respond("Trying to swap a track with itself now, are we?", ephemeral=True)
		
		first = index1 - 1
		second = index2 - 1

		track1 = player.queue.peek(first)
		track2 = player.queue.peek(second)

		player.queue.swap(first, second)

		await ctx.respond(f"Swapped `{track1.title}` and `{track2.title}`!")
	

	@discord.slash_command(name="shuffle")
	async def shuffle(self, ctx: discord.ApplicationContext):
		"""
		Shuffle the queue.

		This command shuffles the order of tracks in the player's queue.

		Params:
			ctx (discord.ApplicationContext): The context of the command invocation.

		Returns:
			None
		"""
		if not await CoreFunctions.check_voice(ctx):
			return
		
		player: wavelink.Player = cast(wavelink.Player, ctx.voice_client)

		player.queue.shuffle()

		await ctx.respond("Player queue has now been shuffled!")


	@discord.slash_command(name="skipto")
	@discord.option(
		name="index",
		description="Index of the track in the queue.",
		min_value=1,
	)
	async def skipto(self, ctx: discord.ApplicationContext, index: int):
		"""
		Skip to the track at the specified index. Autoplay queue is used if queue is empty.

		Params:
			ctx (discord.ApplicationContext): The context of the issued command.
			index (int): The 1-based index of the track to skip to in the queue.
		"""
		if not await CoreFunctions.check_voice(ctx):
			return
		
		player: wavelink.Player = cast(wavelink.Player, ctx.voice_client)

		queue = player.queue

		if not queue:

			if player.autoplay == wavelink.AutoPlayMode.enabled:
				if not player.auto_queue:
					return await ctx.respond("Both queue and autoplay queue are empty.")
				queue = player.auto_queue
			else:
				return await ctx.respond("The queue is empty.")
		
		if index > len(queue):
			return await ctx.respond("Invalid index.", ephemeral=True)
		
		for i in range(index - 1):
			queue.delete(0)
		
		track: wavelink.Playable = queue.peek(0)
		
		loopmode = player.queue.mode
		player.queue.mode = wavelink.QueueMode.normal

		await player.skip(force=True)

		player.queue.mode = loopmode

		await ctx.respond(f"Skipped to `{track.title}`.")
	

	@discord.slash_command(name="delete")
	@discord.option(
		name="index",
		description="Index of the track in the queue.",
		min_value=1,
	)
	async def delete(self, ctx: discord.ApplicationContext, index: int):
		"""
		Delete a track from the queue by its index.

		Params:
			ctx (discord.ApplicationContext): The context of the issued command.
			index (int): The 1-based index of the track to delete from the queue.

		Returns:
			None
		"""
		if not await CoreFunctions.check_voice(ctx):
			return
		
		player: wavelink.Player = cast(wavelink.Player, ctx.voice_client)

		if index > len(player.queue):
			return await ctx.respond("Invalid index!", ephemeral=True)
		
		track = player.queue.peek(index - 1)
		player.queue.delete(index - 1)

		await ctx.respond(f"Deleted `{track.title}` from the queue.")


	clear = discord.SlashCommandGroup(name="clear", description="Clear queue commands.")
	

	@clear.command(name="queue")
	async def clear_queue(self, ctx: discord.ApplicationContext):
		"""
		Clear the queue.

		Params:
			ctx (discord.ApplicationContext): The context of the issued command.
		
		Returns:
			None
		"""
		if not await CoreFunctions.check_voice(ctx):
			return
		
		player: wavelink.Player = cast(wavelink.Player, ctx.voice_client)

		player.queue.clear()

		await ctx.respond("The queue has been cleared.")
	

	@clear.command(name="history")
	async def clear_history(self, ctx: discord.ApplicationContext):
		"""
		Clear the queue history.

		This command removes all previously played tracks from the queue's history.

		Params:
			ctx (discord.ApplicationContext): The context of the issued command.

		Returns:
			None
		"""
		if not await CoreFunctions.check_voice(ctx):
			return
		
		player: wavelink.Player = cast(wavelink.Player, ctx.voice_client)

		player.queue.history.clear()

		await ctx.respond("The queue history has been cleared.")


	clear_autoplay = clear.create_subgroup(name="autoplay", description="Clear autoplay commands.")


	@clear_autoplay.command(name="queue")
	async def clear_autoqueue(self, ctx: discord.ApplicationContext):
		"""
		Clear the autoplay queue.

		This command clears the autoplay queue associated with the Wavelink player.

		Params:
			ctx (discord.ApplicationContext): The context of the issued command.

		Returns:
			None
		"""
		if not await CoreFunctions.check_voice(ctx):
			return
		
		player: wavelink.Player = cast(wavelink.Player, ctx.voice_client)

		player.auto_queue.clear()

		await ctx.respond("The autoplay queue has been cleared.")
	

	@clear_autoplay.command(name="history")
	async def clear_autoqueue_history(self, ctx: discord.ApplicationContext):
		"""
		Clear the autoplay queue history.

		This command clears the history of the autoplay queue associated with the current Wavelink player.

		Params:
			ctx (discord.ApplicationContext): The context of the issued command.

		Returns:
			None
		"""
		if not await CoreFunctions.check_voice(ctx):
			return
		
		player: wavelink.Player = cast(wavelink.Player, ctx.voice_client)

		player.auto_queue.history.clear()

		await ctx.respond("The autoplay queue history has been cleared.")


	reset = discord.SlashCommandGroup(name="reset", description="Reset queue history.")


	@reset.command(name="queue")
	async def reset_queue(self, ctx: discord.ApplicationContext):
		"""
		Reset the queue.

		This command clears the current music queue associated with the voice client
		in the context.

		Params:
			ctx (discord.ApplicationContext): The context of the issued command.
		
		Returns:
			None
		"""
		if not await CoreFunctions.check_voice(ctx):
			return
		
		player: wavelink.Player = cast(wavelink.Player, ctx.voice_client)

		player.queue.reset()

		await ctx.respond("The queue has been reset.")


	@reset.command(name="autoplay")
	async def reset_autoplay(self, ctx: discord.ApplicationContext):
		"""
		Reset the autoplay queue.

		This command resets the autoplay queue associated with the current Wavelink player instance.

		Params:
			ctx (discord.ApplicationContext): The context of the issued command.

		Returns:
			None
		"""
		if not await CoreFunctions.check_voice(ctx):
			return
		
		player: wavelink.Player = cast(wavelink.Player, ctx.voice_client)

		player.auto_queue.reset()

		await ctx.respond("The autoplay queue has been reset.")


def setup(bot: discord.Bot):
	bot.add_cog(MusicQueue(bot))

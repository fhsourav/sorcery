from typing import cast

import discord

import wavelink

from utils.music import CoreFunctions, QueueFunctions

class MusicQueue(discord.Cog):
	"""This cog contains the queue features."""

	def __init__(self, bot: discord.Bot):
		self.bot = bot

	
	@discord.slash_command(name="queue")
	async def queue(self, ctx: discord.ApplicationContext):
		"""Display the current queue."""
		if not await CoreFunctions.check_voice(ctx):
			return
		
		player: wavelink.Player = cast(wavelink.Player, ctx.voice_client)

		queue: wavelink.Queue = player.queue

		paginator = QueueFunctions.get_queue_paginator(ctx, queue, 0)

		await paginator.respond(ctx.interaction)

	
	@discord.slash_command(name="history")
	async def history(self, ctx: discord.ApplicationContext):
		"""Display the queue history."""
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
		"""Select the loop mode."""
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
		"""Choose Autoplay Mode."""
		await CoreFunctions.set_autoplay_mode(ctx, mode)


	@autoplay.command(name="queue")
	async def autoqueue(self, ctx: discord.ApplicationContext):
		"""Display the autoplay queue."""
		if not await CoreFunctions.check_voice(ctx):
			return
		
		player: wavelink.Player = cast(wavelink.Player, ctx.voice_client)

		paginator = QueueFunctions.get_queue_paginator(ctx, player.auto_queue, 2)

		await paginator.respond(ctx.interaction)
	

	@autoplay.command(name="history")
	async def autohistory(self, ctx: discord.ApplicationContext):
		"""Display the autoplay queue history."""
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
		description="If the track exists in the autoplay history",
	)
	async def replay(self, ctx: discord.ApplicationContext, index: int, autoplay: bool = False):
		"""Replay a song from history/autoplay history. Skips the current song."""
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

		history.remove(track)

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
		"""Swap two tracks in the queue by index."""
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
		"""Shuffle the queue."""
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
		"""Skip to another track in the queue. Use autoplay queue if queue is empty."""
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
		"""Delete a track from the queue by index."""
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
		"""Clear the queue."""
		if not await CoreFunctions.check_voice(ctx):
			return
		
		player: wavelink.Player = cast(wavelink.Player, ctx.voice_client)

		player.queue.clear()

		await ctx.respond("The queue has been cleared.")
	

	@clear.command(name="history")
	async def clear_history(self, ctx: discord.ApplicationContext):
		"""Clear queue history."""
		if not await CoreFunctions.check_voice(ctx):
			return
		
		player: wavelink.Player = cast(wavelink.Player, ctx.voice_client)

		player.queue.history.clear()

		await ctx.respond("The queue history has been cleared.")


	clear_autoplay = clear.create_subgroup(name="autoplay", description="Clear autoplay commands.")


	@clear_autoplay.command(name="queue")
	async def clear_autoqueue(self, ctx: discord.ApplicationContext):
		"""Clear autoplay queue."""
		if not await CoreFunctions.check_voice(ctx):
			return
		
		player: wavelink.Player = cast(wavelink.Player, ctx.voice_client)

		player.auto_queue.clear()

		await ctx.respond("The autoplay queue has been cleared.")
	

	@clear_autoplay.command(name="history")
	async def clear_autoqueue_history(self, ctx: discord.ApplicationContext):
		"""Clear autoplay queue history."""
		if not await CoreFunctions.check_voice(ctx):
			return
		
		player: wavelink.Player = cast(wavelink.Player, ctx.voice_client)

		player.auto_queue.history.clear()

		await ctx.respond("The autoplay queue history has been cleared.")


	reset = discord.SlashCommandGroup(name="reset", description="Reset queue history.")

	@reset.command(name="queue")
	async def reset_queue(self, ctx: discord.ApplicationContext):
		"""Reset the queue."""
		if not await CoreFunctions.check_voice(ctx):
			return
		
		player: wavelink.Player = cast(wavelink.Player, ctx.voice_client)

		player.queue.reset()

		await ctx.respond("The queue has been reset.")


	@reset.command(name="autoplay")
	async def reset_autoplay(self, ctx: discord.ApplicationContext):
		"""Reset the autoplay queue."""
		if not await CoreFunctions.check_voice(ctx):
			return
		
		player: wavelink.Player = cast(wavelink.Player, ctx.voice_client)

		player.auto_queue.reset()

		await ctx.respond("The autoplay queue has been reset.")


def setup(bot: discord.Bot):
	bot.add_cog(MusicQueue(bot))

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

		history: wavelink.Queue = player.queue.history

		paginator = QueueFunctions.get_queue_paginator(ctx, history, 1)

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


def setup(bot: discord.Bot):
	bot.add_cog(MusicQueue(bot))

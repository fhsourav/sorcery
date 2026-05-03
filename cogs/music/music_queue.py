import discord

from discord.ext import commands

from services.music.music_core_service import MusicCoreService
from services.music.music_queue_service import MusicQueueService


class MusicQueue(discord.Cog):

	def __init__(self, bot: discord.Bot):
		self.bot = bot
		self.search_results = {}
	

	@discord.slash_command(name="queue")
	@commands.check(MusicCoreService.create_player)
	async def queue(self, ctx: discord.ApplicationContext):
		"""
		Display the queue.

		Docstring for queue
		
		:param self: Description
		:param ctx: Description
		:type ctx: discord.ApplicationContext
		"""
		await MusicQueueService.get_queue_paginator(ctx, 0)
	

	@discord.slash_command(name="history")
	@commands.check(MusicCoreService.create_player)
	async def history(self, ctx: discord.ApplicationContext):
		"""
		Display queue history.
		
		Docstring for history
		
		:param self: Description
		:param ctx: Description
		:type ctx: discord.ApplicationContext
		"""
		await MusicQueueService.get_queue_paginator(ctx, 1)
	

	@discord.slash_command(name="delete")
	@discord.option(
		name="track",
		description="Choose from queue.",
		autocomplete=MusicQueueService.queue_autocomplete
	)
	@commands.check(MusicCoreService.create_player)
	async def delete(self, ctx: discord.ApplicationContext, track: int):
		"""
		Delete a track from the queue.
		"""
		await MusicQueueService.delete(ctx, track)
	

	@discord.slash_command(name="loop")
	@discord.option(
		name="mode",
		description="Choose a mode.",
		choices=[
			discord.OptionChoice(name="off", value=0),
			discord.OptionChoice(name="current track", value=1),
			discord.OptionChoice(name="all (loops through the current queue, previous tracks are ignored)", value=2)
		]
	)
	@commands.check(MusicCoreService.create_player)
	async def loop(self, ctx: discord.ApplicationContext, mode: int):
		"""
		Adjust the loop mode.
		"""
		await MusicQueueService.set_loop(ctx, mode)
	

	@discord.slash_command(name="shuffle")
	@discord.option(
		name="set",
		description="Set shuffle mode.",
		choices=[
			True,
			False
		]
	)
	@commands.check(MusicCoreService.create_player)
	async def shuffle(self, ctx: discord.ApplicationContext, set: bool):
		"""
		Shuffle the queue.
		"""
		await MusicQueueService.shuffle(ctx, set)
	

	@discord.slash_command(name="skipto")
	@discord.option(
		name="track",
		description="Choose from queue.",
		autocomplete=MusicQueueService.queue_autocomplete
	)
	@commands.check(MusicCoreService.create_player)
	async def skipto(self, ctx: discord.ApplicationContext, track: int):
		"""
		Skip to another song from the queue. Tracks in between are discarded.
		"""
		await MusicQueueService.skipto(ctx, track)
	

	reset = discord.SlashCommandGroup(name="reset")

	@reset.command(name="queue")
	@commands.check(MusicCoreService.create_player)
	async def reset_queue(self, ctx: discord.ApplicationContext):
		"""
		Reset the queue.
		"""
		await MusicQueueService.clear_queue(ctx)
	

	@reset.command(name="history")
	@commands.check(MusicCoreService.create_player)
	async def reset_history(self, ctx: discord.ApplicationContext):
		"""
		Reset the history.
		"""
		await MusicQueueService.clear_history(ctx)
		


def setup(bot: discord.Bot):
	bot.add_cog(MusicQueue(bot))

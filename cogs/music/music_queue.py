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
		Docstring for queue
		
		:param self: Description
		:param ctx: Description
		:type ctx: discord.ApplicationContext
		"""
		await MusicQueueService.display_queue(ctx)
	

	@discord.slash_command(name="history")
	@commands.check(MusicCoreService.create_player)
	async def history(self, ctx: discord.ApplicationContext):
		"""
		Docstring for history
		
		:param self: Description
		:param ctx: Description
		:type ctx: discord.ApplicationContext
		"""
		await MusicQueueService.display_history(ctx)
		


def setup(bot: discord.Bot):
	bot.add_cog(MusicQueue(bot))

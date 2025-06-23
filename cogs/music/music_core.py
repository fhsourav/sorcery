import discord

from discord.ext import commands

from services.music.music_core_service import MusicCoreService


class MusicCore(discord.Cog):

	def __init__(self, bot: discord.Bot):
		self.bot = bot
		self.search_results = {}


	@discord.slash_command(name="play")
	@discord.option(
		name="source",
		description="Where to search",
		choices=[
			discord.OptionChoice(name="YouTube Music", value="ytmsearch:"),
			discord.OptionChoice(name="YouTube", value="ytsearch:"),
			discord.OptionChoice(name="SoundCloud", value="scsearch:"),
			discord.OptionChoice(name="Any link", value="")
		]
	)
	@discord.option(
		name="query",
		description="The search query or link of the track/playlist.",
		autocomplete=MusicCoreService.autocomplete_query
	)
	@discord.option(
		name="isplaylist",
		description="If the query is for a playlist.",
		choices=[
			True,
			False
		]
	)
	@commands.check(MusicCoreService.create_player)
	async def play(self, ctx: discord.ApplicationContext, source: str, playlist: bool, query: str):
		await MusicCoreService.play(ctx, source, playlist, query)
	

	@discord.slash_command(name="disconnect")
	@commands.check(MusicCoreService.create_player)
	async def disconnect(self, ctx: discord.ApplicationContext):
		await MusicCoreService.disconnect(ctx)


def setup(bot: discord.Bot):
	bot.add_cog(MusicCore(bot))

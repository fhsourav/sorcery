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
			discord.OptionChoice(name="Link (playlist or any)", value="")
		]
	)
	@discord.option(
		name="query",
		description="The search query or link of the track/playlist.",
		autocomplete=MusicCoreService.autocomplete_query
	)
	@commands.check(MusicCoreService.create_player)
	async def play(self, ctx: discord.ApplicationContext, source: str, query: str):
		if query in self.search_results[ctx.author.id]:
			await MusicCoreService.play(ctx, self.search_results[ctx.author.id][query])
		else:
			await ctx.respond("Interaction failed.", ephemeral=True)
			await MusicCoreService.disconnect(ctx)
	

	@discord.slash_command(name="disconnect")
	@commands.check(MusicCoreService.create_player)
	async def disconnect(self, ctx: discord.ApplicationContext):
		await MusicCoreService.disconnect(ctx)
	

	@discord.slash_command(name="autoplay")
	@discord.option(
		name="set",
		description="Set autoplay mode",
		choices=[
			True,
			False
		],
		required=True
	)
	@commands.check(MusicCoreService.create_player)
	async def autoplay(self, ctx: discord.ApplicationContext, set: bool):
		await MusicCoreService.autoplay(ctx, set)
	

	@discord.slash_command(name="nowplaying")
	@commands.check(MusicCoreService.create_player)
	async def nowplaying(self, ctx: discord.ApplicationContext):
		await MusicCoreService.nowplaying(ctx)
	

	@discord.slash_command(name="pausetoggle")
	@commands.check(MusicCoreService.create_player)
	async def pausetoggle(self, ctx: discord.ApplicationContext):
		await MusicCoreService.pausetoggle(ctx)


def setup(bot: discord.Bot):
	bot.add_cog(MusicCore(bot))

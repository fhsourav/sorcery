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
		"""
		Play a track with the given query.
		"""
		if query in self.search_results[ctx.author.id]:
			await MusicCoreService.play(ctx, self.search_results[ctx.author.id][query])
		else:
			await ctx.respond("Interaction failed.", ephemeral=True)
	

	@discord.slash_command(name="stop") # previously disconnect
	@commands.check(MusicCoreService.create_player)
	async def stop(self, ctx: discord.ApplicationContext):
		"""
		Stop the player and disconnect.
		"""
		await MusicCoreService.disconnect(ctx, self.search_results)
	

	@discord.slash_command(name="autoplay")
	@discord.option(
		name="mode",
		description="If set to True, player will keep playing recommended tracks.",
		choices=[
			True,
			False
		],
		required=True
	)
	@commands.check(MusicCoreService.create_player)
	async def autoplay(self, ctx: discord.ApplicationContext, set: bool):
		"""
		Set the autoplay mode.
		"""
		await MusicCoreService.autoplay(ctx, set)
	

	@discord.slash_command(name="nowplaying")
	@commands.check(MusicCoreService.create_player)
	async def nowplaying(self, ctx: discord.ApplicationContext):
		"""
		Display information about the current track.
		"""
		await MusicCoreService.nowplaying(ctx)
	

	@discord.slash_command(name="pausetoggle")
	@commands.check(MusicCoreService.create_player)
	async def pausetoggle(self, ctx: discord.ApplicationContext):
		"""
		Pause/resume playback.		
		"""
		await MusicCoreService.pausetoggle(ctx)


	@discord.slash_command(name="volume")
	@discord.option(
		name="value",
		description="The desired volume level",
		max_value=200,
		min_value=0,
	)
	@commands.check(MusicCoreService.create_player)
	async def volume(self, ctx: discord.ApplicationContext, value: int):
		"""
		Adjust the volume of the player (clipping may occur when the value exceeds 100).

		Docstring for volume
		
		:param self: Description
		:param ctx: Description
		:type ctx: discord.ApplicationContext
		:param value: Description
		:type value: int
		"""
		await MusicCoreService.set_volume(ctx, value)
	

	@discord.slash_command(name="skip")
	@commands.check(MusicCoreService.create_player)
	async def skip(self, ctx: discord.ApplicationContext):
		"""
		Skip the current track.

		Docstring for skip
		
		:param self: Description
		:param ctx: Description
		:type ctx: discord.ApplicationContext
		"""
		await MusicCoreService.skip_track(ctx)
	

	@discord.slash_command(name="restart")
	@commands.check(MusicCoreService.create_player)
	async def restart(self, ctx: discord.ApplicationContext):
		"""
		Restart the current track.

		Docstring for restart
		
		:param self: Description
		:param ctx: Description
		:type ctx: discord.ApplicationContext
		"""
		await MusicCoreService.restart_current_track(ctx)
	

	@discord.slash_command(name="seek")
	@discord.option(
		name="hour",
		description="The hour value",
		min_value=0,
	)
	@discord.option(
		name="minute",
		description="The minute value",
		min_value=0,
	)
	@discord.option(
		name="second",
		description="The second value",
		min_value=0,
	)
	@commands.check(MusicCoreService.create_player)
	async def seek(self, ctx: discord.ApplicationContext, hour: int, minute: int, second: int):
		"""
		Seek to a specific position in the current track.

		Docstring for seek
		
		:param self: Description
		:param ctx: Description
		:type ctx: discord.ApplicationContext
		:param hour: Description
		:type hour: int
		:param minute: Description
		:type minute: int
		:param second: Description
		:type second: int
		"""
		await MusicCoreService.seek(ctx, hour, minute, second)
	

	@discord.slash_command(name="rewind")
	@discord.option(
		name="value",
		description="How many seconds to rewind",
		min_value=1,
	)
	@commands.check(MusicCoreService.create_player)
	async def rewind(self, ctx: discord.ApplicationContext, value: int = 10):
		"""
		Rewind the current track (defaults to 10 seconds).

		Docstring for rewind
		
		:param self: Description
		:param ctx: Description
		:type ctx: discord.ApplicationContext
		:param value: Description
		:type value: int
		"""
		await MusicCoreService.rewind(ctx, value)

	
	@discord.slash_command(name="fastforward")
	@discord.option(
		name="value",
		description="How many seconds to fast forward",
		min_value=1,
	)
	@commands.check(MusicCoreService.create_player)
	async def fastforward(self, ctx: discord.ApplicationContext, value: int = 10):
		"""
		Fast-forward the current track (defaults to 10 seconds).

		Docstring for fastforward
		
		:param self: Description
		:param ctx: Description
		:type ctx: discord.ApplicationContext
		:param value: Description
		:type value: int
		"""
		await MusicCoreService.fastforward(ctx, value)
	

	# @discord.slash_command(name="stop")
	# @commands.check(MusicCoreService.create_player)
	# async def stop(self, ctx: discord.ApplicationContext):
	# 	"""
	# 	Docstring for stop
		
	# 	:param self: Description
	# 	:param ctx: Description
	# 	:type ctx: discord.ApplicationContext
	# 	"""
	# 	await MusicCoreService.stop_player(ctx)

	
	@discord.slash_command(name="lyrics")
	@commands.check(MusicCoreService.create_player)
	async def lyrics(self, ctx: discord.ApplicationContext):
		"""
		Display lyrics of the current track.

		Docstring for lyrics
		
		:param self: Description
		:param ctx: Description
		:type ctx: discord.ApplicationContext
		"""
		await MusicCoreService.lyrics(ctx)


def setup(bot: discord.Bot):
	bot.add_cog(MusicCore(bot))

import discord

from discord.ext import commands

from services.music.music_core_service import MusicCoreService
from services.music.music_filter_service import MusicFilterService

class MusicFilters(discord.Cog):
	def __init__(self, bot: discord.Bot):
		self.bot = bot
	

	filter_commands = discord.SlashCommandGroup(
		name="filter",
		description="Set filters."
	)


	@filter_commands.command(name="stats")
	@commands.check(MusicCoreService.create_player)
	async def filter_stats(self, ctx: discord.ApplicationContext):
		"""
		Display the current filter settings.
		"""
		await MusicFilterService.filter_stats(ctx)


	@filter_commands.command(name="reset")
	@commands.check(MusicCoreService.create_player)
	async def reset_all(self, ctx: discord.ApplicationContext):
		"""
		Reset all filters.
		"""
		await MusicFilterService.reset_all_filters(ctx)


	@filter_commands.command(name="volume")
	@discord.option(
		name="value",
		description="Set multiplier value. A value > 1.0 may cause clipping.",
		max_value=5.0,
		min_value=0.0,
	)
	@commands.check(MusicCoreService.create_player)
	async def filter_volume(self, ctx: discord.ApplicationContext, value: float):
		"""
		Set volume multiplier.
		"""
		await MusicFilterService.filter_volume(ctx, value)
	

	equalizer = filter_commands.create_subgroup(
		name="equalizer",
		description="Equalizer"
	)


	@equalizer.command(name="set")
	@discord.option(
		name="band0",
		description="Set gain for band 0 [25 Hz]",
		max_value=1.0,
		min_value=-0.25,
	)
	@discord.option(
		name="band1",
		description="Set gain for band 1 [40 Hz]",
		max_value=1.0,
		min_value=-0.25,
	)
	@discord.option(
		name="band2",
		description="Set gain for band 2 [63 Hz]",
		max_value=1.0,
		min_value=-0.25,
	)
	@discord.option(
		name="band3",
		description="Set gain for band 3 [100 Hz]",
		max_value=1.0,
		min_value=-0.25,
	)
	@discord.option(
		name="band4",
		description="Set gain for band 4 [160 Hz]",
		max_value=1.0,
		min_value=-0.25,
	)
	@discord.option(
		name="band5",
		description="Set gain for band 5 [250 Hz]",
		max_value=1.0,
		min_value=-0.25,
	)
	@discord.option(
		name="band6",
		description="Set gain for band 6 [400 Hz]",
		max_value=1.0,
		min_value=-0.25,
	)
	@discord.option(
		name="band7",
		description="Set gain for band 7 [630 Hz]",
		max_value=1.0,
		min_value=-0.25,
	)
	@discord.option(
		name="band8",
		description="Set gain for band 8 [1000 Hz]",
		max_value=1.0,
		min_value=-0.25,
	)
	@discord.option(
		name="band9",
		description="Set gain for band 9 [1600 Hz]",
		max_value=1.0,
		min_value=-0.25,
	)
	@discord.option(
		name="band10",
		description="Set gain for band 10 [2500 Hz]",
		max_value=1.0,
		min_value=-0.25,
	)
	@discord.option(
		name="band11",
		description="Set gain for band 11 [4000 Hz]",
		max_value=1.0,
		min_value=-0.25,
	)
	@discord.option(
		name="band12",
		description="Set gain for band 12 [6300 Hz]",
		max_value=1.0,
		min_value=-0.25,
	)
	@discord.option(
		name="band13",
		description="Set gain for band 13 [10000 Hz]",
		max_value=1.0,
		min_value=-0.25,
	)
	@discord.option(
		name="band14",
		description="Set gain for band 14 [16000 Hz]",
		max_value=1.0,
		min_value=-0.25,
	)
	@commands.check(MusicCoreService.create_player)
	async def set_equalizer(self, ctx: discord.ApplicationContext, band0: float = None, band1: float = None, band2: float = None, band3: float = None, band4: float = None, band5: float = None, band6: float = None, band7: float = None, band8: float = None, band9: float = None, band10: float = None, band11: float = None, band12: float = None, band13: float = None, band14: float = None):
		"""
		Set Equalizer filter.
		"""
		await MusicFilterService.set_equalizer(ctx, band0, band1, band2, band3, band4, band5, band6, band7, band8, band9, band10, band11, band12, band13, band14)
	

	@equalizer.command(name="reset")
	@commands.check(MusicCoreService.create_player)
	async def reset_equalizer(self, ctx: discord.ApplicationContext):
		"""
		Reset Equalizer filter.
		"""
		await MusicFilterService.reset_equalizer(ctx)
	

	karaoke = filter_commands.create_subgroup(
		name="karaoke",
		description="karaoke",
	)


	@karaoke.command(name="set")
	@discord.option(
		name="level",
		description="0.0 is no effect and 1.0 is full effect",
		max_value=1.0,
		min_value=0.0,
	)
	@discord.option(
		name="mono_level",
		description="0.0 is no effect and 1.0 is full effect",
		max_value=1.0,
		min_value=0.0,
	)
	@discord.option(
		name="filter_band",
		description="Target frequency in Hz for vocal reduction.",
	)
	@discord.option(
		name="filter_width",
		description="Range of frequencies that will be affected around `filter_band`",
	)
	@commands.check(MusicCoreService.create_player)
	async def set_karaoke(self, ctx: discord.ApplicationContext, level: float = 1.0, mono_level: float = 1.0, filter_band: float = 220, filter_width: float = 100):
		"""
		Set Karaoke filter.
		"""
		await MusicFilterService.set_karaoke(ctx, level, mono_level, filter_band, filter_width)
	

	@karaoke.command(name="reset")
	@commands.check(MusicCoreService.create_player)
	async def reset_karaoke(self, ctx: discord.ApplicationContext):
		"""
		Reset Karaoke filter.
		"""
		await MusicFilterService.reset_karaoke(ctx)
	

	timescale = filter_commands.create_subgroup(
		name="timescale",
		description="Timescale"
	)

	
	@timescale.command(name="set")
	@discord.option(
		name="speed",
		description="The playback speed",
		min_value=0.0,
	)
	@discord.option(
		name="pitch",
		description="The pitch",
		min_value=0.0,
	)
	@discord.option(
		name="rate",
		description="The rate",
		min_value=0.0,
	)
	@commands.check(MusicCoreService.create_player)
	async def set_timescale(self, ctx: discord.ApplicationContext, speed: float, pitch: float, rate: float):
		"""
		Set Timescale filter.
		"""
		await MusicFilterService.set_timescale(ctx, speed, pitch, rate)
	

	@timescale.command(name="reset")
	@commands.check(MusicCoreService.create_player)
	async def reset_timescale(self, ctx: discord.ApplicationContext):
		"""
		Reset Timescale filter.
		"""
		await MusicFilterService.reset_timescale(ctx)
	

	tremolo = filter_commands.create_subgroup(
		name="tremolo",
		description="Tremolo"
	)


	@tremolo.command(name="set")
	@discord.option(
		name="frequency",
		description="The frequency",
		min_value=0.0,
	)
	@discord.option(
		name="depth",
		description="The tremolo depth",
		max_value=1.0,
		min_value=0.0,
	)
	@commands.check(MusicCoreService.create_player)
	async def set_tremolo(self, ctx: discord.ApplicationContext, frequency: float, depth: float):
		"""
		Set Tremolo filter.
		"""
		await MusicFilterService.set_tremolo(ctx, frequency, depth)
	

	@tremolo.command(name="reset")
	@commands.check(MusicCoreService.create_player)
	async def reset_tremolo(self, ctx: discord.ApplicationContext):
		"""
		Reset Tremolo filter.
		"""
		await MusicFilterService.reset_tremolo(ctx)
	

	vibrato = filter_commands.create_subgroup(
		name="vibrato",
		description="Vibrato"
	)


	@vibrato.command(name="set")
	@discord.option(
		name="frequency",
		description="The frequency",
		max_value=14.0,
		min_value=0.0,
	)
	@discord.option(
		name="depth",
		description="The vibrato depth",
		max_value=1.0,
		min_value=0.0,
	)
	@commands.check(MusicCoreService.create_player)
	async def set_vibrato(self, ctx: discord.ApplicationContext, frequency: float, depth: float):
		"""
		Set Vibrato filter.
		"""
		await MusicFilterService.set_vibrato(ctx, frequency, depth)
	

	@vibrato.command(name="reset")
	@commands.check(MusicCoreService.create_player)
	async def reset_vibrato(self, ctx: discord.ApplicationContext):
		"""
		Reset Vibrato filter.
		"""
		await MusicFilterService.reset_vibrato(ctx)
	

	rotation = filter_commands.create_subgroup(
		name="rotation",
		description="Rotation"
	)


	@rotation.command(name="set")
	@discord.option(
		name="rotation_hz",
		description="The frequency of the audio rotating around the listener in Hz.",
	)
	@commands.check(MusicCoreService.create_player)
	async def set_rotation(self, ctx: discord.ApplicationContext, rotation_hz: float = 0.2):
		"""
		Set Rotation filter.
		"""
		await MusicFilterService.set_rotation(ctx, rotation_hz)
	

	@rotation.command(name="reset")
	@commands.check(MusicCoreService.create_player)
	async def reset_rotation(self, ctx: discord.ApplicationContext):
		"""
		Reset Rotation filter.
		"""
		await MusicFilterService.reset_rotation(ctx)
	

	distortion = filter_commands.create_subgroup(
		name="distortion",
		description="Distortion"
	)


	@distortion.command(name="set")
	@discord.option(
		name="sin_offset",
		description="The sin offset.",
	)
	@discord.option(
		name="sin_scale",
		description="The sin scale.",
	)
	@discord.option(
		name="cos_offset",
		description="The cos offset.",
	)
	@discord.option(
		name="cos_scale",
		description="The cos scale.",
	)
	@discord.option(
		name="tan_offset",
		description="The tan offset.",
	)
	@discord.option(
		name="tan_scale",
		description="The tan scale.",
	)
	@discord.option(
		name="offset",
		description="The offset.",
	)
	@discord.option(
		name="scale",
		description="The scale.",
	)
	@commands.check(MusicCoreService.create_player)
	async def set_distortion(self, ctx: discord.ApplicationContext, sin_offset: float, sin_scale: float, cos_offset: float, cos_scale: float, tan_offset: float, tan_scale: float, offset: float, scale: float):
		"""
		Set Distortion filter.
		"""
		await MusicFilterService.set_distortion(ctx, sin_offset, sin_scale, cos_offset, cos_scale, tan_offset, tan_scale, offset, scale)
	

	@distortion.command(name="reset")
	@commands.check(MusicCoreService.create_player)
	async def reset_distortion(self, ctx: discord.ApplicationContext):
		"""
		Reset Distortion filter.
		"""
		await MusicFilterService.reset_distortion(ctx)
	

	channel_mix = filter_commands.create_subgroup(
		name="channel_mix",
		description="Channel Mix"
	)


	@channel_mix.command(name="set")
	@discord.option(
		name="left_to_left",
		description="The left to left channel mix factor.",
		max_value=1.0,
		min_value=0.0,
	)
	@discord.option(
		name="left_to_right",
		description="The left to right channel mix factor.",
		max_value=1.0,
		min_value=0.0,
	)
	@discord.option(
		name="right_to_left",
		description="The right to left channel mix factor.",
		max_value=1.0,
		min_value=0.0,
	)
	@discord.option(
		name="right_to_right",
		description="The right to right channel mix factor.",
		max_value=1.0,
		min_value=0.0,
	)
	@commands.check(MusicCoreService.create_player)
	async def set_channel_mix(self, ctx: discord.ApplicationContext, left_to_left: float, left_to_right: float, right_to_left: float, right_to_right: float):
		"""
		Set Channel Mix filter.
		"""
		await MusicFilterService.set_channelmix(ctx, left_to_left, left_to_right, right_to_left, right_to_right)
	

	@channel_mix.command(name="reset")
	@commands.check(MusicCoreService.create_player)
	async def reset_channel_mix(self, ctx: discord.ApplicationContext):
		"""
		Reset Channel Mix filter.
		"""
		await MusicFilterService.reset_channelmix(ctx)
	

	low_pass = filter_commands.create_subgroup(
		name="low_pass",
		description="Low Pass"
	)


	@low_pass.command(name="set")
	@discord.option(
		name="smoothing",
		description="The smoothing factor.",
		min_value=1.0,
	)
	@commands.check(MusicCoreService.create_player)
	async def set_low_pass(self, ctx: discord.ApplicationContext, smoothing: float):
		"""
		Set Low Pass filter.
		"""
		await MusicFilterService.set_lowpass(ctx, smoothing)
	

	@low_pass.command(name="reset")
	@commands.check(MusicCoreService.create_player)
	async def reset_low_pass(self, ctx: discord.ApplicationContext):
		"""
		Reset Low Pass filter.
		"""
		await MusicFilterService.reset_lowpass(ctx)


def setup(bot: discord.Bot):
	bot.add_cog(MusicFilters(bot))

from typing import cast

import discord
from discord.ext import pages

import wavelink

from utils import CustomPage
from utils.music import CoreFunctions

class MusicFilters(discord.Cog):
	"""
	A Discord Cog that provides a set of commands to manage and apply various audio filters
	to a music player using the Wavelink library.
	"""

	def __init__(self, bot: discord.Bot):
		self.bot = bot


	filterCommands = discord.SlashCommandGroup(
		name="filter",
		description="Set filters."
	)


	@filterCommands.command(name="volume")
	@discord.option(
		name="value",
		description="Set Filter volume. value > 1.0 may cause clipping.",
		max_value=5.0,
		min_value=0.0,
	)
	async def filterVolume(self, ctx: discord.ApplicationContext, value: float):
		"""Set filter volume."""
		if not await CoreFunctions.check_voice(ctx):
			return
		
		player: wavelink.Player = cast(wavelink.Player, ctx.voice_client)

		filters: wavelink.Filters = player.filters

		filters.volume = value

		await player.set_filters(filters, seek=True)

		await ctx.respond("filter volume has been set.")


	@filterCommands.command(name="reset")
	async def resetAll(self, ctx: discord.ApplicationContext):
		"Reset all filters."
		if not await CoreFunctions.check_voice(ctx):
			return
		
		player: wavelink.Player = cast(wavelink.Player, ctx.voice_client)
		
		filters: wavelink.Filters = player.filters
		filters.reset()

		await player.set_filters(filters, seek=True)

		await ctx.respond("All filters have been reset.")
	

	def get_embed(self, ctx: discord.ApplicationContext, filter_type: str, filter_volume: float, payload):

		filters = {
			"Karaoke": ['level', 'monoLevel', 'filterBand', 'filterWidth'],
			"Timescale": ['speed', 'pitch', 'rate'],
			"Tremolo": ['frequency', 'depth'],
			"Vibrato": ['frequency', 'depth'],
			"Rotation": ['rotationHz'],
			"Distortion": ['sinOffset', 'sinScale', 'cosOffset', 'cosScale', 'tanOffset', 'tanScale', 'offset', 'scale'],
			"Channel Mix": ['leftToLeft', 'leftToRight', 'rightToLeft', 'rightToRight'],
			"Low Pass": ['smoothing'],
		}

		bands = [
			"25 Hz", "40 Hz", "63 Hz", "100 Hz", "160 Hz", "250 Hz", "400 Hz", "630 Hz",
			"1000 Hz", "1600 Hz", "2500 Hz", "4000 Hz", "6300 Hz", "10000 Hz", "16000 Hz",
		]

		author = discord.EmbedAuthor(name=f"{ctx.author.nick if ctx.author.nick else ctx.author.display_name}", icon_url=ctx.author.avatar)
		footer = None

		if filter_volume:
			footer = discord.EmbedFooter(text=f"Filter Volume: {filter_volume}")

		embed: discord.Embed = discord.Embed(title="Current Filter Settings", description=f"## {filter_type}", author=author, footer=footer)

		if not payload:
			embed.add_field(name="", value="*Filter has not been set.*", inline=False)
			return embed

		if filter_type == "Equalizer":
			for i in range(15):
				embed.add_field(name=bands[i], value=payload[i]["gain"])
			return embed

		for field in filters[filter_type]:
			if field in payload:
				embed.add_field(name=field, value=payload[field])

		return embed


	@filterCommands.command(name="stats")
	async def filter_stats(self, ctx: discord.ApplicationContext):
		"Show the current filter settings."
		if not await CoreFunctions.check_voice(ctx):
			return
		
		player: wavelink.Player = cast(wavelink.Player, ctx.voice_client)
		
		filters: wavelink.Filters = player.filters

		filter_pages = []

		filter_pages.append(self.get_embed(ctx, "Equalizer", filters.volume, filters.equalizer.payload))
		filter_pages.append(self.get_embed(ctx, "Karaoke", filters.volume, filters.karaoke.payload))
		filter_pages.append(self.get_embed(ctx, "Timescale", filters.volume, filters.timescale.payload))
		filter_pages.append(self.get_embed(ctx, "Tremolo", filters.volume, filters.tremolo.payload))
		filter_pages.append(self.get_embed(ctx, "Vibrato", filters.volume, filters.vibrato.payload))
		filter_pages.append(self.get_embed(ctx, "Rotation", filters.volume, filters.rotation.payload))
		filter_pages.append(self.get_embed(ctx, "Distortion", filters.volume, filters.distortion.payload))
		filter_pages.append(self.get_embed(ctx, "Channel Mix", filters.volume, filters.channel_mix.payload))
		filter_pages.append(self.get_embed(ctx, "Low Pass", filters.volume, filters.low_pass.payload))

		paginator = pages.Paginator(
			pages=filter_pages,
			use_default_buttons=False,
			custom_buttons=CustomPage.BUTTONS,
		)

		await paginator.respond(ctx.interaction)	


	equalizer = filterCommands.create_subgroup(
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
	async def set_equalizer(self, ctx: discord.ApplicationContext, band0: float = None, band1: float = None, band2: float = None, band3: float = None, band4: float = None, band5: float = None, band6: float = None, band7: float = None, band8: float = None, band9: float = None, band10: float = None, band11: float = None, band12: float = None, band13: float = None, band14: float = None):
		"""Set Equalizer filter."""
		if not await CoreFunctions.check_voice(ctx):
			return
		
		player: wavelink.Player = cast(wavelink.Player, ctx.voice_client)
		
		gains = [
			band0, band1, band2, band3, band4,
			band5, band6, band7, band8, band9,
			band10, band11, band12, band13, band14,
		]

		filters: wavelink.Filters = player.filters

		payload = filters.equalizer.payload # payload structure e.g. idx = 0 --- {0: {'band': 0, 'gain': 0.0}}

		bands = []

		for idx, gain in enumerate(gains):
			if gain != None: # since if not gain returns True even when gain is 0, we are using gain != None to check None values
				bandData = {"band": idx, "gain": gain}
				bands.append(bandData)
			else:
				bands.append(payload[idx])

		filters.equalizer.set(bands=bands)

		await player.set_filters(filters, seek=True)

		await ctx.respond("Equalizer has been set.")


	@equalizer.command(name="reset")
	async def reset_equalizer(self, ctx: discord.ApplicationContext):
		"""Reset Equalizer filter."""
		if not await CoreFunctions.check_voice(ctx):
			return
		
		player: wavelink.Player = cast(wavelink.Player, ctx.voice_client)
		filters: wavelink.Filters = player.filters

		filters.equalizer.reset()

		await player.set_filters(filters, seek=True)

		await ctx.respond("Equalizer has been reset.")


	# @equalizer.command(name="preset")
	# @discord.option(
	# 	name="preset",
	# 	description="Select preset",
	# 	choices=[
	# 		"Bass Boost",
	# 		"Treble Boost",
	# 		"Rock",
	# 		"Pop",
	# 		"Jazz",
	# 		"Classical",
	# 		"Dance",
	# 		"Hip-Hop",
	# 		"Acoustic",
	# 		"Electronic",
	# 		"R&B/Soul",
	# 		"Country",
	# 		"Live/Studio",
	# 	]
	# )
	# async def equalizer_preset(self, ctx: discord.ApplicationContext, preset: str):
	# 	if not await CoreFunctions.check_voice(ctx):
	# 		return
		
	# 	presets = {
	# 		"Bass Boost": [
	# 			{"band": 0, "gain": 1.0},
	# 			{"band": 1, "gain": 0.8},
	# 			{"band": 2, "gain": 0.6},
	# 			{"band": 3, "gain": 0.4},
	# 			{"band": 4, "gain": 0.2},
	# 			{"band": 5, "gain": 0.1},
	# 			{"band": 6, "gain": -0.1},
	# 			{"band": 7, "gain": -0.1},
	# 			{"band": 8, "gain": -0.1},
	# 			{"band": 9, "gain": 0.0},
	# 			{"band": 10, "gain": 0.0},
	# 			{"band": 11, "gain": 0.0},
	# 			{"band": 12, "gain": 0.0},
	# 			{"band": 13, "gain": 0.0},
	# 			{"band": 14, "gain": 0.0},
	# 		],
	# 		"Treble Boost": [
	# 			{"band": 0, "gain": -0.1},
	# 			{"band": 1, "gain": -0.1},
	# 			{"band": 2, "gain": -0.1},
	# 			{"band": 3, "gain": -0.1},
	# 			{"band": 4, "gain": -0.1},
	# 			{"band": 5, "gain": -0.1},
	# 			{"band": 6, "gain": -0.1},
	# 			{"band": 7, "gain": -0.1},
	# 			{"band": 8, "gain": 0.0},
	# 			{"band": 9, "gain": 0.2},
	# 			{"band": 10, "gain": 0.3},
	# 			{"band": 11, "gain": 0.4},
	# 			{"band": 12, "gain": 0.5},
	# 			{"band": 13, "gain": 0.6},
	# 			{"band": 14, "gain": 0.6},
	# 		],
	# 		"Rock": [
	# 			{"band": 0, "gain": 0.8},
	# 			{"band": 1, "gain": 0.7},
	# 			{"band": 2, "gain": 0.6},
	# 			{"band": 3, "gain": 0.0},
	# 			{"band": 4, "gain": -0.1},
	# 			{"band": 5, "gain": -0.1},
	# 			{"band": 6, "gain": -0.1},
	# 			{"band": 7, "gain": 0.0},
	# 			{"band": 8, "gain": 0.1},
	# 			{"band": 9, "gain": 0.5},
	# 			{"band": 10, "gain": 0.7},
	# 			{"band": 11, "gain": 0.8},
	# 			{"band": 12, "gain": 0.9},
	# 			{"band": 13, "gain": 1.0},
	# 			{"band": 14, "gain": 1.0},
	# 		],
	# 		"Pop": [
	# 			{"band": 0, "gain": 0.3},
	# 			{"band": 1, "gain": 0.2},
	# 			{"band": 2, "gain": 0.1},
	# 			{"band": 3, "gain": 0.0},
	# 			{"band": 4, "gain": 0.1},
	# 			{"band": 5, "gain": 0.2},
	# 			{"band": 6, "gain": 0.2},
	# 			{"band": 7, "gain": 0.2},
	# 			{"band": 8, "gain": 0.1},
	# 			{"band": 9, "gain": 0.0},
	# 			{"band": 10, "gain": 0.1},
	# 			{"band": 11, "gain": 0.2},
	# 			{"band": 12, "gain": 0.2},
	# 			{"band": 13, "gain": 0.1},
	# 			{"band": 14, "gain": 0.0},
	# 		],
	# 		"Jazz": [
	# 			{"band": 0, "gain": 0.0},
	# 			{"band": 1, "gain": 0.0},
	# 			{"band": 2, "gain": 0.1},
	# 			{"band": 3, "gain": 0.2},
	# 			{"band": 4, "gain": 0.3},
	# 			{"band": 5, "gain": 0.3},
	# 			{"band": 6, "gain": 0.3},
	# 			{"band": 7, "gain": 0.3},
	# 			{"band": 8, "gain": 0.3},
	# 			{"band": 9, "gain": 0.2},
	# 			{"band": 10, "gain": 0.2},
	# 			{"band": 11, "gain": 0.1},
	# 			{"band": 12, "gain": 0.0},
	# 			{"band": 13, "gain": 0.0},
	# 			{"band": 14, "gain": 0.0},
	# 		],
	# 		"Classical": [
	# 			{"band": 0, "gain": 0.0},
	# 			{"band": 1, "gain": 0.0},
	# 			{"band": 2, "gain": 0.0},
	# 			{"band": 3, "gain": 0.0},
	# 			{"band": 4, "gain": 0.0},
	# 			{"band": 5, "gain": 0.0},
	# 			{"band": 6, "gain": 0.0},
	# 			{"band": 7, "gain": 0.0},
	# 			{"band": 8, "gain": 0.0},
	# 			{"band": 9, "gain": 0.0},
	# 			{"band": 10, "gain": 0.0},
	# 			{"band": 11, "gain": 0.0},
	# 			{"band": 12, "gain": 0.0},
	# 			{"band": 13, "gain": 0.2},
	# 			{"band": 14, "gain": 0.2},
	# 		],
	# 		"Dance": [
	# 			{"band": 0, "gain": 0.5},
	# 			{"band": 1, "gain": 0.4},
	# 			{"band": 2, "gain": 0.2},
	# 			{"band": 3, "gain": 0.0},
	# 			{"band": 4, "gain": 0.1},
	# 			{"band": 5, "gain": 0.2},
	# 			{"band": 6, "gain": 0.0},
	# 			{"band": 7, "gain": -0.1},
	# 			{"band": 8, "gain": 0.0},
	# 			{"band": 9, "gain": 0.2},
	# 			{"band": 10, "gain": 0.4},
	# 			{"band": 11, "gain": 0.5},
	# 			{"band": 12, "gain": 0.4},
	# 			{"band": 13, "gain": 0.3},
	# 			{"band": 14, "gain": 0.2},
	# 		],
	# 		"Hip-Hop": [
	# 			{"band": 0, "gain": 1.0},
	# 			{"band": 1, "gain": 0.9},
	# 			{"band": 2, "gain": 0.8},
	# 			{"band": 3, "gain": 0.6},
	# 			{"band": 4, "gain": 0.4},
	# 			{"band": 5, "gain": 0.1},
	# 			{"band": 6, "gain": 0.0},
	# 			{"band": 7, "gain": -0.1},
	# 			{"band": 8, "gain": 0.0},
	# 			{"band": 9, "gain": 0.1},
	# 			{"band": 10, "gain": 0.3},
	# 			{"band": 11, "gain": 0.4},
	# 			{"band": 12, "gain": 0.5},
	# 			{"band": 13, "gain": 0.6},
	# 			{"band": 14, "gain": 0.7},
	# 		],
	# 		"Acoustic": [
	# 			{"band": 0, "gain": 0.2},
	# 			{"band": 1, "gain": 0.2},
	# 			{"band": 2, "gain": 0.2},
	# 			{"band": 3, "gain": 0.3},
	# 			{"band": 4, "gain": 0.4},
	# 			{"band": 5, "gain": 0.4},
	# 			{"band": 6, "gain": 0.3},
	# 			{"band": 7, "gain": 0.2},
	# 			{"band": 8, "gain": 0.2},
	# 			{"band": 9, "gain": 0.2},
	# 			{"band": 10, "gain": 0.1},
	# 			{"band": 11, "gain": 0.0},
	# 			{"band": 12, "gain": 0.0},
	# 			{"band": 13, "gain": 0.0},
	# 			{"band": 14, "gain": 0.0},
	# 		],
	# 		"Electronic": [
	# 			{"band": 0, "gain": 0.9},
	# 			{"band": 1, "gain": 0.8},
	# 			{"band": 2, "gain": 0.7},
	# 			{"band": 3, "gain": 0.5},
	# 			{"band": 4, "gain": 0.3},
	# 			{"band": 5, "gain": 0.1},
	# 			{"band": 6, "gain": 0.0},
	# 			{"band": 7, "gain": 0.0},
	# 			{"band": 8, "gain": 0.2},
	# 			{"band": 9, "gain": 0.4},
	# 			{"band": 10, "gain": 0.6},
	# 			{"band": 11, "gain": 0.8},
	# 			{"band": 12, "gain": 0.9},
	# 			{"band": 13, "gain": 1.0},
	# 			{"band": 14, "gain": 1.0},
	# 		],
	# 		"R&B/Soul": [
	# 			{"band": 0, "gain": 0.3},
	# 			{"band": 1, "gain": 0.3},
	# 			{"band": 2, "gain": 0.3},
	# 			{"band": 3, "gain": 0.4},
	# 			{"band": 4, "gain": 0.5},
	# 			{"band": 5, "gain": 0.5},
	# 			{"band": 6, "gain": 0.5},
	# 			{"band": 7, "gain": 0.5},
	# 			{"band": 8, "gain": 0.5},
	# 			{"band": 9, "gain": 0.4},
	# 			{"band": 10, "gain": 0.3},
	# 			{"band": 11, "gain": 0.2},
	# 			{"band": 12, "gain": 0.1},
	# 			{"band": 13, "gain": 0.0},
	# 			{"band": 14, "gain": 0.0},
	# 		],
	# 		"Country": [
	# 			{"band": 0, "gain": 0.4},
	# 			{"band": 1, "gain": 0.4},
	# 			{"band": 2, "gain": 0.4},
	# 			{"band": 3, "gain": 0.3},
	# 			{"band": 4, "gain": 0.3},
	# 			{"band": 5, "gain": 0.3},
	# 			{"band": 6, "gain": 0.3},
	# 			{"band": 7, "gain": 0.4},
	# 			{"band": 8, "gain": 0.5},
	# 			{"band": 9, "gain": 0.5},
	# 			{"band": 10, "gain": 0.4},
	# 			{"band": 11, "gain": 0.3},
	# 			{"band": 12, "gain": 0.2},
	# 			{"band": 13, "gain": 0.1},
	# 			{"band": 14, "gain": 0.1},
	# 		],
	# 		"Live/Studio": [
	# 			{"band": 0, "gain": 0.1},
	# 			{"band": 1, "gain": 0.1},
	# 			{"band": 2, "gain": 0.1},
	# 			{"band": 3, "gain": 0.1},
	# 			{"band": 4, "gain": 0.1},
	# 			{"band": 5, "gain": 0.1},
	# 			{"band": 6, "gain": 0.15},
	# 			{"band": 7, "gain": 0.25},
	# 			{"band": 8, "gain": 0.15},
	# 			{"band": 9, "gain": 0.1},
	# 			{"band": 10, "gain": 0.1},
	# 			{"band": 11, "gain": 0.1},
	# 			{"band": 12, "gain": 0.1},
	# 			{"band": 13, "gain": 0.1},
	# 			{"band": 14, "gain": 0.1},
	# 		],
	# 	}

	# 	player: wavelink.Player = cast(wavelink.Player, ctx.voice_client)

	# 	filters: wavelink.Filters = player.filters

	# 	filters.equalizer.set(bands=presets[preset])

	# 	await player.set_filters(filters, seek=True)

	# 	await ctx.respond(f"Equalizer has been set to preset `{preset}`")


	karaoke = filterCommands.create_subgroup(
		name="karaoke",
		description="Karaoke"
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
	async def set_karaoke(self, ctx: discord.ApplicationContext, level: float = 1.0, mono_level: float = 1.0, filter_band: float = 220, filter_width: float = 100):
		"""Set Karaoke filter."""
		if not await CoreFunctions.check_voice(ctx):
			return
		
		player: wavelink.Player = cast(wavelink.Player, ctx.voice_client)

		filters: wavelink.Filters = player.filters
		filters.karaoke.set(
			level=level,
			mono_level=mono_level,
			filter_band=filter_band,
			filter_width=filter_width,
		)

		await player.set_filters(filters, seek=True)

		await ctx.respond("karaoke has been set.")


	@karaoke.command(name="reset")
	async def reset_karaoke(self, ctx: discord.ApplicationContext):
		"""Reset Karaoke filter."""
		if not await CoreFunctions.check_voice(ctx):
			return
		
		player: wavelink.Player = cast(wavelink.Player, ctx.voice_client)
		filters: wavelink.Filters = player.filters

		filters.karaoke.reset()

		await player.set_filters(filters, seek=True)

		await ctx.respond("karaoke has been reset.")


	timescale = filterCommands.create_subgroup(
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
	async def set_timescale(self, ctx: discord.ApplicationContext, speed: float, pitch: float, rate: float):
		"Set Timescale filter."
		if not await CoreFunctions.check_voice(ctx):
			return
		
		player: wavelink.Player = cast(wavelink.Player, ctx.voice_client)

		filters: wavelink.Filters = player.filters
		filters.timescale.set(
			speed=speed,
			pitch=pitch,
			rate=rate,
		)

		await player.set_filters(filters, seek=True)

		await ctx.respond("timescale has been set.")


	@timescale.command(name="reset")
	async def reset_timescale(self, ctx: discord.ApplicationContext):
		"""Reset Timescale filter."""
		if not await CoreFunctions.check_voice(ctx):
			return
		
		player: wavelink.Player = cast(wavelink.Player, ctx.voice_client)
		filters: wavelink.Filters = player.filters

		filters.timescale.reset()

		await player.set_filters(filters, seek=True)

		await ctx.respond("timescale has been reset.")


	tremolo = filterCommands.create_subgroup(
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
	async def set_tremolo(self, ctx: discord.ApplicationContext, frequency: float, depth: float):
		"Set Tremolo filter."
		if not await CoreFunctions.check_voice(ctx):
			return
		
		player: wavelink.Player = cast(wavelink.Player, ctx.voice_client)

		filters: wavelink.Filters = player.filters
		filters.tremolo.set(
			frequency=frequency,
			depth=depth,
		)

		await player.set_filters(filters, seek=True)

		await ctx.respond("tremolo has been set.")


	@tremolo.command(name="reset")
	async def reset_tremolo(self, ctx: discord.ApplicationContext):
		"""Reset Tremolo filter."""
		if not await CoreFunctions.check_voice(ctx):
			return
		
		player: wavelink.Player = cast(wavelink.Player, ctx.voice_client)
		filters: wavelink.Filters = player.filters

		filters.tremolo.reset()

		await player.set_filters(filters, seek=True)

		await ctx.respond("tremolo has been reset.")


	vibrato = filterCommands.create_subgroup(
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
	async def set_vibrato(self, ctx: discord.ApplicationContext, frequency: float, depth: float):
		"Set Vibrato filter."
		if not await CoreFunctions.check_voice(ctx):
			return
		
		player: wavelink.Player = cast(wavelink.Player, ctx.voice_client)

		filters: wavelink.Filters = player.filters
		filters.vibrato.set(
			frequency=frequency,
			depth=depth,
		)

		await player.set_filters(filters, seek=True)

		await ctx.respond("vibrato has been set.")


	@vibrato.command(name="reset")
	async def reset_vibrato(self, ctx: discord.ApplicationContext):
		"""Reset Vibrato filter."""
		if not await CoreFunctions.check_voice(ctx):
			return
		
		player: wavelink.Player = cast(wavelink.Player, ctx.voice_client)
		filters: wavelink.Filters = player.filters

		filters.vibrato.reset()

		await player.set_filters(filters, seek=True)

		await ctx.respond("vibrato has been reset.")


	rotation = filterCommands.create_subgroup(
		name="rotation",
		description="Rotation"
	)


	@rotation.command(name="set")
	@discord.option(
		name="rotation_hz",
		description="The frequency of the audio rotating around the listener in Hz.",
	)
	async def set_rotation(self, ctx: discord.ApplicationContext, rotation_hz: float = 0.2):
		"Set Rotation filter."
		if not await CoreFunctions.check_voice(ctx):
			return
		
		player: wavelink.Player = cast(wavelink.Player, ctx.voice_client)

		filters: wavelink.Filters = player.filters
		filters.rotation.set(
			rotation_hz=rotation_hz,
		)

		await player.set_filters(filters, seek=True)

		await ctx.respond("rotation has been set.")


	@rotation.command(name="reset")
	async def reset_rotation(self, ctx: discord.ApplicationContext):
		"""Reset Rotation filter."""
		if not await CoreFunctions.check_voice(ctx):
			return
		
		player: wavelink.Player = cast(wavelink.Player, ctx.voice_client)
		filters: wavelink.Filters = player.filters

		filters.rotation.reset()

		await player.set_filters(filters, seek=True)

		await ctx.respond("rotation has been reset.")


	distortion = filterCommands.create_subgroup(
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
	async def set_distortion(self, ctx: discord.ApplicationContext, sin_offset: float, sin_scale: float, cos_offset: float, cos_scale: float, tan_offset: float, tan_scale: float, offset: float, scale: float):
		"Set Distortion filter."
		if not await CoreFunctions.check_voice(ctx):
			return
		
		player: wavelink.Player = cast(wavelink.Player, ctx.voice_client)

		filters: wavelink.Filters = player.filters
		filters.distortion.set(
			sin_offset=sin_offset,
			sin_scale=sin_scale,
			cos_offset=cos_offset,
			cos_scale=cos_scale,
			tan_offset=tan_offset,
			tan_scale=tan_scale,
			offset=offset,
			scale=scale,
		)

		await player.set_filters(filters, seek=True)

		await ctx.respond("distortion has been set.")


	@distortion.command(name="reset")
	async def reset_distortion(self, ctx: discord.ApplicationContext):
		"""Reset Distortion filter."""
		if not await CoreFunctions.check_voice(ctx):
			return
		
		player: wavelink.Player = cast(wavelink.Player, ctx.voice_client)
		filters: wavelink.Filters = player.filters

		filters.distortion.reset()

		await player.set_filters(filters, seek=True)

		await ctx.respond("distortion has been reset.")


	channel_mix = filterCommands.create_subgroup(
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
	async def set_channel_mix(self, ctx: discord.ApplicationContext, left_to_left: float, left_to_right: float, right_to_left: float, right_to_right: float):
		"Set Channel Mix filter."
		if not await CoreFunctions.check_voice(ctx):
			return
		
		player: wavelink.Player = cast(wavelink.Player, ctx.voice_client)

		filters: wavelink.Filters = player.filters
		filters.channel_mix.set(
			left_to_left=left_to_left,
			left_to_right=left_to_right,
			right_to_left=right_to_left,
			right_to_right=right_to_right,
		)

		await player.set_filters(filters, seek=True)

		await ctx.respond("channel_mix has been set.")


	@channel_mix.command(name="reset")
	async def reset_channel_mix(self, ctx: discord.ApplicationContext):
		"""Reset channel mix filter."""
		if not await CoreFunctions.check_voice(ctx):
			return
		
		player: wavelink.Player = cast(wavelink.Player, ctx.voice_client)
		filters: wavelink.Filters = player.filters

		filters.channel_mix.reset()

		await player.set_filters(filters, seek=True)

		await ctx.respond("channel mix has been reset.")


	low_pass = filterCommands.create_subgroup(
		name="low_pass",
		description="Low Pass"
	)


	@low_pass.command(name="set")
	@discord.option(
		name="smoothing",
		description="The smoothing factor",
		min_value=1.0,
	)
	async def set_low_pass(self, ctx: discord.ApplicationContext, smoothing: float):
		"Set low pass filter."
		if not await CoreFunctions.check_voice(ctx):
			return
		
		player: wavelink.Player = cast(wavelink.Player, ctx.voice_client)

		filters: wavelink.Filters = player.filters
		filters.low_pass.set(
			smoothing=smoothing
		)

		await player.set_filters(filters, seek=True)

		await ctx.respond("low pass has been set.")


	@low_pass.command(name="reset")
	async def reset_low_pass(self, ctx: discord.ApplicationContext):
		"""Reset Timescale filter."""
		if not await CoreFunctions.check_voice(ctx):
			return
		
		player: wavelink.Player = cast(wavelink.Player, ctx.voice_client)
		filters: wavelink.Filters = player.filters

		filters.low_pass.reset()

		await player.set_filters(filters, seek=True)

		await ctx.respond("low pass has been reset.")


def setup(bot: discord.Bot):
	bot.add_cog(MusicFilters(bot))

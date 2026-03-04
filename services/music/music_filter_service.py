import discord
import lavalink

from discord.ext import pages
from bot import CustomPage

class MusicFilterService:


	async def reset_all_filters(ctx: discord.ApplicationContext):
		player: lavalink.DefaultPlayer = ctx.bot.lavalink.player_manager.get(ctx.guild.id)
		
		await player.clear_filters()

		await ctx.respond("All filters have been reset.")
	

	async def filter_volume(ctx: discord.ApplicationContext, value: float):
		player: lavalink.DefaultPlayer = ctx.bot.lavalink.player_manager.get(ctx.guild.id)

		volume = lavalink.filters.Volume()
		volume.update(volume=value)

		await player.set_filter(volume)

		await ctx.respond(f"Filter volume has been set to `{value}`")
	

	async def filter_stats(ctx: discord.ApplicationContext):
		player: lavalink.DefaultPlayer = ctx.bot.lavalink.player_manager.get(ctx.guild.id)

		all_filters = {
			'equalizer': 'Equalizer',
			'karaoke': 'Karaoke',
			'timescale': 'Timescale',
			'tremolo': 'Tremolo',
			'vibrato': 'Vibrato',
			'rotation': 'Rotation',
			'distortion': 'Distortion',
			'channelmix': 'Channel Mix',
			'lowpass': 'Low Pass',
		}

		filter_pages = []

		volume = -1.0
		if player.get_filter('volume'):
			volume = player.get_filter('volume').values

		for filter in all_filters.keys():
			if not player.get_filter(filter):
				payload = None
			else:
				payload = player.get_filter(filter).values

			filter_pages.append(MusicFilterService.get_embed(ctx, all_filters[filter], volume, payload))

		paginator = pages.Paginator(
			pages=filter_pages,
			use_default_buttons=False,
			custom_buttons=CustomPage.BUTTONS,
		)

		await paginator.respond(ctx.interaction)
	

	def get_embed(ctx: discord.ApplicationContext, filter_type: str, filter_volume: float, payload): # payload is a name that has passed from wavelink. it's basically `values` from Filter object. it can also be `None`
		
		filters = {
			"Karaoke": ['level', 'monoLevel', 'filterBand', 'filterWidth'],
			"Timescale": ['speed', 'pitch', 'rate'],
			"Tremolo": ['frequency', 'depth'],
			"Vibrato": ['frequency', 'depth'],
			"Rotation": 'rotationHz',
			"Distortion": ['sinOffset', 'sinScale', 'cosOffset', 'cosScale', 'tanOffset', 'tanScale', 'offset', 'scale'],
			"Channel Mix": ['leftToLeft', 'leftToRight', 'rightToLeft', 'rightToRight'],
			"Low Pass": 'smoothing',
		}

		bands = [
			"25 Hz", "40 Hz", "63 Hz", "100 Hz", "160 Hz", "250 Hz", "400 Hz", "630 Hz",
			"1000 Hz", "1600 Hz", "2500 Hz", "4000 Hz", "6300 Hz", "10000 Hz", "16000 Hz",
		]

		author = discord.EmbedAuthor(name=f"{ctx.author.nick if ctx.author.nick else ctx.author.display_name}", icon_url=ctx.author.avatar)
		footer = None

		if filter_volume != -1:
			footer = discord.EmbedFooter(text=f"Volume Multiplier: {filter_volume}")
		
		embed: discord.Embed = discord.Embed(title="Current Filter Settings", description=f"## {filter_type}", author=author, footer=footer)

		if not payload:
			embed.add_field(name="", value="*Filter has not been set.*", inline=False)
			return embed
		
		if filter_type == "Equalizer":
			for i in range(15):
				embed.add_field(name=bands[i], value=payload[i])
			return embed
		
		if filter_type == "Rotation":
			embed.add_field(name=filters[filter_type], value=payload)
			return embed
		
		if filter_type == "Low Pass":
			embed.add_field(name=filters[filter_type], value=payload)
			return embed
		
		for field in filters[filter_type]:
			if field in payload:
				embed.add_field(name=field, value=payload[field])
		
		return embed
	

	async def set_equalizer(ctx: discord.ApplicationContext, band0: float = None, band1: float = None, band2: float = None, band3: float = None, band4: float = None, band5: float = None, band6: float = None, band7: float = None, band8: float = None, band9: float = None, band10: float = None, band11: float = None, band12: float = None, band13: float = None, band14: float = None):
		player: lavalink.DefaultPlayer = ctx.bot.lavalink.player_manager.get(ctx.guild.id)

		gains = [
			band0, band1, band2, band3, band4,
			band5, band6, band7, band8, band9,
			band10, band11, band12, band13, band14,
		]

		bands = []

		payload = None

		equalizer = player.get_filter('equalizer')

		if equalizer:
			payload = equalizer.values

		for idx, gain in enumerate(gains):
			if gain is None:
				gain = 0.0 if not payload else payload[idx]
			
			band_data = (idx, gain)
			bands.append(band_data)
		
		equalizer = lavalink.filters.Equalizer()
		equalizer.update(bands=bands)

		await player.set_filter(equalizer)

		await ctx.respond("Equalizer has been set.")
	

	async def reset_equalizer(ctx: discord.ApplicationContext):
		player: lavalink.DefaultPlayer = ctx.bot.lavalink.player_manager.get(ctx.guild.id)

		await player.remove_filter('equalizer')

		await ctx.respond("Equalizer has been reset.")
	

	async def set_karaoke(ctx: discord.ApplicationContext, level: float = 1.0, mono_level: float = 1.0, filter_band: float = 220, filter_width: float = 100):
		player: lavalink.DefaultPlayer = ctx.bot.lavalink.player_manager.get(ctx.guild.id)
		
		karaoke = lavalink.filters.Karaoke()
		karaoke.update(
			level=level,
			mono_level=mono_level,
			filter_band=filter_band,
			filter_width=filter_width,
		)

		await player.set_filter(karaoke)

		await ctx.respond("Karaoke has been applied.")
	

	async def reset_karaoke(ctx: discord.ApplicationContext):
		player: lavalink.DefaultPlayer = ctx.bot.lavalink.player_manager.get(ctx.guild.id)

		await player.remove_filter('karaoke')

		await ctx.respond("Karaoke has been reset.")
	

	async def set_timescale(ctx: discord.ApplicationContext, speed: float, pitch: float, rate: float):
		player: lavalink.DefaultPlayer = ctx.bot.lavalink.player_manager.get(ctx.guild.id)

		timescale = lavalink.filters.Timescale()
		timescale.update(
			speed=speed,
			pitch=pitch,
			rate=rate,
		)

		await player.set_filter(timescale)

		await ctx.respond("Timescale has been set.")
	

	async def reset_timescale(ctx: discord.ApplicationContext):
		player: lavalink.DefaultPlayer = ctx.bot.lavalink.player_manager.get(ctx.guild.id)

		await player.remove_filter('timescale')

		await ctx.respond("Timescale has been reset.")
	

	async def set_tremolo(ctx: discord.ApplicationContext, frequency: float, depth: float):
		player: lavalink.DefaultPlayer = ctx.bot.lavalink.player_manager.get(ctx.guild.id)

		tremolo = lavalink.filters.Tremolo()
		tremolo.update(
			frequency=frequency,
			depth=depth,
		)

		await player.set_filter(tremolo)

		await ctx.respond("Tremolo has been set.")
	

	async def reset_tremolo(ctx: discord.ApplicationContext):
		player: lavalink.DefaultPlayer = ctx.bot.lavalink.player_manager.get(ctx.guild.id)

		await player.remove_filter('tremolo')

		await ctx.respond("Tremolo has been reset.")
	

	async def set_vibrato(ctx: discord.ApplicationContext, frequency: float, depth: float):
		player: lavalink.DefaultPlayer = ctx.bot.lavalink.player_manager.get(ctx.guild.id)

		vibrato = lavalink.filters.Vibrato()
		vibrato.update(
			frequency=frequency,
			depth=depth,
		)

		await player.set_filter(vibrato)

		await ctx.respond("Vibrato has been set.")
	

	async def reset_vibrato(ctx: discord.ApplicationContext):
		player: lavalink.DefaultPlayer = ctx.bot.lavalink.player_manager.get(ctx.guild.id)

		await player.remove_filter('vibrato')

		await ctx.respond("Vibrato has been reset.")
	

	async def set_rotation(ctx: discord.ApplicationContext, rotation_hz: float = 0.2):
		player: lavalink.DefaultPlayer = ctx.bot.lavalink.player_manager.get(ctx.guild.id)

		rotation = lavalink.filters.Rotation()
		rotation.update(
			rotation_hz=rotation_hz
		)

		await player.set_filter(rotation)

		await ctx.respond("Rotation has been set.")
	

	async def reset_rotation(ctx: discord.ApplicationContext):
		player: lavalink.DefaultPlayer = ctx.bot.lavalink.player_manager.get(ctx.guild.id)

		await player.remove_filter('rotation')

		await ctx.respond("Rotation has been reset.")
	

	async def set_distortion(ctx: discord.ApplicationContext, sin_offset: float, sin_scale: float, cos_offset: float, cos_scale: float, tan_offset: float, tan_scale: float, offset: float, scale: float):
		player: lavalink.DefaultPlayer = ctx.bot.lavalink.player_manager.get(ctx.guild.id)

		distortion = lavalink.filters.Distortion()
		distortion.update(
			sin_offset=sin_offset,
			sin_scale=sin_scale,
			cos_offset=cos_offset,
			cos_scale=cos_scale,
			tan_offset=tan_offset,
			tan_scale=tan_scale,
			offset=offset,
			scale=scale,
		)

		await player.set_filter(distortion)

		await ctx.respond("Distortion has been set.")
	

	async def reset_distortion(ctx: discord.ApplicationContext):
		player: lavalink.DefaultPlayer = ctx.bot.lavalink.player_manager.get(ctx.guild.id)

		await player.remove_filter('distortion')

		await ctx.respond("Distortion has been reset.")
	

	async def set_channelmix(ctx: discord.ApplicationContext, left_to_left: float, left_to_right: float, right_to_left: float, right_to_right: float):
		player: lavalink.DefaultPlayer = ctx.bot.lavalink.player_manager.get(ctx.guild.id)

		channelmix = lavalink.filters.ChannelMix()
		channelmix.update(
			left_to_left=left_to_left,
			left_to_right=left_to_right,
			right_to_left=right_to_left,
			right_to_right=right_to_right,
		)

		await player.set_filter(channelmix)

		await ctx.respond("Channel Mix has been set.")
	

	async def reset_channelmix(ctx: discord.ApplicationContext):
		player: lavalink.DefaultPlayer = ctx.bot.lavalink.player_manager.get(ctx.guild.id)

		await player.remove_filter('channelmix')

		await ctx.respond("Channel Mix has been reset.")
	

	async def set_lowpass(ctx: discord.ApplicationContext, smoothing: float):
		player: lavalink.DefaultPlayer = ctx.bot.lavalink.player_manager.get(ctx.guild.id)

		lowpass = lavalink.filters.LowPass()
		lowpass.update(
			smoothing=smoothing
		)

		await player.set_filter(lowpass)

		await ctx.respond("Low Pass has been set.")
	

	async def reset_lowpass(ctx: discord.ApplicationContext):
		player: lavalink.DefaultPlayer = ctx.bot.lavalink.player_manager.get(ctx.guild.id)

		await player.remove_filter('lowpass')

		await ctx.respond("Low Pass has been reset.")
	

	

import discord
import lavalink


class LavaPlayer(discord.Cog):
	
	def __init__(self, bot: discord.Bot):
		self.bot = bot
	
	
	def cog_unload(self):
		"""
		This will remove any registered event hooks when the cog is unloaded.
		They will subsequently be registered again once the cog is loaded.
		
		This effectively allows for event handlers to be updated when the cog is reloaded.
		"""
		self.lavalink._event_hooks.clear()
	

	@discord.Cog.listener()
	async def on_ready(self):
		if not hasattr(self.bot, 'lavalink'):
			self.bot.lavalink = lavalink.Client(self.bot.user.id)
			self.bot.lavalink.add_node(
				host='192.168.1.234',
				port=2333,
				password='youshallnotpass',
				region='us',
				name='default-node'
			)
		
		self.lavalink: lavalink.Client = self.bot.lavalink
		self.lavalink.add_event_hooks(self)

	@lavalink.listener(lavalink.TrackStartEvent)
	async def on_track_start(self, event: lavalink.TrackStartEvent):
		guild_id = event.player.guild_id
		channel_id = event.player.fetch('channel')
		guild = self.bot.get_guild(guild_id)

		if not guild:
			return await self.lavalink.player_manager.destroy(guild_id)
		
		channel = guild.get_channel(channel_id)

		if channel:
			await channel.send(f'Now playing: {event.track.title} by {event.track.author}')
	
	@lavalink.listener(lavalink.QueueEndEvent)
	async def on_queue_end(self, event: lavalink.QueueEndEvent):
		guild_id = event.player.guild_id
		guild = self.bot.get_guild(guild_id)

		if guild is not None:
			await guild.voice_client.disconnect(force=True)


def setup(bot: discord.Bot):
	bot.add_cog(LavaPlayer(bot))

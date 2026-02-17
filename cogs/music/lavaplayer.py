# loading lavalink credentials from .env
import os
from dotenv import load_dotenv

import requests

import discord
import lavalink

from services.music.music_core_service import MusicCoreService


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
			load_dotenv()
			lavalink_address = os.getenv('LAVALINK_SERVER_ADDRESS')
			host, port = lavalink_address.split(':') # the 'https://' part may cause trouble
			password = os.getenv('LAVALINK_SERVER_PASSWORD')
			self.bot.lavalink = lavalink.Client(self.bot.user.id)
			self.bot.lavalink.add_node(
				host=host,
				port=port,
				password=password,
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
		player: lavalink.DefaultPlayer = event.player

		if not guild:
			return await self.lavalink.player_manager.destroy(guild_id)
		
		channel = guild.get_channel(channel_id)

		if not channel:
			return
		
		embed: discord.Embed = discord.Embed(title="Now Playing")
		embed.description = f"**[{event.track.title}]({event.track.uri})** by `{event.track.author}`"

		if event.track.artwork_url:
			embed.set_thumbnail(url=event.track.artwork_url)
		
		embed.description += f"\n*This track was requested by <@{event.track.requester}>*" if event.track.requester else f"\n*This is an autoplay track*"

		lrclib_data = requests.get(f"https://lrclib.net/api/get?artist_name={event.track.author}&track_name={event.track.title}")

		if lrclib_data.status_code == 200:
			lrclib_data = lrclib_data.json() # contains id, trackName, artistName, albumName, duration, instrumental, plainLyrics and syncedLyrics.
			event.track.extra["albumName"] = lrclib_data["albumName"]
			event.track.extra["trackName"] = lrclib_data["trackName"]
			event.track.extra["artistName"] = lrclib_data["artistName"]
			event.track.extra["plainLyrics"] = lrclib_data["plainLyrics"] if not lrclib_data["instrumental"] else "🎼 instrumental 🎼"
		
		footerText = MusicCoreService.get_player_state(event.player)
		embed.set_footer(text=footerText)

		player.store('channel_status', f"Listening to {event.track.title}")
		voice_channel = guild.get_channel(event.player.channel_id)
		await voice_channel.set_status(player.fetch('channel_status'))
		
		await channel.send(embed=embed)


	@lavalink.listener(lavalink.TrackEndEvent)
	async def on_track_end(self, event: lavalink.TrackEndEvent):
		guild = self.bot.get_guild(event.player.guild_id)
		player: lavalink.DefaultPlayer = event.player

		voice_channel = guild.get_channel(event.player.channel_id)

		history: list = player.fetch('history')
		history.insert(0, event.track)
		
		if voice_channel.status == player.fetch('channel_status'):
			await voice_channel.set_status(None)

		if not player.queue and player.fetch('autoplay'):
			track_id: str = event.track.identifier
			await MusicCoreService.add_autoplay_track(player, track_id)


	@lavalink.listener(lavalink.TrackStuckEvent)
	async def on_track_stuck(self, event: lavalink.TrackStuckEvent):
		pass


	@lavalink.listener(lavalink.TrackExceptionEvent)
	async def on_track_exception(self, event: lavalink.TrackExceptionEvent):
		pass


	@lavalink.listener(lavalink.TrackLoadFailedEvent)
	async def on_track_load_failed(self, event: lavalink.TrackLoadFailedEvent):
		pass

	
	@lavalink.listener(lavalink.QueueEndEvent)
	async def on_queue_end(self, event: lavalink.QueueEndEvent):
		guild_id = event.player.guild_id
		guild = self.bot.get_guild(guild_id)

		if guild is not None and not event.player.fetch('autoplay'):
			await guild.voice_client.disconnect(force=True)
	

	@lavalink.listener(lavalink.PlayerUpdateEvent)
	async def on_player_update(self, event: lavalink.PlayerUpdateEvent):
		pass


	@lavalink.listener(lavalink.PlayerErrorEvent)
	async def on_player_error(self, event: lavalink.PlayerErrorEvent):
		pass


	@lavalink.listener(lavalink.NodeConnectedEvent)
	async def on_node_connected(self, event: lavalink.NodeConnectedEvent):
		pass


	@lavalink.listener(lavalink.NodeDisconnectedEvent)
	async def on_node_disconnected(self, event: lavalink.NodeDisconnectedEvent):
		pass


	@lavalink.listener(lavalink.NodeReadyEvent)
	async def on_node_ready(self, event: lavalink.NodeReadyEvent):
		print(f"Node with session ID {event.node.session_id} has connected")
		print(f"Resumed session: {event.resumed}")


	@lavalink.listener(lavalink.NodeChangedEvent)
	async def on_node_changed(self, event: lavalink.NodeChangedEvent):
		pass


	@lavalink.listener(lavalink.IncomingWebSocketMessage)
	async def on_incoming_websocket_message(self, event: lavalink.IncomingWebSocketMessage):
		pass


	@lavalink.listener(lavalink.WebSocketClosedEvent)
	async def on_websocket_closed(self, event: lavalink.WebSocketClosedEvent):
		pass


def setup(bot: discord.Bot):
	bot.add_cog(LavaPlayer(bot))

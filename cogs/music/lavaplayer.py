# loading lavalink credentials from .env
import os
from dotenv import load_dotenv

import aiohttp
import asyncio

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
	

	async def empty_channel_timeout(self, player: lavalink.DefaultPlayer, msg: str):
		"""
		"""
		guild = self.bot.get_guild(player.guild_id)
		text_channel = guild.get_channel(player.fetch('channel'))
		voice_channel = guild.get_channel(player.channel_id)
		try:
			await text_channel.send(f"{msg} Leaving after a timeout of 2 minutes.")
			await asyncio.sleep(120)
			await MusicCoreService.disconnect_chores(self.bot, player)
			await guild.voice_client.disconnect(force=True)
			await text_channel.send(f"{self.bot.user.name} has gracefully left the stage. See you next time.")
		except asyncio.CancelledError:
			pass # if cancelled, do nothing (maybe do something someday, but for now, nothing comes to mind.)
	

	async def inactive_player_timeout(self, player: lavalink.DefaultPlayer):
		"""
		"""
		guild = self.bot.get_guild(player.guild_id)
		text_channel = guild.get_channel(player.fetch('channel'))
		try:
			await text_channel.send(f"Player is idle. Leaving after a timeout of 2 minutes.")
			await asyncio.sleep(120)
			await MusicCoreService.disconnect_chores(self.bot, player)
			await guild.voice_client.disconnect(force=True)
			await text_channel.send(f"{self.bot.user.name} has gracefully left the stage. See you next time.")
		except asyncio.CancelledError:
			pass

	

	@discord.Cog.listener()
	async def on_voice_state_update(self, member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
		"""
		"""
		# this event is currently being used to check if there are any users in the voice channel
		# that the player is connected to.
		# if there are no users in the voice channel, we start a 2 minute countdown
		# and if no user joins within 2 minutes, the player disconnects

		# if the member is a bot, do nothing
		if member.bot:
			return
		
		# return if both before and after have the same channel (meaning no user left or joined a voice channel)
		if before.channel == after.channel:
			return

		if not hasattr(self.bot, "lavalink"):
			return
		
		player: lavalink.DefaultPlayer = self.bot.lavalink.player_manager.get(member.guild.id)
		if not player: # if voice client is not connected
			# TODO
			return
		
		if player.fetch("inactive_player_timeout_task"):
			return
		
		guild = self.bot.get_guild(player.guild_id)
		text_channel = guild.get_channel(player.fetch('channel'))
		player_channel = guild.get_channel(player.channel_id)

		if not player_channel:
			return
		
		if before.channel == player_channel: # member has left the channel
			if not False in [member.bot for member in player_channel.members]: # if the channel is inactive (if all members are bots)
				msg = "" # the message to send
				if player.is_playing and not player.paused: # if the player is in the middle of playing a track
					await player.set_pause(True) # pause the player
					msg += "Playback paused." # notify in a message
				if len(player_channel.members) > 1: # if there are other bots in the channel
					msg += f" The bots are now conspiring to take over <#{player.channel_id}>."
				else: # if the bot is alone in the channel
					msg += f" {self.bot.user.name} is alone in <#{player.channel_id}>."

				empty_channel_timeout_task = asyncio.create_task(self.empty_channel_timeout(player, msg))
				player.store("empty_channel_timeout_task", empty_channel_timeout_task)
		
		elif after.channel == player_channel: # member has joined the channel
			empty_channel_timeout_task: asyncio.Task = player.fetch("empty_channel_timeout_task")
			if not empty_channel_timeout_task:
				return
			
			if not empty_channel_timeout_task.done(): # if a member joins the channel before timeout is done
				msg = ""
				empty_channel_timeout_task.cancel() # cancel the task
				if player.is_playing: # if player was playing
					await player.set_pause(False) # resume it
					msg += "Playback resumed."
				
				await text_channel.send(f"Timeout cancelled. {msg}") # notify in a message
			player.store("empty_channel_timeout_task", None) 
		

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
		
		history: list = player.fetch("history")
		history.insert(0, event.track)

		add_autoplay_track_task: asyncio.Task = asyncio.create_task(MusicCoreService.add_autoplay_track(player, event.track.identifier))
		
		embed: discord.Embed = discord.Embed(title="Now Playing")
		embed.description = f"**[{event.track.title}]({event.track.uri})** by `{event.track.author}`"

		if event.track.artwork_url:
			embed.set_thumbnail(url=event.track.artwork_url)
		
		embed.description += f"\n*This track was requested by <@{event.track.requester}>*" if event.track.requester else f"\n*This is an autoplay track*"
		
		footerText = MusicCoreService.get_player_state(event.player)
		embed.set_footer(text=footerText)

		player.store('channel_status', f"Listening to {event.track.title}")
		voice_channel = guild.get_channel(event.player.channel_id)
		await voice_channel.set_status(player.fetch('channel_status'))
		
		await channel.send(embed=embed)

		if "plainLyrics" in event.track.extra.keys():
			return

		try:
			async with self.bot.session.get(f"https://lrclib.net/api/get?artist_name={event.track.author}&track_name={event.track.title}") as response:
				
				if response.status == 200:
					lrclib_data = await response.json()
					event.track.extra["albumName"] = lrclib_data["albumName"]
					event.track.extra["trackName"] = lrclib_data["trackName"]
					event.track.extra["artistName"] = lrclib_data["artistName"]
					event.track.extra["plainLyrics"] = lrclib_data["plainLyrics"] if not lrclib_data["instrumental"] else "🎼 instrumental 🎼"
		
		except aiohttp.ClientConnectionError as e:
			print(f"Connection Error: Check if your internet or the site is down.\n{e}")
		except aiohttp.ClientSSLError as e:
			print(f"SSL/Certificate Error:\n{e}")
		except asyncio.TimeoutError:
			print(f"The API took too long to respond.\n{e}")
		except Exception as e:
			print(f"Lyrics could not be retrieved\n{e}")


	@lavalink.listener(lavalink.TrackEndEvent)
	async def on_track_end(self, event: lavalink.TrackEndEvent):
		guild = self.bot.get_guild(event.player.guild_id)
		player: lavalink.DefaultPlayer = event.player

		
		voice_channel = guild.get_channel(event.player.channel_id)

		if voice_channel.status == player.fetch('channel_status'):
			await voice_channel.set_status(None)

		if player.fetch("autoplay") and not player.queue and not player.is_playing:
			asyncio.create_task(MusicCoreService.add_autoplay_track_to_queue(player))


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
		player: lavalink.DefaultPlayer = event.player

		if guild is not None and not player.fetch('autoplay'):
			inactive_player_timeout_task = asyncio.create_task(self.inactive_player_timeout(event.player))
			player.store("inactive_player_timeout_task", inactive_player_timeout_task)
	

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

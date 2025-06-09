import discord
import lavalink


class LavalinkVoiceClient(discord.VoiceProtocol):
	"""
	This is the preferred way to handle external voice sending
	This client will be created via a cls in the connect method of the channel
	See the following documentation:
	https://discordpy.readthedocs.io/en/latest/api.html#voiceprotocol
	"""


	def __init__(self, client: discord.Client, channel: discord.abc.Connectable):
		self.client = client
		self.channel = channel
		self.guild_id = channel.guild.id
		self._destroyed = False

		if not hasattr(self.client, 'lavalink'):
			# Instantiate a client if one doesn't exist
			# We store it in `self.client` so that it may persist across cog reloads,
			# however this is not mandatory
			self.client.lavalink = lavalink.Client(client.user.id)
			self.client.lavalink.add_node(
				host='192.168.1.234',
				port='2333',
				password='youshallnotpass',
				region='bd',
				name='default-node'
			)
		
		# Create a shortcut to the Lavalink client here.
		self.lavalink = self.client.lavalink
	

	async def on_voice_server_update(self, data):
		# the data needs to be transformed before being handed down to voice_update_handler
		lavalink_data = {
			't': 'VOICE_SERVER_UPDATE',
			'd': data
		}
		await self.lavalink.voice_update_handler(lavalink_data)
	

	async def on_voice_state_update(self, data):
		channel_id = data['channel_id']

		if not channel_id:
			await self._destroy()
			return
		
		self.channel = self.client.get_channel(int(channel_id))

		# the data needs to be transformed before being handed down to voice_update_handler
		lavalink_data = {
			't': 'VOICE_STATE_UPDATE',
			'd': data
		}

		await self.lavalink.voice_update_handler(lavalink_data)
	

	async def connect(self, *, timeout: float, reconnect: bool, self_deaf: bool = False, self_mute: bool = False) -> None:
		"""
		Connect the bot to the voice channel and create a player_manager if it doesn't exist yet.
		"""
		# ensure there is a plater_manager when creating a new voice_client
		self.lavalink.player_manager.create(guild_id=self.channel.guild.id)
		await self.channel.guild.change_voice_state(channel=self.channel, self_mute=self_mute, self_deaf=self_deaf)
	

	async def disconnect(self, *, force: bool = False) -> None:
		"""
		Handles the disconnect.
		Cleans up running player and leaves the voice client.
		"""
		player = self.lavalink.player_manager.get(self.channel.guild.id)

		# no need to disconnect if we are not connected
		if not force and not player.is_connected:
			return
		
		# None means disconnect
		await self.channel.guild.change_voice_state(channel=None)

		# update the channel_id of the player to None
		# this must be done because the on_voice_state_update that would set channel_id
		# to None doesn't get dispatched after the disconnect
		player.channel_id = None
		await self._destroy()
	

	async def _destroy(self):
		self.cleanup()

		if self._destroyed:
			# Idempotency handling, if `disconnect()` is called, the changed voice state
			# could cause this to run a second time.
			return
		
		self._destroyed = True

		try:
			await self.lavalink.player_manager.destroy(self.guild_id)
		except lavalink.ClientError:
			pass

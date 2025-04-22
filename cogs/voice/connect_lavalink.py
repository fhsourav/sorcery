import os

import discord

import wavelink


class ConnectLavalink(discord.Cog):
	"""
	A Discord Cog for managing Lavalink connections and node events.

	This cog handles the connection to Lavalink nodes for music playback functionality,
	including initialization, connection management, and event handling for node status changes.
	"""

	def __init__(self, bot: discord.Bot):
		self.bot = bot

	async def connect_nodes(self):
		"""Connect to Lavalink nodes.

		This method establishes connections to the configured Lavalink nodes for audio streaming.
		It waits for the bot to be ready before attempting to connect.

		The node configuration includes:
		- A random unique identifier
		- URI from environment variable LAVALINK_SERVER_ADDRESS
		- Password from environment variable LAVALINK_SERVER_PASSWORD
		- Inactive player timeout of 120 seconds
		The connection is made with a cache capacity of 100 (experimental feature).
		"""
		await self.bot.wait_until_ready() # wait until the bot is ready

		nodes = [
			wavelink.Node(
				identifier=None, # this identifier must be unique for all the nodes; pass None to generate a random one on creation
				uri=os.getenv("LAVALINK_SERVER_ADDRESS"), # for the uri, protocol (http/s) is required, port must be what Lavalink uses. e.g. http://0.0.0.0:2333
				password=os.getenv("LAVALINK_SERVER_PASSWORD"), # password of the lavalink server. check environment variables or application.yml file
				
				# starts when a track ends (at least one track has to be played)
				inactive_player_timeout=120, # 2 minutes (120 seconds); Setting the value to `None` disables the check
			)
		]

		# cache_capacity is EXPERIMENTAL. Turn it off by passing None
		await wavelink.Pool.connect(nodes=nodes, client=self.bot, cache_capacity=100) # Connect the nodes

	
	@discord.Cog.listener()
	async def on_ready(self):
		"""
		Event handler that triggers when the bot becomes ready.

		This method executes when the Discord bot has successfully connected and is ready
		to receive commands. It automatically connects to configured Lavalink nodes for
		music functionality.
		"""
		await self.connect_nodes() # Connect to the lavalink server

	
	@discord.Cog.listener()
	async def on_shutdown(self):
		"""
		Handles the shutdown process for Lavalink connection.

		This coroutine is called when the bot is shutting down. It ensures proper cleanup
		by closing all connected Lavalink nodes and terminating audio connections.
		"""
		print("Closing connected Lavalink Nodes.")
		await wavelink.Pool.close()

	
	@discord.Cog.listener()
	async def on_wavelink_node_ready(self, payload: wavelink.NodeReadyEventPayload):
		"""
		Event handler for when a Wavelink node becomes ready.

		This method is triggered whenever a Wavelink node successfully connects to the bot.
		It prints connection details including the node identifier and session resume status.

		Params:
			payload (wavelink.NodeReadyEventPayload): The payload containing information about the connected node

		Returns:
			None
		"""
		print(f"Node with ID {payload.node.identifier} has connected")
		print(f"Resumed session: {payload.resumed}")

	
	@discord.Cog.listener()
	async def on_wavelink_node_closed(self, node: wavelink.Node, disconnected: list[wavelink.Player]):
		"""
		Event handler triggered when a Wavelink node is closed.

		Params:
			node (wavelink.Node): The Wavelink node that was closed.
			disconnected (list[wavelink.Player]): A list of players that were disconnected 
			as a result of the node closure.

		This method is called automatically by the Wavelink library whenever a node
		is closed. It can be used to handle cleanup or logging related to the node
		closure.
		"""
		print(f"Node with ID {node.identifier} has closed.")


def setup(bot: discord.Bot):
	bot.add_cog(ConnectLavalink(bot))

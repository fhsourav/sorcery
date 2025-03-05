import os

import discord

import wavelink


class ConnectLavalink(discord.Cog):
	"""This cog connects to the lavalink server."""

	def __init__(self, bot: discord.Bot):
		self.bot = bot

	async def connect_nodes(self):
		"""Connect to Lavalink nodes."""
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
		"""When the bot is ready."""
		await self.connect_nodes() # Connect to the lavalink server

	
	@discord.Cog.listener()
	async def on_shutdown(self):
		"""Closing the bot"""
		print("Closing connected Lavalink Nodes.")
		await wavelink.Pool.close()

	
	@discord.Cog.listener()
	async def on_wavelink_node_ready(self, payload: wavelink.NodeReadyEventPayload):
		"""Everytime a node is successfully connected."""

		print(f"Node with ID {payload.node.identifier} has connected")
		print(f"Resumed session: {payload.resumed}")

	
	@discord.Cog.listener()
	async def on_wavelink_node_closed(self, node: wavelink.Node, disconnected: list[wavelink.Player]):
		"""Everytime a node is closed."""
		print(f"Node with ID {node.identifier} has closed.")


def setup(bot: discord.Bot):
	bot.add_cog(ConnectLavalink(bot))

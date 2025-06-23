import asyncio
import signal

import discord


class SorceryBot(discord.Bot):
	"""
	A subclass of `discord.Bot` that provides additional functionality for handling
	graceful shutdowns and custom events.
	"""

	inactive_timeout = 120 # The timeout duration for inactivity (in seconds).

	
	def __init__(self, *args, **kwargs):
		"""
		Initializes the bot instance and sets up signal handlers for graceful shutdown.
		"""
		super().__init__(*args, **kwargs)
		self.add_listener(self.on_shutdown)
		
		for signame in ("SIGINT", "SIGTERM"):
			self.loop.add_signal_handler(
				getattr(signal, signame),
				lambda: asyncio.ensure_future(self.close())
			)
	

	async def on_ready(self):
		"""
		Event hadler that is triggered when the bot is ready.
		"""
		print(f"Logged in as {self.user} (ID: {self.user.id})")
		print("----------")
	

	async def close(self):
		"""
		Gracefully shuts down the bot.
		
		This methoud triggers the `shutdown` event, waits for 10 seconds to allow any on_shutdown
		tasks to complete, and then proceeds to close the bot connection.
		"""
		self.dispatch("shutdown") # triggers `on_shutdown`
		await asyncio.sleep(2) # sleep to let `on_shutdown` to complete
		print("shutting down gracefully.")
		print("----------")
		return await super().close()
	

	async def on_shutdown(self):
		"""
		Handles the shutdown event for the bot.

		I think this method here might be unnecessary.
		"""
		pass

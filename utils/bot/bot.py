import asyncio
import signal

import discord


class SorceryBot(discord.Bot): # subclass discord.Bot
	"""
	A subclass of `discord.Bot` that provides additional functionality for handling
	graceful shutdowns and custom events.
	"""


	inactive_timeout = 120 # The timeout duration (in seconds) for inactivity.


	def __init__(self, *args, **kwargs):
		"""
		Initializes the bot instance and sets up signal handlers for graceful shutdown.

		Params:
			*args: Variable length argument list passed to the parent class initializer.
			**kwargs: Arbitrary keyword arguments passed to the parent class initializer.

		This constructor performs the following:
		- Calls the parent class initializer with the provided arguments.
		- Adds a listener for the `on_shutdown` event.
		- Registers signal handlers for `SIGINT` and `SIGTERM` to ensure the bot
		  shuts down gracefully when these signals are received.
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
		Event handler that is triggered when the bot is ready.

		This method is called automatically by the Discord client when the bot has successfully connected
		to Discord and is ready to operate. It logs the bot's username and ID to the console for verification.
		"""
		print(f"Logged in as {self.user} (ID: {self.user.id})")
		print("----------")
	

	async def close(self):
		"""
		Gracefully shuts down the bot.

		This method triggers the "shutdown" event, waits for 10 seconds to allow
		any on_shutdown tasks to complete, and then proceeds to close the bot
		connection.

		Returns:
			Coroutine: The coroutine returned by the superclass's close method.
		"""
		self.dispatch("shutdown") # triggering on_close
		await asyncio.sleep(10) # need to sleep because on_shutdown codes not running since the bot is disconnecting
		print("Shutting down gracefully.")
		print("----------")
		return await super().close()
	

	async def on_shutdown(self):
		"""
		Handles the shutdown event for the bot.

		This method is triggered when the bot is closed using `ctrl + c`. 
		Currently, it is overridden in the subclass, and due to being 
		triggered twice, no specific actions are performed here.

		Note:
			Subclasses should implement their own shutdown logic if needed.
		"""
		pass # for some reason, this is being triggered twice from the subclass, so not doing anything here.

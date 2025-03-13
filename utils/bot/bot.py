import asyncio
import signal

import discord


class SorceryBot(discord.Bot): # subclass discord.Bot


	inactive_timeout = 120


	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.add_listener(self.on_shutdown)
		for signame in ("SIGINT", "SIGTERM"):
			self.loop.add_signal_handler(
				getattr(signal, signame),
				lambda: asyncio.ensure_future(self.close())
			)


	async def on_ready(self):
		"""Prints an on_ready message on the console."""
		print(f"Logged in as {self.user} (ID: {self.user.id})")
		print("----------")
	

	async def close(self):
		"""Graceful shutdown."""
		self.dispatch("shutdown") # triggering on_close
		await asyncio.sleep(10) # need to sleep because on_shutdown codes not running since the bot is disconnecting
		print("Shutting down gracefully.")
		print("----------")
		return await super().close()
	

	async def on_shutdown(self):
		"""
		A custom event which triggers when the bot is closed with `ctrl + c`.
		"""
		pass # for some reason, this is being triggered twice from the subclass, so not doing anything here.

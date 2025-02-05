import discord


class SorceryBot(discord.Bot): # subclass discord.Bot

	async def on_ready(self):
		"""Prints an on_ready message on the console."""
		print(f"Logged in as {self.user} (ID: {self.user.id})")
		print("----------")
	

	async def close(self):
		"""Graceful shutdown."""
		print("Shutting down gracefully.")
		print("----------")
		return await super().close()

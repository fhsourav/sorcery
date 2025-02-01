import asyncio

import discord
from discord.ext import commands


class Basic(discord.Cog, name="Basic Slash Commands Cog"):
	"""Basic Cog"""

	# custom emoji allowed types
	allowed_content_types = [
		"image/jpeg",
		"image/png",
	]

	def __init__(self, bot: discord.Bot):
		self.bot = bot

	
	@discord.slash_command()
	@discord.option(
		name="user",
		description="Recipient"
	)
	async def hello(self, ctx: discord.ApplicationContext, user: discord.Member = None):
		"""Says 'Hello!'"""
		if not user:
			await ctx.respond(f"Hello!")
		else:
			await ctx.respond(f"Hello {user.mention}")

	
	@discord.slash_command()
	@discord.option(
		name="left",
		description="The first number"
	)
	@discord.option(
		name="right",
		description="The second number"
	)
	async def add(self, ctx: discord.ApplicationContext, left: int, right: int):
		"""Adds two numbers together."""
		await ctx.respond(str(left + right))
	

	@discord.slash_command()
	@discord.option(
		name="user",
		description="User"
	)
	async def userinfo(self, ctx: discord.ApplicationContext, user: discord.Member):
		"""Gives information of an user."""
		await ctx.respond(f"User ID: {user.id}\nUsername: {user.name}\nJoined at {user.joined_at}\n{user.display_avatar.url}")

	
	@discord.slash_command()
	@discord.option(
		name="value",
		description="Choose a value",
		choices=[1, 2, 3]
	)
	async def choose(self, ctx: discord.ApplicationContext, value: int):
		"""Choose between 1, 2 and 3."""
		await ctx.respond(f"You chose: {value}!")
	

	@discord.slash_command()
	@discord.option(
		name="seconds",
		description="Seconds to wait for",
		choices=range(1, 11)
	)
	async def wait(self, ctx: discord.ApplicationContext, seconds: int = 5):
		"""Wait a few seconds."""
		await ctx.defer()
		await asyncio.sleep(seconds)
		await ctx.respond(f"Waited for {seconds} seconds!")

	
	@discord.slash_command()
	async def add_private_emoji(self, ctx: discord.ApplicationContext, name: str, image: discord.Attachment, role: discord.Role):
		"""Adds a private emoji to the server."""
		if image.content_type not in self.allowed_content_types:
			return await ctx.respond("Invalid attachment type!", ephemeral=True)
		
		image_file = await image.read() # Reading attachment's content to get bytes

		await ctx.guild.create_custom_emoji(
			name=name, image=image_file, roles=[role]
		) # Image argument only takes bytes!

		await ctx.respond("Private emoji is successfully created.")

	
	@discord.slash_command()
	@commands.cooldown(
		1, 5, commands.BucketType.user
	)
	async def cooldown(self, ctx: discord.ApplicationContext):
		"""This command has a five second cooldown."""
		await ctx.respond("You can use this command again in 5 seconds.")

	
	# Dynamic cooldown example (notice that "self" is not necessary here)
	def decide_cooldown(message: discord.Message):
		if message.author.id % 2 == 0:
			return commands.Cooldown(1, 5)
		else:
			return commands.Cooldown(1, 10)
	

	@discord.slash_command()
	@commands.dynamic_cooldown(decide_cooldown, commands.BucketType.user)
	async def dynamic(self, ctx: discord.ApplicationContext):
		"""Dynamic cooldown example."""
		await ctx.respond("You can use this command again soon.")

	
	@commands.Cog.listener()
	async def on_application_command_error(self, ctx: discord.ApplicationContext, error: discord.DiscordException):
		"""Application command error handler."""
		if isinstance(error, commands.CommandOnCooldown):
			await ctx.respond("This command is currently on cooldown.", ephemeral=True)
		else:
			raise error


def setup(bot: discord.Bot):
	bot.add_cog(Basic(bot))

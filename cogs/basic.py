import asyncio

import discord
from discord.ext import commands


class Basic(commands.Cog, name="Basic Commands Cog"):
	"""Basic Cog"""

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


def setup(bot: discord.Bot):
	bot.add_cog(Basic(bot))

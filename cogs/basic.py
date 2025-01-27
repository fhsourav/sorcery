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


def setup(bot: discord.Bot):
	bot.add_cog(Basic(bot))

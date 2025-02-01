from typing import Union

import discord
from discord.ext import commands

class Secret(commands.Cog, command_attrs=dict(hidden=True)):

	def __init__(self, bot: discord.Bot):
		self.bot = bot

	# @discord.Bot.group(hidden=True)
	# async def secret(self, ctx: commands.Context):
	# 	"""What is this "secret" you speak of?"""
	# 	if ctx.invoked_subcommand is None:
	# 		await ctx.send("Shh!", delete_after=5)

	secret = discord.SlashCommandGroup(name="secret", description="What is this 'secret' you speak of?")


	def create_overwrites(self, ctx: discord.ApplicationContext, obj: Union[discord.Role, discord.Member]):
		"""
		This is just a helper function that creates the overwrites for the voice/text channels.

		A `discord.PermissionOverwrite` allows you to determine the permissions of an object,
		whether it be a `discord.Role` or a `discord.Member`.

		In this case, the `view_channel permission is being used to hide the channel from being
		viewed by whoever does not meet the criteria, thus creating a secret channel.
		"""

		# A dict comprehension is being utilized here to set the same permission overwrites for
		# each `discord.Role` or `discord.Member`
		overwrites = {
			obj: discord.PermissionOverwrite(view_channel=True)
		}

		# Prevents the default role (@everyone) from viewing the channel
		# if it isn't already allowed to view the channel
		overwrites.setdefault(
			ctx.guild.default_role, discord.PermissionOverwrite(view_channel=False)
		)

		# Makes sure the client is always allowed to view the channel.
		overwrites[ctx.guild.me] = discord.PermissionOverwrite(view_channel=True)

		return overwrites
	
	
	# Since these commands rely on guild related features,
	# it is best to lock it to be guild-only.
	@secret.command()
	@commands.guild_only()
	async def text(
		self,
		ctx: discord.ApplicationContext,
		name: str,
		obj: Union[discord.Role, discord.Member],
	):
		"""
		This makes a text channel with the passed name that is only visible to specified roles or members.
		"""

		overwrites = self.create_overwrites(ctx, obj)

		await ctx.guild.create_text_channel(
			name,
			overwrites=overwrites,
			topic=(
				"Top secret text channel. Any leakage of this channel may result in trouble."
			),
			reason="Very secret business.",
		)

		await ctx.respond("Channel created", ephemeral=True)

def setup(bot: discord.Bot):
	bot.add_cog(Secret(bot))

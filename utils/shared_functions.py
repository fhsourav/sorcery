"""
Common functionalities that are shared by two or more cog functions.
"""


from typing import cast

import discord

import wavelink


def milli_to_minutes(milli: int) -> str:
	"""from milliseconds to understandable output."""
	seconds = (milli // 1000) % 60
	minutes = milli // (1000 * 60)
	return f"{minutes:02}:{seconds:02}"


async def check_voice(ctx: discord.ApplicationContext, player: wavelink.Player):
	"""
	Checks if the bot is connected to a voice channel
	Also checks if the user is connected to the same voice channel
	"""

	if not player:
		await ctx.respond("The bot is not connected to a voice channel.")
		return False
	
	if ctx.author.voice is None or ctx.author.voice.channel != player.channel:
		await ctx.respond(f"Please join {player.channel.name} to use this command.")
		return False
	
	return True


async def join_voice(ctx: discord.ApplicationContext):
	"""
	Join a voice channel.
	"""
	# First we may define our voice client,
	# for this, we are going to use typing.cast()
	# function just for the type checker know that
	# `ctx.voice_client` is going to be from type
	# `wavelink.Player`
	player: wavelink.Player = cast(wavelink.Player, ctx.voice_client) # type: ignore

	if not player: # We firstly check if there is a voice client
		try:
			player = await ctx.author.voice.channel.connect(cls=wavelink.Player) # If there isn't, we connect it to the channel
		except AttributeError:
			await ctx.respond("Please join a voice channel first before using this command.")
			return player
		except discord.ClientException:
			await ctx.respond("I was unable to join this voice channel. Please try again.")
			return player

	# Lock the player to this channel...
	if not hasattr(player, "home"):
		player.home = ctx.channel
	elif player.home != ctx.channel:
		await ctx.respond(f"The bot is already connected to {player.home.mention}.")

	return player

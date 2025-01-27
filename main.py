# loading token from .env
import os
from dotenv import load_dotenv

# logging
import logging

# pycord
import discord
from discord.ext import commands

# regular expression for loading cogs
import re


# logging for discord
logger = logging.getLogger("discord")
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename="discord.log", encoding="utf-8", mode="a")
handler.setFormatter(logging.Formatter("%(asctime)s:%(levelname)s:%(name)s: %(message)s"))
logger.addHandler(handler)

# loading .env
load_dotenv()

# loading guild(server) ids from .env
debug_guilds = os.getenv("GUILD_IDS").split(",")

# loading discord_token
discord_token = os.getenv("DISCORD_TOKEN")

# loading cog_folder (if there are multiple cog folders, the way to load them has to be altered accordingly)
cog_folder = os.getenv("COG_FOLDER")

# the bot uses cogs for all the commands

description = """
A basic utility bot (for now)
"""

# intents
intents = discord.Intents.default()
intents.members = True
intents.message_content = True

# the bot
bot = discord.Bot(
	description=description,
	intents=intents,
	help_command=commands.DefaultHelpCommand(),
	debug_guilds=debug_guilds
)


@bot.event
async def on_ready():
	"""Prints an on_ready message to the console."""
	print(f"Logged in as {bot.user} (ID: {bot.user.id})")
	print("------")


@bot.listen
async def on_member_join(member: discord.Member):
	"""Sends a welcome message mentioning the newly joined member in the desired channel."""
	channel_id = -1 # change -1 to YOUR_DESIRED_CHANNEL_ID
	channel = bot.get_channel(channel_id)
	await channel.send(f"Welcome to the server {member.mention}!")


# loading cogs (if there are multiple cog folders, the way to load them has to be altered accordingly)
pattern = r"(.+)(\.py)"
for filename in os.listdir(cog_folder):
	match = re.fullmatch(pattern, filename)
	if match:
		bot.load_extension(f"{cog_folder}.{match[1]}")

# running the bot
bot.run(discord_token)

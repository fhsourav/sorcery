# loading token from .env
import os
from dotenv import load_dotenv

# logging
import logging

# pycord
import discord

from src import SorceryBot


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
An all-in-one bot.
"""

# intents
intents = discord.Intents.default()

# the bot
bot = SorceryBot(
	description=description,
	intents=intents,
	debug_guilds=debug_guilds
)

# loading cogs (if there are multiple cog folders, the way to load them has to be altered accordingly)
for (root, dirs, files) in os.walk(cog_folder):
	dotpath = root.replace(os.sep, ".")
	for file in files:
		name, ext = os.path.splitext(file)
		if ext == ".py":
			bot.load_extension(f"{dotpath}.{name}")

# running the bot
bot.run(discord_token)

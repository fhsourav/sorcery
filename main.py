# loading token from .env
import os
from dotenv import load_dotenv

# logging
import logging

# pycord
import discord

# importing the subclassed bot
from utils.bot import SorceryBot


# logging for discord
logger = logging.getLogger("discord")
logger.setLevel(logging.INFO)
handler = logging.FileHandler(filename="discord.log", encoding="utf-8", mode="a")
handler.setFormatter(logging.Formatter("%(asctime)s:%(levelname)s:%(name)s: %(message)s"))
logger.addHandler(handler)

# loading .env
load_dotenv()

# loading discord_token
discord_token = os.getenv("DISCORD_TOKEN")

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
)

# loading cogs (if there are multiple cog folders, the way to load them has to be altered accordingly)
for (root, dirs, files) in os.walk("cogs"):
	dotpath = root.replace(os.sep, ".")
	for file in files:
		name, ext = os.path.splitext(file)
		if ext == ".py":
			bot.load_extension(f"{dotpath}.{name}")

# running the bot
bot.run(discord_token)

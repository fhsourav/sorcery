# loading token from .env
import os
from dotenv import load_dotenv

# logging
import logging

# pycord
import discord

# for both slash commands and prefix commands
from discord.ext import bridge

# logging for discord
logger = logging.getLogger("discord")
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename="discord.log", encoding="utf-8", mode="a")
handler.setFormatter(logging.Formatter("%(asctime)s:%(levelname)s:%(name)s: %(message)s"))
logger.addHandler(handler)

# loading .env
load_dotenv()

# loading guild/server ids from .env
guild_ids = os.getenv("GUILD_IDS").split(",")

# loading discord_token
discord_token = os.getenv("DISCORD_TOKEN")

# the code below is for testing. it's a basic bot with a simple command, !hello or /hello

# intents
intents = discord.Intents.default()
intents.message_content = True

# bridge bot for slash command and prefix command
bot = bridge.Bot(command_prefix="!", intents=intents)

# guild_ids field required to register the slash command
@bot.bridge_command(guild_ids=guild_ids, name="hello")
async def hello(ctx):
	await ctx.respond("Hello!")

# running the bot
bot.run(discord_token)

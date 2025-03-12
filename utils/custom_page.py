import discord
from discord.ext import pages

class CustomPage():

	BUTTONS = [
		pages.PaginatorButton("first", label="<<", style=discord.ButtonStyle.secondary),
		pages.PaginatorButton("prev", label="<", style=discord.ButtonStyle.secondary),
		pages.PaginatorButton("page_indicator", style=discord.ButtonStyle.primary, disabled=True),
		pages.PaginatorButton("next", label=">", style=discord.ButtonStyle.secondary),
		pages.PaginatorButton("last", label=">>", style=discord.ButtonStyle.secondary),
	]

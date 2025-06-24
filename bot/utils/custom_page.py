import discord
from discord.ext import pages


class CustomPage():
	"""
	CustomPage class provides a structure for creating a custom paginator with predefined buttons.

	Attributes:
		BUTTONS (list): A list of `PaginatorButton` objects used to navigate through pages.
			- "first": Navigates to the first page.
			- "prev": Navigates to the previous page.
			- "page_indicator": Displays the current page number (disabled by default).
			- "next": Navigates to the next page.
			- "last": Navigates to the last page.
	"""
	
	BUTTONS = [
		pages.PaginatorButton("first", label="<<", style=discord.ButtonStyle.secondary),
		pages.PaginatorButton("prev", label="<", style=discord.ButtonStyle.secondary),
		pages.PaginatorButton("page_indicator", style=discord.ButtonStyle.primary, disabled=True),
		pages.PaginatorButton("next", label=">", style=discord.ButtonStyle.secondary),
		pages.PaginatorButton("last", label=">>", style=discord.ButtonStyle.secondary),
	]

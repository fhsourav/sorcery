import discord
from discord.ext import pages


class Utils():
	
	def milli_to_minutes(milli: int) -> str:
		"""
		Converts a duration from milliseconds to a formatted string in the format mm:ss.

		This function is useful for converting track lengths or other time durations 
		provided in milliseconds into a more human-readable format.

		(Wavelink track lengths are given in milliseconds.)

		Params:
			milli (int): The duration in milliseconds.

		Returns:
			str: The formatted time string in the format mm:ss, where mm represents 
				 minutes and ss represents seconds, both zero-padded to two digits.
		"""
		seconds = (milli // 1000) % 60
		minutes = milli // (1000 * 60)
		return f"{minutes:02}:{seconds:02}"


class CustomPage():
	"""
	Docstring for CustomPage
	"""
	BUTTONS = [
		pages.PaginatorButton("first", label="<<", style=discord.ButtonStyle.secondary),
		pages.PaginatorButton("prev", label="<", style=discord.ButtonStyle.secondary),
		pages.PaginatorButton("page_indicator", style=discord.ButtonStyle.primary, disabled=True),
		pages.PaginatorButton("next", label=">", style=discord.ButtonStyle.secondary),
		pages.PaginatorButton("last", label=">>", style=discord.ButtonStyle.secondary),
	]

from typing import cast

import discord
from discord.ext import pages

import wavelink

from utils import CustomPage
from utils.music import CoreFunctions


class QueueFunctions():
	"""
	QueueFunctions

	A utility class for managing and generating paginated views of music queues in a Discord bot context. 
	This class provides functionality to process different types of queues, including the current queue, 
	queue history, autoplay queue, autoplay history, and saved playlists.
	"""


	def get_queue_paginator(ctx: discord.ApplicationContext, queue: wavelink.Queue | list, category: int):
		"""
		Generates a paginator for displaying tracks in a queue or playlist.

		Params:
			ctx (discord.ApplicationContext): The context of the issued command.
			queue (wavelink.Queue | list): The queue or saved playlist to be processed.
			category (int): Specifies the type of queue to process:
				- 0: Current queue
				- 1: Queue history
				- 2: Autoplay queue
				- 3: Autoplay history
				- 4: Playlist

		Returns:
			pages.Paginator: A paginator object containing the queue or playlist tracks.

		Notes:
			- The paginator includes metadata such as the current playing track, queue type, and additional indicators like loop and shuffle states.
			- If the queue is empty, an appropriate message is displayed based on the category.
			- For queue history and autoplay history, the queue is reversed before processing.
		"""

		description = "" # We are using the description for nowplaying and to show the kind of queue it is
		footer = None # footer includes loop and shuffle indicators
		thumbnail = None # thumbnail of nowplaying
		empty_queue_message = "" # message to show if queue/playlist is empty

		if not category == 4: # if not playlist
			player: wavelink.Player = cast(wavelink.Player, ctx.voice_client)
			footerText = CoreFunctions.get_player_state(player)
			footer = discord.EmbedFooter(text=footerText)

			if player.playing:
				description += f"### {'⏸️' if player.paused else '▶️'} Now playing\n"
				description += f"**[{player.current.title}]({player.current.uri})** by `{player.current.author}` [{CoreFunctions.milli_to_minutes(player.current.length - player.position)} *left*]\n"
				if player.current.artwork:
					thumbnail = player.current.artwork

		if category == 0:
			description += "## 📜 Queue"
			empty_queue_message = "Queue is empty."
			if player.autoplay == wavelink.AutoPlayMode.enabled:
				empty_queue_message += " Autoplay is enabled. Check `/autoplay queue`."
		elif category == 1:
			description += "## ⌛ History"
			empty_queue_message = "Player history is empty."
		elif category == 2:
			description += f"## ♾️ Autoplay Queue"
			empty_queue_message = "Autoplay queue has not yet been generated."
		elif category == 3:
			description += f"## 🛰️ Autoplay History"
			empty_queue_message = "Autoplay history is empty."
		elif category == 4:
			description += f"## 💾 Playlist" # gotta find a way to replace it with playlist name
			empty_queue_message = "Playlist is empty."
		else:
			print("Not a valid category.")
			return
		
		if queue:
			description += f"\n\t*({len(queue)} tracks)*\n"
			if category == 1 or category == 3:
				queue = reversed(queue)
		
		author = discord.EmbedAuthor(name=f"{ctx.author.nick if ctx.author.nick else ctx.author.display_name}", icon_url=ctx.author.avatar)

		embed_pages = [] # all the pages for the paginator as a list of Embed objects

		if not queue:
			embed_pages.append(discord.Embed(
				author=author,
				fields=[discord.EmbedField(name="", value=empty_queue_message, inline=False)],
				description=description,
				footer=footer,
				thumbnail=thumbnail,
			))

		# temp_page = discord.Embed()
		temp_page = [] # A page is basically a list of EmbedField objects

		for idx, item in enumerate(queue):
			if idx != 0 and idx % 10 == 0:
				embed_pages.append(discord.Embed(
					author=author,
					fields=temp_page,
					description=description,
					footer=footer,
					thumbnail=thumbnail,
				))
				temp_page = []

			trackEmbed = discord.EmbedField(name="", value=f"\n**#{idx + 1} [{item.title}]({item.uri})** by `{item.author}` [{CoreFunctions.milli_to_minutes(item.length)}]", inline=False)
			temp_page.append(trackEmbed)

		if temp_page:
			embed_pages.append(discord.Embed(
				author=author,
				fields=temp_page,
				description=description,
				footer=footer,
				thumbnail=thumbnail,
			))

		paginator = pages.Paginator(
			pages=embed_pages,
			use_default_buttons=False,
			custom_buttons=CustomPage.BUTTONS,
			disable_on_timeout=True,
			timeout=30,
		)

		return paginator

from typing import cast

import discord
from discord.ext import pages

import wavelink

from utils.music import CoreFunctions


class QueueFunctions():

	def get_queue_paginator(ctx: discord.ApplicationContext, queue: wavelink.Queue | list, category: int):
		"""
		takes a queue, returns paginator with tracks in the queue.

		params:
			ctx (discord.ApplicationContext):
			queue (wavelink.Queue | list): the queue / saved playlist that will be processed
			category (int): 0 if processing current queue; 1 if processing queue history; 2 if processing playlist
		returns:
			paginator
		"""

		description = "" # We are using the description for nowplaying and to show the kind of queue it is
		footer = None # footer includes loop and shuffle indicators
		thumbnail = None # thumbnail of nowplaying

		if not category == 2: # queue or history; not playlist
			player: wavelink.Player = cast(wavelink.Player, ctx.voice_client)
			footerText = f"{'🔁' if player.queue.mode == wavelink.QueueMode.loop_all else '🔂' if player.queue.mode == wavelink.QueueMode.loop else '🚫'} Loop: {'all' if player.queue.mode == wavelink.QueueMode.loop_all else 'one' if player.queue.mode == wavelink.QueueMode.loop else 'off'}\t\t"
			footerText += f"{'🚨' if player.volume > 100 else '🔊' if player.volume > 67 else '🔉' if player.volume > 33 else '🔈' if player.volume > 0 else '🔇'} Volume: {player.volume}\t\t"
			footerText += f"{'♾️' if player.autoplay == wavelink.AutoPlayMode.enabled else '❎'} Autoplay: {'on' if player.autoplay == wavelink.AutoPlayMode.enabled else 'off' if player.autoplay == wavelink.AutoPlayMode.partial else 'play one and stop'}"

			footer = discord.EmbedFooter(text=footerText)

			if player.playing:
				description += f"### {'⏸️' if player.paused else '▶️'} Now playing\n"
				description += f"**[{player.current.title}]({player.current.uri})** by `{player.current.author}` [{CoreFunctions.milli_to_minutes(player.current.length - player.position)} *left*]\n"
				thumbnail = player.current.artwork

		if category == 0:
			description += "## 📜 Queue"
		elif category == 1:
			description += "## ⌛ History"
		elif category == 2:
			description += f"## 💾 Playlist" # gotta find a way to replace it with playlist name
		else:
			print("Not a valid category.")
			return
		
		author = discord.EmbedAuthor(name=f"{ctx.author.nick if ctx.author.nick else ctx.author.display_name}", icon_url=ctx.author.avatar)

		embed_pages = [] # all the pages for the paginator as a list of Embed objects 

		# temp_page = discord.Embed()
		temp_page = [] # A page is basically a list of EmbedField objects

		for idx, item in enumerate(queue):

			if category == 1:
				position = idx
			else:
				position = idx + 1
			
			if position == 0:
				continue

			trackEmbed = discord.EmbedField(name="", value=f"\n**#{position} [{item.title}]({item.uri})** by `{item.author}` [{CoreFunctions.milli_to_minutes(item.length)}]", inline=False)
			temp_page.append(trackEmbed)

			if idx != 0 and idx % 9 == 0:
				embed_pages.append(discord.Embed(
					author=author,
					fields=temp_page,
					description=description,
					footer=footer,
					thumbnail=thumbnail,
				))
				temp_page = []

		if temp_page:
			embed_pages.append(discord.Embed(
				author=author,
				fields=temp_page,
				description=description,
				footer=footer,
				thumbnail=thumbnail,
			))
		
		pagebuttons = [
			pages.PaginatorButton("first", label="<<", style=discord.ButtonStyle.secondary),
			pages.PaginatorButton("prev", label="<", style=discord.ButtonStyle.secondary),
			pages.PaginatorButton("page_indicator", style=discord.ButtonStyle.primary, disabled=True),
			pages.PaginatorButton("next", label=">", style=discord.ButtonStyle.secondary),
			pages.PaginatorButton("last", label=">>", style=discord.ButtonStyle.secondary),
		]

		paginator = pages.Paginator(
			pages=embed_pages,
			use_default_buttons=False,
			custom_buttons=pagebuttons,
			disable_on_timeout=True,
			timeout=30,
		)

		return paginator

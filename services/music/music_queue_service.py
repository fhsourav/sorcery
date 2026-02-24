from typing import Union

import discord
import lavalink

from discord.ext import pages

from bot import Utils, CustomPage

from services.music.music_core_service import MusicCoreService


class MusicQueueService:
	

	async def display_queue(ctx: discord.ApplicationContext):
		player: lavalink.DefaultPlayer = ctx.bot.lavalink.player_manager.get(ctx.guild.id)

		queue: list[lavalink.AudioTrack] = player.queue

		paginator: pages.Paginator = MusicQueueService.get_queue_paginator(ctx, queue, 0)

		await paginator.respond(ctx.interaction)

	
	async def display_history(ctx: discord.ApplicationContext):
		player: lavalink.DefaultPlayer = ctx.bot.lavalink.player_manager.get(ctx.guild.id)

		history: list[lavalink.AudioTrack] = player.fetch('history')[1:]

		paginator: pages.Paginator = MusicQueueService.get_queue_paginator(ctx, history, 1)

		await paginator.respond(ctx.interaction)

	
	def get_queue_paginator(ctx: discord.ApplicationContext, queue: list[lavalink.AudioTrack], category: int):
		"""
		Docstring for get_queue_paginator

		category:
			- 0: current queue
			- 1: history
			- 2: playlist
		
		:param ctx: Description
		:type ctx: discord.ApplicationContext
		:param queue: Description
		:type queue: list
		:param category: Description
		:type category: int
		"""
		description = ""
		footer = None
		thumbnail = None
		empty_queue_message = ""

		if not category == 2: # if not playlist
			player: lavalink.DefaultPlayer = ctx.bot.lavalink.player_manager.get(ctx.guild.id)

			footerText = MusicCoreService.get_player_state(player)
			footer = discord.EmbedFooter(text=footerText)

			if player.is_playing:
				description += f"### {'⏸️' if player.paused else '▶️'} Now playing\n"
				description += f"**[{player.current.title}]({player.current.uri})** by `{player.current.author}` [{Utils.milli_to_minutes(player.current.duration - player.position)} *left*]\n"
				if player.current.artwork_url:
					thumbnail = player.current.artwork_url

		if category == 0: # current queue
			description += "## 📜 Queue"
			empty_queue_message = "Queue is empty."
			if player.fetch("autoplay"):
				empty_queue_message += " Autoplay is enabled."
		elif category == 1: # history
			description += "## ⌛ History"
			empty_queue_message = "Player history is empty."
		elif category == 2: # playlist
			description += "## 💾 Playlist"
			empty_queue_message = "Playlist is empty."
		else:
			print("Not a valid category.")
			return
		
		if queue:
			description += f"\n\t*({len(queue)} tracks)*\n"
		
		author = discord.EmbedAuthor(name=f"{ctx.author.nick if ctx.author.nick else ctx.author.display_name}", icon_url=ctx.author.avatar)

		embed_pages = [] # all the pages for the paginator as a list of Embed objects

		if not queue:
			embed_pages.append(discord.Embed(
				author=author,
				fields=[discord.EmbedField(name="", value=empty_queue_message, inline=False)],
				description=description,
				footer=footer,
				thumbnail=thumbnail
			))
		
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

			trackEmbed = discord.EmbedField(name="", value=f"\n**#{idx + 1} [{item.title}]({item.uri})** by `{item.author}` [{Utils.milli_to_minutes(item.duration)}]", inline=False)
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

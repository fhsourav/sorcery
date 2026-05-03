import discord
import lavalink

from discord.ext import pages

from bot import Utils, CustomPage

from services.music.music_core_service import MusicCoreService


class MusicQueueService:
	
	async def get_queue_paginator(ctx: discord.ApplicationContext, category: int):
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
		
		player: lavalink.DefaultPlayer = ctx.bot.lavalink.player_manager.get(ctx.guild.id)

		footerText = MusicCoreService.get_player_state(player)
		footer = discord.EmbedFooter(text=footerText)

		if player.is_playing:
			description += f"### {'⏸️' if player.paused else '▶️'} Now playing\n"
			description += f"**[{player.current.title}]({player.current.uri})** by `{player.current.author}` [{Utils.milli_to_minutes(player.current.duration - player.position)} *left*]\n"
			if player.current.artwork_url:
				thumbnail = player.current.artwork_url

		if category == 0: # current queue
			queue: list[lavalink.AudioTrack] = player.queue
			description += "## 📜 Queue"
			empty_queue_message = "Queue is empty."
			if player.fetch("autoplay"):
				empty_queue_message += " Autoplay is enabled."
		elif category == 1: # history
			if player.is_playing:
				history_idx = 1
			else:
				history_idx = 0
			queue: list[lavalink.AudioTrack] = player.fetch('history')[history_idx:]
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

		await paginator.respond(ctx.interaction)
	

	async def queue_autocomplete(self, ctx: discord.AutocompleteContext):
		if not hasattr(self.bot, 'lavalink'):
			return [
				discord.OptionChoice(
					name="Player has not been initiated.",
					value=-1,
				)
			]
		player: lavalink.DefaultPlayer = self.bot.lavalink.player_manager.get(ctx.interaction.guild.id)
		if not player.queue:
			return [
				discord.OptionChoice(
					name="Queue is empty.",
					value=-2,
				)
			]
		return [
			discord.OptionChoice(
				name=f"[{Utils.milli_to_minutes(track.duration)}] {track.title[:50]} by {track.author[:20]} ({track.source_name})",
				value=idx
			) for idx, track in enumerate(player.queue)
		]
	

	async def delete(ctx: discord.ApplicationContext, track_idx: int):
		player: lavalink.DefaultPlayer = ctx.bot.lavalink.player_manager.get(ctx.guild.id)
		track = player.queue.pop(track_idx)
		await ctx.respond(f"`{track.title}` has been deleted from queue.")
	

	async def set_loop(ctx: discord.ApplicationContext, mode: int):
		player: lavalink.DefaultPlayer = ctx.bot.lavalink.player_manager.get(ctx.guild.id)
		player.set_loop(mode)
		await ctx.respond(f"Player loop is set to `{'off' if mode == 0 else 'current track' if mode == 1 else 'all'}`.")


	async def shuffle(ctx: discord.ApplicationContext, set: bool):
		player: lavalink.DefaultPlayer = ctx.bot.lavalink.player_manager.get(ctx.guild.id)
		player.set_shuffle(set)
		await ctx.respond(f"Player shuffle is `{'enabled' if set else 'disabled'}`.")
	

	async def skipto(ctx: discord.ApplicationContext, track_idx: int):
		if track_idx == -1:
			return await ctx.respond("Player has not been initiated.", ephemeral=True)
		if track_idx == -2:
			return await ctx.respond("Player queue is empty.", ephemeral=True)
		
		player: lavalink.DefaultPlayer = ctx.bot.lavalink.player_manager.get(ctx.guild.id)

		if track_idx > len(player.queue):
			return await ctx.respond("Invalid track.", ephemeral=True)
		
		for i in range(track_idx):
			player.queue.pop(0)
		
		track_title: str = player.queue[0].title

		await player.skip()

		await ctx.respond(f"Skipped to `{track_title}`.")

	
	async def clear_queue(ctx: discord.ApplicationContext):
		player: lavalink.DefaultPlayer = ctx.bot.lavalink.player_manager.get(ctx.guild.id)
		player.queue.clear()
		await ctx.respond("Player queue has been cleared.")

	
	async def clear_history(ctx: discord.ApplicationContext):
		player: lavalink.DefaultPlayer = ctx.bot.lavalink.player_manager.get(ctx.guild.id)
		player.fetch("history").clear()
		await ctx.respond("Player history has been cleared.")

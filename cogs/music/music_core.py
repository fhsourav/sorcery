import re

import discord
import lavalink

from discord.ext import commands

from services.music_service import MusicService

url_rx = re.compile(r'https?://(?:www\.)?.+')


class MusicCore(discord.Cog):

	def __init__(self, bot: discord.Bot):
		self.bot = bot


	@discord.command(aliases=['p'])
	@commands.check(MusicService.create_player)
	async def play(self, ctx: discord.ApplicationContext, *, query: str):
		"""
		Searches and plays a song from a given query.
		"""
		# Get the player for this gild from cache.
		player = self.bot.lavalink.player_manager.get(ctx.guild.id)
		# Remove leading and trailing <>. <> may be used to suppress embedding links in Discord.
		query = query.strip('<>')

		# Check if the user input might be a URL. If it isn't, we can Lavalink do a YouTube search for it instead.
		# SoundCloud searching is possible by prefixing "scsearch:" instead.
		if not url_rx.match(query):
			query = f'ytsearch:{query}'
		
		# Get the results for the query from Lavalink.
		results = await player.node.get_tracks(query)

		embed = discord.Embed(color=discord.Color.blurple())

		# Valid load_types are:
		# 	TRACK		- direct URL to a track
		# 	PLAYLIST	- direct URL to playlist
		# 	SEARCH		- query prefixed with either "ytsearch:" or "scsearch:". This could possibly be expanded with plugins.
		# 	EMPTY		- no results for the query (result.tracks will be empty)
		# 	ERROR		- the track encountered an exception during loading
		if results.load_type == lavalink.LoadType.EMPTY:
			return await ctx.respond("I couldn't find any tracks for that query.")
		elif results.load_type == lavalink.LoadType.PLAYLIST:
			tracks = results.tracks

			# Add all of the tracks from the playlist to the queue.
			for track in tracks:
				# requester isn't necessary but it helps keep track of who queued what.
				# You can store additional metadata by passing it as a kwarg (i.e. key=value)
				player.add(track=track, requester=ctx.author.id)
			
			embed.title = 'Playlist Enqueued!'
			embed.description = f'{results.playlist_info.name} - {len(tracks)} tracks'
		else:
			track = results.tracks[0]
			embed.title = 'Track Enqueued!'
			embed.description = f'[{track.title}]({track.uri})'

			player.add(track=track, requester=ctx.author.id)
		
		await ctx.respond(embed=embed)

		# We don't want to call .play() if the player is playing as that will effectively
		# skip the current track
		if not player.is_playing:
			await player.play()
	

	@discord.command(aliases=['dc'])
	@commands.check(MusicService.create_player)
	async def disconnect(self, ctx: discord.ApplicationContext):
		"""
		Disconnects the player from the voice channel and clears its queue.
		"""
		player: lavalink.BasePlayer = self.bot.lavalink.player_manager.get(ctx.guild.id)
		# The necessary voice channel checks are handled in "create_player".
		# We don't need to duplicate code checking them again.

		# Clear the queue to ensure old tracks don't start playing
		# when someone else queues something.
		player.queue.clear()
		# Stop the current track so Lavalink consumes less resource.
		await player.stop()
		# Disconnect from the voice channel.
		await ctx.voice_client.disconnect(force=True)
		await ctx.respond('* | Disconnected.')


def setup(bot: discord.Bot):
	bot.add_cog(MusicCore(bot))

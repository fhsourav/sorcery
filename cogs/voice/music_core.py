import asyncio
import requests
from typing import cast

import discord

import wavelink

from utils.music import CoreFunctions

class MusicCore(discord.Cog):
	"""This cog contains the core music features."""
	
	def __init__(self, bot: discord.Bot):
		self.bot = bot


	@discord.Cog.listener()
	async def on_ready(self):
		# I wanted to initialize this variable/const (whatever) in __init__
		# but cogs are initialized before logging in
		# so I was getting errors
		# on_ready event listener works since it is accessed after the bot is logged in
		self.DISCONNECT_MESSAGE = f"{self.bot.user.name} has gracefully left the stage. See you next time!"
		self.search_results = {} # list of dict for temporarily storing music search results


	async def empty_channel_timeout(self, player: wavelink.Player, msg: str):
		"""Helper function: If no user in the voice channel that the player is connected to, disconnect after a timeout"""
		try:
			await player.home.send(f"{msg} Leaving after a timeout of 2 minutes.")
			await asyncio.sleep(120) # 2 minutes (120 seconds) of inactivity
			self.search_results.clear()
			await player.home.send(self.DISCONNECT_MESSAGE)
			await player.channel.set_status(None)
			await player.disconnect()

		except asyncio.CancelledError:
			pass # if cancelled, do nothing (maybe do something someday, but for now, nothing comes to mind.)


	def clear_empty_channel_timeout_task(self, player: wavelink.Player):
		if hasattr(player, "empty_channel_timeout_task") and player.empty_channel_timeout_task:
			if not player.empty_channel_timeout_task.done():
				player.empty_channel_timeout_task.cancel()
			player.empty_channel_timeout_task = None


	@discord.Cog.listener()
	async def on_voice_state_update(self, member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
		"""When a user changes their voice state."""

		# This event is currently being used to check if there are any users
		# in the voice channel that the player is connected to.
		# If there are no users in the voice channel, we start a 2 minute countdown
		# and if no user joins within 2 minutes, the player disconnects 

		# If the member is a bot, do nothing
		if member.bot:
			return

		# return if both before and after have the same channel, meaning no user left or joined a voice channel
		if before.channel == after.channel:
			return
		
		# return if wavelink is inactive and voice inactivity timeout is None
		# Explanation: is wavelink is inactive, then wavelink's inactivity timeout is already running, so return
		# and if wavelink is active, and empty_channel_timeout_task exists, return

		player: wavelink.Player = cast(wavelink.Player, member.guild.voice_client)

		if not player: # If player is not connected
			# TODO: Error checking
			return

		if before.channel == player.channel: # member has left the channel
			if player.wavelink_is_inactive:
				return

			if not False in [member.bot for member in player.channel.members]: # if the channel is inactive (if all members are bots)
				msg = "" # the message to send
				if player.playing and not player.paused: # if the player is in the middle of playing a track
					await player.pause(True) # pause the player
					msg += "Playback paused." # notify in a message
				if len(player.channel.members) > 1: # if there are other bots in the channel
					msg += f" The bots are now conspiring to take over {player.channel.mention}."
				else: # if the bot is alone in the channel
					msg += f" {self.bot.user.name} is alone in {player.channel.mention}."

				player.empty_channel_timeout_task = asyncio.create_task(self.empty_channel_timeout(player, msg))
		
		elif after.channel == player.channel: # member has joined the channel
			if hasattr(player, "empty_channel_timeout_task") and player.empty_channel_timeout_task:
				if not player.empty_channel_timeout_task.done(): # if a member joins the channel before timeout is done
					msg = ""
					player.empty_channel_timeout_task.cancel() # cancel the task
					if player.playing and (not hasattr(player, "paused_by_user") or not player.paused_by_user): # if player was playing a track
						await player.pause(False) # resume it
						msg += "Playback resumed."
					
					await player.home.send(f"Timeout cancelled. {msg}") # notify in a message
				
				player.empty_channel_timeout_task = None # remove the task


	@discord.Cog.listener()
	async def on_shutdown(self):
		"""Disconnects the Player."""
		for guild in self.bot.guilds:
			player: wavelink.Player = cast(wavelink.Player, guild.voice_client)
			if player:
				await self.disconnect_player(player)

	
	async def disconnect_player(self, player: wavelink.Player):
		self.clear_empty_channel_timeout_task(player)
		self.search_results.clear()
		if player.channel.status == player.channel_status:
			await player.channel.set_status(None)
		await player.home.send(self.DISCONNECT_MESSAGE)
		await player.disconnect()


	@discord.Cog.listener()
	async def on_wavelink_track_start(self, payload: wavelink.TrackStartEventPayload):
		"""When a track starts playing."""

		player: wavelink.Player | None = payload.player
		if not player:
			# TODO: Handle edge cases
			return
		
		original: wavelink.Playable | None = payload.original
		track: wavelink.Playable = payload.track

		embed: discord.Embed = discord.Embed(title="Now Playing")
		embed.description = f"**[{track.title}]({track.uri})** by `{track.author}`"

		if track.artwork:
			embed.set_thumbnail(url=track.artwork)

		if original:
			if original.recommended:
				embed.description += f"\n*This track was recommended via {track.source}*"
			
			extra_info = dict(original.extras)

			if "requester_id" in extra_info:
				embed.description += f"\n*This track was requested by <@{original.extras.requester_id}>*"

			lrclib_data = requests.get(f"https://lrclib.net/api/get?artist_name={track.author}&track_name={track.title}")
			if lrclib_data.status_code == 200:
				lrclib_data = lrclib_data.json() # contains id, trackName, artistName, albumName, duration, instrumental, plainLyrics and syncedLyrics.
				extra_info["albumName"] = lrclib_data["albumName"]
				extra_info["trackName"] = lrclib_data["trackName"]
				extra_info["artistName"] = lrclib_data["artistName"]
				extra_info["plainLyrics"] = lrclib_data["plainLyrics"] if not lrclib_data["instrumental"] else "🎼 instrumental 🎼"

			original.extras = extra_info

			if (not original.album.name) and "albumName" in dict(original.extras) and original.extras.albumName:
				original.album.name = original.extras.albumName

		footerText = CoreFunctions.get_player_state(player)
		embed.set_footer(text=footerText)

		player.channel_status = f"Listening to {track.title}"
		await player.channel.set_status(player.channel_status)

		player.wavelink_is_inactive = False

		await player.home.send(embed=embed)


	@discord.Cog.listener()
	async def on_wavelink_track_end(self, payload: wavelink.TrackEndEventPayload):
		"""When the current track has finished playing."""

		player: wavelink.Player | None = payload.player
		if not player:
			# TODO: Handle edge case
			return

		if player.channel.status == player.channel_status:
			await player.channel.set_status(None)

		player.wavelink_is_inactive = True

		# if not player.current and player.queue.is_empty and self.autoplaymode == wavelink.AutoPlayMode.partial:
		# 	await player.home.send("Player is inactive. Leaving after 2 minutes.")
	

	async def on_wavelink_track_exception(self, payload: wavelink.TrackExceptionEventPayload):
		"""When an exception occurs while playing a track."""

		player: wavelink.Player | None = payload.player
		
		await player.skip(force=True)

		player.home.send(f"Error playing `{payload.track.title}`")

	
	async def on_wavelink_track_stuck(self, payload: wavelink.TrackStuckEventPayload):
		"""When a track gets stuck while playing."""

		player: wavelink.Player | None = payload.player

		await player.skip(force=True)

		player.home.send(f"Player got stuck playing `{payload.track.title}`. Skipping...")

	
	@discord.Cog.listener()
	async def on_wavelink_inactive_player(self, player: wavelink.Player):
		self.clear_empty_channel_timeout_task(player)
		self.search_results.clear()
		await player.home.send(f"Inactivity detected. {self.DISCONNECT_MESSAGE}")
		await player.disconnect()


	@discord.slash_command(name="disconnect")
	async def disconnect(self, ctx: discord.ApplicationContext):
		"""Disconnects the Player."""
		player: wavelink.Player = cast(wavelink.Player, ctx.voice_client)

		# if the player cannot be disconnected for reasons such as the user not being in the channel
		if not await CoreFunctions.check_voice(ctx=ctx, disconnect=True):
			return

		self.clear_empty_channel_timeout_task(player)
		self.search_results.clear()

		if player.channel.status == player.channel_status:
			await player.channel.set_status(None) # since player.disconnect() does not trigger on_wavelink_track_end

		await player.disconnect()
		await ctx.respond(self.DISCONNECT_MESSAGE) # not using self.disconnect_player since this command will be responded with the message


	async def autocomplete_query(self, ctx: discord.AutocompleteContext):
		"""Autocompleting a `/play` query"""
		
		src = ctx.options["source"] # value passed for source: str
		playlist = ctx.options["playlist"] # value passed for playlist: bool

		tracklist = await wavelink.Playable.search(ctx.value, source=src) # generating tracklist from the value of the query
		
		# if tracklist is empty, return the value of the query
		if not tracklist:
			return [f"{ctx.value}" if ctx.value else "Could not find anything for that query."]
		
		if not ctx.interaction.user.id in self.search_results:
			self.search_results[ctx.interaction.user.id] = {}
		else:
			self.search_results[ctx.interaction.user.id].clear() # clear previous query info (if any) from the self.tracks dictionary

		if playlist: # if the query is a playlist
			if isinstance(tracklist, wavelink.Playlist): # check if the result is also a playlist
				self.search_results[ctx.interaction.user.id][tracklist.name] = tracklist # put the playlist in self.tracks
			else:
				self.search_results[ctx.interaction.user.id]["No playlist found."] = None
		else:
			# if not, create separate entry for all the tracks
			for track in tracklist:
				track_str = f"[{CoreFunctions.milli_to_minutes(track.length)}] {track.title[:50]} by {track.author[:20]} ({track.source})" # length of name must be between 0 to 100; slicing title and author to 50 and 20 characters respectively
				self.search_results[ctx.interaction.user.id][track_str] = track # store the track

		return [
			track_str for track_str in self.search_results[ctx.interaction.user.id]
		]


	@discord.slash_command(name="play")
	@discord.option(
		name="source",
		description="Where to search",
		choices=[
			discord.OptionChoice(name="YouTube Music", value="ytmsearch"),
			discord.OptionChoice(name="YouTube", value="ytsearch"),
			discord.OptionChoice(name="SoundCloud", value="scsearch"),
			discord.OptionChoice(name="Any link", value=None)
		]
	)
	@discord.option(
		name="query",
		description="Search for the name or url of the track",
		autocomplete=autocomplete_query
	)
	@discord.option(
		name="playlist",
		description="If the query is a playlist",
		choices=[
			False,
			True
		]
	)
	async def play(self, ctx: discord.ApplicationContext, source: str, playlist: bool, query: str):
		"""Play a song with the given query."""

		# if the command was not invoked from a guild
		# TODO some error checking
		if not ctx.guild:
			return
		
		# if source is invalid
		if query == "No playlist found." or query == "Could not find anything for that query." or query not in self.search_results[ctx.author.id]:
			await ctx.respond(f"Could not find any {'playlist' if playlist else 'track'} with that query. Please try again.", ephemeral=True)
			return

		await CoreFunctions.play(ctx, self.search_results[ctx.author.id][query])
	

	@discord.slash_command(name="nowplaying")
	async def nowplaying(self, ctx: discord.ApplicationContext):
		"""Display information of the currently playing track."""
		if not await CoreFunctions.check_voice(ctx):
			return
		
		player: wavelink.Player = cast(wavelink.Player, ctx.voice_client)
		
		embed = CoreFunctions.get_track_info_embed(ctx, player.current)

		await ctx.respond(embed=embed)


	@discord.slash_command(name="volume")
	@discord.option(
		name="value",
		max_value=200,
		min_value=0,
	)
	async def volume(self, ctx: discord.ApplicationContext, value: int):
		"""Set the volume of the player [0 - 200]"""
		await CoreFunctions.set_volume(ctx, value)

	
	@discord.slash_command(name="skip")
	async def skip(self, ctx: discord.ApplicationContext):
		"""Skip the current song."""
		player: wavelink.Player = cast(wavelink.Player, ctx.voice_client)

		if not await CoreFunctions.check_voice(ctx):
			return
		
		if not player.playing:
			return await ctx.respond("The queue is empty. Nothing to skip.")
		
		track: wavelink.Playable = player.current

		loopmode = player.queue.mode
		player.queue.mode = wavelink.QueueMode.normal

		await player.skip(force=True)

		player.queue.mode = loopmode

		await ctx.respond(f"Skipped `{track.title}`.")


	@discord.slash_command(name="restart")
	async def restart(self, ctx: discord.ApplicationContext):
		"""Restart the current track."""
		if not await CoreFunctions.check_voice(ctx):
			return
		
		player: wavelink.Player = cast(wavelink.Player, ctx.voice_client)

		if not player.playing:
			return await ctx.respond("No track is playing at the moment.", ephemeral=True)
			
		await player.seek()

		if player.paused:
			await player.pause(False)

		await ctx.respond(f"Restarted `{player.current.title}`.")
	

	@discord.slash_command(name="seek")
	@discord.option(
		name="hour",
		description="The hour value",
		min_value=0,
	)
	@discord.option(
		name="minute",
		description="The minute value",
		min_value=0,
	)
	@discord.option(
		name="second",
		description="The second value",
		min_value=0,
	)
	async def seek(self, ctx: discord.ApplicationContext, hour: int, minute: int, second: int):
		"""Seek to the provided position in the currently playing track."""
		if not await CoreFunctions.check_voice(ctx):
			return
		
		player: wavelink.Player = cast(wavelink.Player, ctx.voice_client)

		seek_position = ((((hour * 60) + minute) * 60) + second) * 1000

		if seek_position > player.current.length:
			return await ctx.respond("Track length exceeded.", ephemeral=True)
		
		await player.seek(seek_position)

		await ctx.respond(f"`{player.current.title}` seeked to {hour:02}:{minute:02}:{second:02}")


	@discord.slash_command(name="rewind")
	@discord.option(
		name="value",
		description="how far to rewind in seconds",
		min_value=0,
	)
	async def rewind(self, ctx: discord.ApplicationContext, value: int = 10):
		"""Rewind the track."""
		if not await CoreFunctions.check_voice(ctx):
			return
		
		player: wavelink.Player = cast(wavelink.Player, ctx.voice_client)

		if not player.playing:
			return await ctx.respond("No tracks are currently being played.", ephemeral=True)
		
		ms = value * 1000

		seek_position = max(0, player.position - ms)

		await player.seek(seek_position)

		await ctx.respond("The track has been rewinded.")


	@discord.slash_command(name="fastforward")
	@discord.option(
		name="value",
		description="how far to fast-forward in seconds",
		min_value=0,
	)
	async def rewind(self, ctx: discord.ApplicationContext, value: int = 10):
		"""Fast-forward the track."""
		if not await CoreFunctions.check_voice(ctx):
			return
		
		player: wavelink.Player = cast(wavelink.Player, ctx.voice_client)

		if not player.playing:
			return await ctx.respond("No tracks are currently being played.", ephemeral=True)
		
		ms = value * 1000

		seek_position = min(player.current.length, player.position + ms)

		await player.seek(seek_position)

		await ctx.respond("The track has been fast-forwarded.")


	@discord.slash_command(name="pausetoggle")
	async def pausetoggle(self, ctx: discord.ApplicationContext):
		"""Pause/resume playback."""
		player: wavelink.Player = cast(wavelink.Player, ctx.voice_client)
		
		if not await CoreFunctions.check_voice(ctx):
			return
		
		if not player.playing:
			return await ctx.respond("Queue is empty.")

		await player.pause(not player.paused)

		player.paused_by_user = player.paused # a custom attribute to know if the user has triggered the pause

		await ctx.respond(f"Playback {'paused' if player.paused else 'resumed'}.")


	@discord.slash_command(name="stop")
	async def stop(self, ctx: discord.ApplicationContext):
		"""Stops the player, clears the queue."""
		await CoreFunctions.stop(ctx)
	

	@discord.slash_command(name="lyrics")
	async def lyrics(self, ctx: discord.ApplicationContext):
		"""Display lyrics of the currently playing track."""
		if not await CoreFunctions.check_voice(ctx):
			return
		
		player: wavelink.Player = cast(wavelink.Player, ctx.voice_client)
		if player.playing and "plainLyrics" in dict(player.current.extras):
			author = discord.EmbedAuthor(name=f"{ctx.author.nick if ctx.author.nick else ctx.author.display_name}", icon_url=ctx.author.avatar)
			description = f"Artist: {player.current.extras.artistName}"
			description += f"\nDuration: {CoreFunctions.milli_to_minutes(player.current.length)}"
			description += f"\nAlbum: {player.current.album.name}"
			description += "\n# 📝🎶 Lyrics"
			description += f"\n\n {player.current.extras.plainLyrics}"
			embed = discord.Embed(
				author=author,
				description=description,
				title=player.current.extras.trackName,
				url=player.current.uri,
				thumbnail=player.current.artwork,
			)
			return await ctx.respond(embed=embed)
		
		return await ctx.respond("No lyrics found for the current track.", ephemeral=True)


def setup(bot: discord.Bot):
	bot.add_cog(MusicCore(bot))

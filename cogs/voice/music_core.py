from typing import cast

import discord

import wavelink

from utils.shared_functions import *

class MusicCore(discord.Cog):
	"""This cog contains the core music features."""
	
	def __init__(self, bot: discord.Bot):
		self.bot = bot
		self.tracks = {} # dict for temporarily storing music search results
		self.autoplaymode = wavelink.AutoPlayMode.partial

	
	@discord.Cog.listener()
	async def on_wavelink_track_start(self, payload: wavelink.TrackStartEventPayload):
		"""When a track starts."""

		player: wavelink.Player | None = payload.player
		if not player:
			# TODO: Handle edge cases
			return
		
		original: wavelink.Playable | None = payload.original
		track: wavelink.Playable = payload.track

		embed: discord.Embed = discord.Embed(title="Now Playing")
		embed.description = f"**{track.title}** by `{track.author}`"

		if track.artwork:
			embed.set_image(url=track.artwork)

		if original and original.recommended:
			embed.description += f"\n\n`This track was recommended via {track.source}`"

		if track.album.name:
			embed.add_field(name="Album", value=track.album.name)

		await player.channel.set_status(f"Playing {track.title}")

		await player.home.send(embed=embed)


	@discord.Cog.listener()
	async def on_wavelink_track_end(self, payload: wavelink.TrackEndEventPayload):
		"""When a track ends."""

		player: wavelink.Player | None = payload.player
		if not player:
			# TODO: Handle edge case
			return

		await player.channel.set_status(None)


	@discord.slash_command(name="join")
	async def join(self, ctx: discord.ApplicationContext):
		"""Join the voice channel user is in."""
		
		player: wavelink.Player = await join_voice(ctx=ctx)

		if not player:
			return
		
		await ctx.respond(f"Joined {ctx.author.voice.channel.name}")


	@discord.slash_command(name="disconnect")
	async def disconnect(self, ctx: discord.ApplicationContext):
		"""Disconnects the Player."""
		player: wavelink.Player = cast(wavelink.Player, ctx.voice_client)

		if not player:
			return await ctx.respond("The bot is not connected to a voice channel.")
		
		await player.channel.set_status(None)
		await player.disconnect()

		await ctx.respond("Bot has been disconnected.")


	async def autocomplete_query(self, ctx: discord.AutocompleteContext):
		"""Autocompleting a `/play` query"""
		
		src = ctx.options["source"] # value passed for source: str
		playlist = ctx.options["playlist"] # value passed for playlist: bool

		tracklist = await wavelink.Playable.search(ctx.value, source=src) # generating tracklist from the value of the query
		
		# if tracklist is empty, return the value of the query
		if not tracklist:
			return [f"{ctx.value}" if ctx.value else "Could not find anything for that query."]
		
		self.tracks.clear() # clear previous query info (if any) from the self.tracks dictionary

		if playlist: # if the query is a playlist
			if isinstance(tracklist, wavelink.Playlist): # check if the result is also a playlist
				self.tracks[tracklist.name] = tracklist # put the playlist in self.tracks
			else:
				self.tracks["No playlist found."] = None
		else:
			# if not, create separate entry for all the tracks
			for track in tracklist:
				track_str = f"[{milli_to_minutes(track.length)}] {track.title[:50]} by {track.author[:20]} ({track.source})" # length of name must be between 0 to 100; slicing title and author to 50 and 20 characters respectively
				self.tracks[track_str] = track # store the track

		return [
			track_str for track_str in self.tracks
		]


	@discord.slash_command(name="play")
	@discord.option(
		name="source",
		description="Where to search",
		choices=[
			discord.OptionChoice(name="YouTube Music", value="ytmsearch"),
			discord.OptionChoice(name="YouTube", value="ytsearch"),
			discord.OptionChoice(name="SoundCloud", value="scsearch"),
			discord.OptionChoice(name="Any link (even local files!)", value="")
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
		if query == "No playlist found." or query == "Could not find anything for that query." or query not in self.tracks:
			await ctx.respond(f"Could not find any {'playlist' if playlist else 'tracks'} with that query. Please try again.")
			return
		
		player: wavelink.Player = await join_voice(ctx=ctx)
		if not player:
			return
		
		player.autoplay = self.autoplaymode

		tracks = self.tracks[query]
		if isinstance(tracks, wavelink.Playlist):
			# tracks is a playlist...
			added: int = await player.queue.put_wait(tracks)
			await ctx.respond(f"Added the playlist **`{tracks.name}`** ({added} songs) to the queue.")
		else:
			# tracks is not a playlist, it's a single track
			track = tracks
			await player.queue.put_wait(track)
			await ctx.respond(f"Added **`{track} ({track.source})`** to the queue.")

		if not player.playing:
			# Play now since we aren't playing anything...
			await player.play(player.queue.get(), volume=30)


	@discord.slash_command(name="volume")
	@discord.option(
		name="value",
		max_value=100,
		min_value=0,
	)
	async def volume(self, ctx: discord.ApplicationContext, value: int):
		"""Set the volume of the player [0 - 100]"""
		player: wavelink.Player = cast(wavelink.Player, ctx.voice_client)

		if not await check_voice(ctx=ctx, player=player):
			return
		
		await player.set_volume(value)
		await ctx.respond(f"Volume set to {value}.")

	
	@discord.slash_command(name="skip")
	async def skip(self, ctx: discord.ApplicationContext):
		"""Skip the current song."""
		player: wavelink.Player = cast(wavelink.Player, ctx.voice_client)

		if not await check_voice(ctx=ctx, player=player):
			return
		
		if not player.playing:
			return await ctx.respond("The queue is empty. Nothing to skip.")
		
		track: wavelink.Playable = player.current

		await player.skip(force=True)
		await ctx.respond(f"skipped {track.title} by {track.author}")		
	

	@discord.slash_command(name="toggle_playback")
	async def toggle_playback(self, ctx: discord.ApplicationContext):
		"""Pause/resume playback."""
		player: wavelink.Player = cast(wavelink.Player, ctx.voice_client)
		
		if not await check_voice(ctx=ctx, player=player):
			return
		
		if not player.playing:
			return await ctx.respond("Queue is empty.")

		await player.pause(not player.paused)

		await ctx.respond(f"Playback {'paused' if player.paused else 'resumed'}.")


	@discord.slash_command(name="stop")
	async def stop(self, ctx: discord.ApplicationContext):
		"""Stops the player, clears the queue."""
		player: wavelink.Player = cast(wavelink.Player, ctx.voice_client)

		if not await check_voice(ctx=ctx, player=player):
			return
		
		player.queue.clear()

		if player.playing:
			await player.stop(force=True) # player.stop is an alias for player.skip 

		await ctx.respond("Playback has stopped.")


def setup(bot: discord.Bot):
	bot.add_cog(MusicCore(bot))

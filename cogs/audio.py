from typing import cast

import discord
from discord.ext import commands

import wavelink

class Audio(commands.Cog):
	
	def __init__(self, bot: discord.Bot):
		self.bot = bot
		self.connections = {}

	async def connect_nodes(self):
		"""Connect to our Lavalink nodes."""
		await self.bot.wait_until_ready() # wait until the bot is ready

		nodes = [
			wavelink.Node(
				identifier="Node1", #This identifier must be unique for all the nodes you are going to use
				uri="http://0.0.0.0:2333", # Protocol (http/s) is required, port must be what Lavalink uses
				password="youshallnotpass"
			)
		]

		# cache_capacity is EXPERIMENTAL.Turn it off by passing None
		await wavelink.Pool.connect(nodes=nodes, client=self.bot, cache_capacity=100) # Connect our nodes

	
	@discord.slash_command(name="play")
	async def play(self, ctx: discord.ApplicationContext, query: str):
		"""Play a song with the given query."""
		if not ctx.guild:
			return
		
		# First we may define our voice client,
		# for this, we are going to use typing.cast()
		# function just for the type checker know that
		# `ctx.voice_client` is going to be from type
		# `wavelink.Player`
		player = cast(wavelink.Player, ctx.voice_client) # type: ignore

		if not player: # We firstly check if there is a voice client
			try:
				player = await ctx.author.voice.channel.connect(cls=wavelink.Player) # If there isn't, we connect it to the channel
			except AttributeError:
				await ctx.respond("Please join a voice channel first before using this command.")
			except discord.ClientException:
				await ctx.respond("I was unable to join this voice channel. Please try again.")

		# Turn on AutoPlay to enabled mode.
		# enabled = AutoPlay will play songs for us and fetch recommendations...
		# partial = AutoPlay will play songs for us, but WILL NOT fetch recommendations...
		# disabled = AutoPlay will do nothing...
		player.autoplay = wavelink.AutoPlayMode.enabled

		# Lock the player to this chanel...
		if not hasattr(player, "home"):
			player.home = ctx.channel
		elif player.home != ctx.channel:
			await ctx.respond(f"You can only play songs in {player.home.mention}, as the player has already started there.")

		# # Now we are going to check if the invoker of the command
		# # is in the same voice channel than the voice client, when defined.
		# # If not, we return an error message.
		# if ctx.author.voice.channel.id != vc.channel.id:
		# 	return await ctx.respond("You must be in the same voice channel as the bot.")
		
		# # Now we search for the song. You can optionally
		# # pass the "source" keyword, of type "wavelink.TrackSource"
		# songlist = await wavelink.Playable.search(search)

		# This will handle fetching Tracks and Playlists...
		# Seed the doc strings for more information on this method...
		# If spotify is enabled via LavaSrc, this will automatically fetch Spotify tracks if you pass a URL...
		# Defaults to YouTube for non URL based queries...
		tracks: wavelink.Search = await wavelink.Playable.search(query)

		if not tracks: # In case the song is not found
			await ctx.respond("Could not find any tracks with that query. Please try again.") # we return an error message

		if isinstance(tracks, wavelink.Playlist):
			# tracks is a playlist...
			added: int = await player.queue.put_wait(tracks)
			await ctx.respond(f"Added the playlist **`{tracks.name}`** ({added} songs) to the queue.")
		else:
			track: wavelink.Playable = tracks[0]
			await player.queue.put_wait(track)
			await ctx.respond(f"Added **`{track} ({track.source})`** to the queue.")

		if not player.playing:
			# Play now since we aren't playing anything...
			await player.play(player.queue.get(), volume=30)

	@discord.slash_command()
	async def skip(self, ctx: discord.ApplicationContext):
		"""Skip the current song."""
		player: wavelink.Player = cast(wavelink.Player, ctx.voice_client)
		if not player:
			return
		
		await player.skip(force=True)
		await ctx.respond("skipped...")

	@discord.slash_command(name="toggle", aliases=["pause", "resume"])
	async def pause_resume(self, ctx: discord.ApplicationContext):
		"""Pause or Resume the Player depending on its crrent state."""
		player: wavelink.Player = cast(wavelink.Player, ctx.voice_client)
		if not player:
			return
		
		await player.pause(not player.paused)
		await ctx.message.respond(f"{'paused' if player.paused else 'resumed'}")

	@discord.slash_command()
	async def volume(self, ctx: discord.ApplicationContext, value: int):
		"""Change the volume of the player."""
		player: wavelink.Player = cast(wavelink.Player, ctx.voice_client)
		if not player:
			return
		
		await player.set_volume(value)
		await ctx.respond(f"volume changed to {value}.")

	@discord.slash_command()
	async def disconnect(self, ctx: discord.ApplicationContext):
		"""Disconnects the Player."""
		player: wavelink.Player = cast(wavelink.Player, ctx.voice_client)
		if not player:
			return
		
		await player.disconnect()
		await ctx.respond("Bot has been disconnected.")


	@commands.Cog.listener()
	async def on_ready(self):
		await self.connect_nodes() # connect to the server

	@commands.Cog.listener()
	async def on_wavelink_node_ready(self, payload: wavelink.NodeReadyEventPayload):
		# Everytime a node is successfully connected, we
		# will print a message letting it know.
		print(f"Node with ID {payload.session_id} has connected")
		print(f"Resumed session: {payload.resumed}")

	@commands.Cog.listener()
	async def on_wavelink_track_start(self, payload: wavelink.TrackStartEventPayload):
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

		await player.home.send(embed=embed)

	@discord.slash_command()
	async def record(self, ctx: discord.ApplicationContext): # If you're using commands.Bot, this will also work
		voice = ctx.author.voice

		if not voice:
			await ctx.respond("You aren't in a voice channel!")

		vc = await voice.channel.connect() # Connect to the voice channel the author is in.
		self.connections.update({ctx.guild.id: vc}) # Updating the cache with the guild and channel.

		vc.start_recording(
			discord.sinks.WaveSink(), # The sink type to use.
			self.once_done, # What to do once done
			ctx.channel # The channel to disconnect from.
		)

	
	async def once_done(self, sink: discord.sinks, channel: discord.TextChannel, *args): # Our voice client already passes these in.
		recorded_users = [ # A list of recorded users
			f"<@{user_id}>"
			for user_id, audio in sink.audio_data.items()
		]
		await sink.vc.disconnect() # Disconnect from the voice channel.
		files = [discord.File(audio.file, f"{user_id}.{sink.encoding}") for user_id, audio in sink.audio_data.items()] # List down the files.
		await channel.send(f"finished recording audio for: {', '.join(recorded_users)}.", files=files) # Send a message with the accumulated files.

	
	@discord.slash_command()
	async def stop_recording(self, ctx: discord.ApplicationContext):
		if ctx.guild.id in self.connections: # Check if the guild is in the cache.
			vc = self.connections[ctx.guild.id]
			vc.stop_recording() # Stop recording, and call the callback (once_done).
			del self.connections[ctx.guild.id] # Remove the guild from the cache.
			await ctx.delete() # And delete.
		else:
			await ctx.respond("I am currently not recording here.") # Respond with this if we aren't recording.


def setup(bot: discord.Bot):
	bot.add_cog(Audio(bot))

import discord

from discord.ext import commands

from bot import LavalinkVoiceClient

class MusicService:
	
	async def create_player(ctx: discord.ApplicationContext):
		"""
		A check that is invoked before any commands marked with `@discord.Bot.check(create_player)` can run.
		
		This function will try to create a player for the guild associated with this Context, or raise
		an error which will be relayed to the user if one cannot be created.
		"""
		if ctx.guild is None:
			raise commands.NoPrivateMessage()
			return
		
		player = ctx.bot.lavalink.player_manager.create(ctx.guild.id)

		# Create returns a player if one exists, otherwise creates.
		# This line is important because it ensures that a player always exists for a guild.

		# Most people might consider this a waste of resources for guilds that aren't playing, but this is
		# the easiest and simplest way of ensuring players are created.

		# These are commands that require the bot to join a voicechannel (i.e. initiating playback).
		# Commands such as volume/skip etc don't require the bot to be in a voicechannel so don't need listing here.
		should_connect = ctx.command.name in ('play', 'pausetoggle', 'skip', 'volume')

		voice_client = ctx.voice_client

		if not ctx.author.voice or not ctx.author.voice.channel:
			# Check if we're in a voice channel. If we are, tell the user to join our voice channel.
			if voice_client is not None:
				raise discord.errors.ApplicationCommandInvokeError('You need to join my voice channel first.')
			
			# Otherwise, tell them to join any voice channel to begin playing music.
			raise discord.errors.ApplicationCommandInvokeError("Join a voice channel first.")
		
		voice_channel = ctx.author.voice.channel

		if voice_client is None:
			if not should_connect:
				raise discord.errors.ApplicationCommandInvokeError("I'm not playing music.")
			
			permissions = voice_channel.permissions_for(ctx.me)

			if not permissions.connect or not permissions.speak:
				raise discord.errors.ApplicationCommandInvokeError('I need the `CONNECT` and `SPEAK` permissions.')
			
			if voice_channel.user_limit > 0:
				# A limit of 0 means no limit. Anything higher means that there is a member limit which we need to check.
				# If it's full, and we don't have "move members" permissions, then we cannot join it.
				if len(voice_channel.members) >= voice_channel.user_limit and not ctx.me.guild_permissions.move_members:
					raise discord.errors.ApplicationCommandInvokeError("Your voice channel is full!")
				
			player.store('channel', ctx.channel.id)
			await ctx.author.voice.channel.connect(cls=LavalinkVoiceClient)
		
		elif voice_client.channel.id != voice_channel.id:
			raise discord.errors.ApplicationCommandInvokeError("You need to be in my voice channel!")
		
		return True

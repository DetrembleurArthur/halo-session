# bot.py

import discord
from discord.ext import commands
import requests
import asyncio
import os
from halostats import *

TOKEN = os.getenv("DISCORD_HALO_SESSION_BOT_TOKEN")
if TOKEN is None:
	import sys
	TOKEN = sys.argv[1]

intents = discord.Intents.default()
intents.message_content = True

#client = discord.Client(intents=intents)
bot = commands.Bot(command_prefix="!",intents=intents)


sessions = {}

async def private_message(message, text):
	dm_channel = await message.author.create_dm()
	await dm_channel.send(text)

async def private_image(message, image):
	dm_channel = await message.author.create_dm()
	await dm_channel.send(file=image)


@bot.command(name="last")
async def last_game(message, pseudo=None):
	pseudo = pseudo if pseudo != None else message.author.nick
	lastGame = LastGame(pseudo)
	lastGame.update()
	await private_message(message, lastGame.to_str())
	await private_message(message, f"\n\n{pseudo}'s medals:")
	image = lastGame.medals.create_image(pseudo)
	await private_image(message, discord.File(image, filename=f"{pseudo}-medals.png"))

@bot.command(name="start")
async def start_session(message, pseudo=None):
	pseudo = pseudo if pseudo != None else message.author.nick
	if pseudo not in sessions.keys():
		sessions[pseudo] = {"lastGame" : LastGame(pseudo, skip_first=True)}
		lastGame = sessions[pseudo]["lastGame"]
		await message.channel.send(f"{pseudo}'s session started\n")
		while pseudo in sessions.keys():
			print("update...")
			lastGame.update()
			if lastGame.changed:
				await private_message(message, lastGame.to_str())
				await private_message(message, f"\n{pseudo}'s medals:")
				image = lastGame.medals.create_image(pseudo)
				await private_image(message, discord.File(image, filename=f"{pseudo}-medals.png"))
			print("sleep for 30s...")
			await asyncio.sleep(30)

@bot.command(name="stop")
async def stop_session(message, pseudo=None):
	pseudo = pseudo if pseudo != None else message.author.nick
	if pseudo in sessions.keys():
		del sessions[pseudo]
		await private_message(message, f"{pseudo}'s session stopped")
	else:
		await private_message(message, f"{pseudo} has no session")



@bot.event
async def on_ready():
	print(f'{bot.user} has connected to Discord!')



#client.run(TOKEN)
bot.run(TOKEN)
# bot.py

import discord
from discord.ext import commands
import requests
import asyncio
import os
from halostats import *
import json

TOKEN = os.getenv("DISCORD_HALO_SESSION_BOT_TOKEN")
if TOKEN is None:
	import sys
	TOKEN = sys.argv[1]

intents = discord.Intents.default()
intents.message_content = True

#client = discord.Client(intents=intents)
bot = commands.Bot(command_prefix="!",intents=intents)


sessions = {}
users = {}

def get_pseudo(message, pseudo=None):
	if pseudo is not None: return pseudo
	if message.author.name in users.keys(): return users[message.author.name]["pseudo"]
	return message.author.name

async def private_message(message, text):
	dm_channel = await message.author.create_dm()
	await dm_channel.send(text)

async def private_image(message, image):
	dm_channel = await message.author.create_dm()
	await dm_channel.send(file=image)

async def clear_messages(message):
	dm_channel = await message.author.create_dm()
	async for message_ in dm_channel.history(limit=None):
		if message_.author == bot.user:
			await message_.delete()

@bot.command(name="last")
async def last_game(message, pseudo=None):
	await clear_messages(message)
	pseudo = get_pseudo(message, pseudo)
	lastGame = LastGame(pseudo)
	lastGame.update()
	async with message.typing():
		await private_message(message, lastGame.to_str())
		await private_message(message, f"\n\n{pseudo}'s medals:")
		image = lastGame.medals.create_image(pseudo)
		await private_image(message, discord.File(image, filename=f"{pseudo}-medals.png"))

@bot.command(name="start")
async def start_session(message, pseudo=None):
	await clear_messages(message)
	pseudo = get_pseudo(message, pseudo)
	if pseudo not in sessions.keys():
		sessions[pseudo] = {"lastGame" : LastGame(pseudo, skip_first=True)}
		lastGame = sessions[pseudo]["lastGame"]
		await message.channel.send(f"{pseudo}'s session started\n")
		while pseudo in sessions.keys():
			print("update...")
			lastGame.update()
			if lastGame.changed:
				async with message.typing():
					await clear_messages(message)
					await private_message(message, lastGame.to_str())
					await private_message(message, f"\n{pseudo}'s medals:")
					image = lastGame.medals.create_image(pseudo)
					await private_image(message, discord.File(image, filename=f"{pseudo}-medals.png"))
			print("sleep for 30s...")
			await asyncio.sleep(30)

@bot.command(name="stop")
async def stop_session(message, pseudo=None):
	await clear_messages(message)
	pseudo = get_pseudo(message, pseudo)
	if pseudo in sessions.keys():
		del sessions[pseudo]
		await private_message(message, f"{pseudo}'s session stopped")
	else:
		await private_message(message, f"{pseudo} has no session")

@bot.command(name="pseudo")
async def register_pseudo(message, pseudo):
	await clear_messages(message)
	if message.author not in users.keys():
		users[message.author.name] = {"pseudo" : pseudo}
	else:
		users[message.author.name]["pseudo"] = pseudo
	with open('/home/arthur/Documents/halo-session/users.json', 'w') as file:
		file.write(json.dumps(users, indent=4))
	print(f"{pseudo} saved")
	await private_message(message, f"**{pseudo}** registered for ***{message.author}***")

@bot.command(name="whoami")
async def whoami(message, pseudo=None):
	await clear_messages(message)
	pseudo = get_pseudo(message, pseudo)
	await private_message(message, f"You are **{pseudo}**")

@bot.event
async def on_ready():
	global users
	print(f'{bot.user} has connected to Discord!')
	with open('/home/arthur/Documents/halo-session/users.json', 'r') as file:
		users = json.load(file)
	print("users loaded")



#client.run(TOKEN)
bot.run(TOKEN)

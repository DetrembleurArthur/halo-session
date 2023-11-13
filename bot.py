# bot.py

import discord
from discord.ext import commands
import requests
import asyncio
import os
from halostats import *
import json
from datetime import date
from log import logger

logger.info("starting")

DIR = "/etc/halo-session/"
TOKEN = os.getenv("DISCORD_HALO_SESSION_BOT_TOKEN")
if TOKEN is None:
	import sys
	TOKEN = sys.argv[1]

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!",intents=intents)


sessions = {}
users = {}

def save_users():
	with open(f'{DIR}users.json', 'w') as file:
		file.write(json.dumps(users, indent=4))
	logger.info(f"users saved in {DIR}users.json")

def get_pseudo(message, pseudo=None):
	if pseudo is not None: return pseudo
	if message.author.name in users.keys(): return users[message.author.name]["pseudo"]
	return message.author.name

async def private_message(message, text):
	dm_channel = await message.author.create_dm()
	await dm_channel.send(text)
	logger.info(f"message sent to {message.author.name} : {text}")

async def private_image(message, image):
	dm_channel = await message.author.create_dm()
	await dm_channel.send(file=image)
	logger.info(f"image sent to {message.author.name}")

async def clear_messages(message):
	dm_channel = await message.author.create_dm()
	async for message_ in dm_channel.history(limit=None):
		if message_.author == bot.user:
			await message_.delete()

def get_target_percentage(lastGame: LastGame, author_name: str):
	target_xp = users[author_name]["target_xp"]
	current_session_xp = lastGame.score.acc
	if target_xp > 0:
		ratio = current_session_xp / target_xp
		return ratio * 100.0

@bot.command(name="last")
async def last_game(message, pseudo=None):
	logger.info(f"{message.author.name} used '!last' command")
	pseudo = get_pseudo(message, pseudo)
	lastGame = LastGame(pseudo)
	lastGame.update()
	await private_message(message, lastGame.to_str())
	if lastGame.medals_number.value > 0:
		await private_message(message, f"**{pseudo}**'s medals:")
		image = lastGame.medals.create_image(pseudo)
		async with message.typing(): await private_image(message, discord.File(image, filename=f"{pseudo}-medals.png"))

@bot.command(name="start")
async def start_session(message, pseudo=None):
	SLEEP_TIME = 30
	logger.info(f"{message.author.name} used '!start' command")
	pseudo = get_pseudo(message, pseudo)
	if pseudo not in sessions.keys():
		current_date = date.today()
		sessions[pseudo] = {"lastGame" : LastGame.load(pseudo, f"{DIR}sessions/{pseudo}-{current_date}.pkl")}
		lastGame = sessions[pseudo]["lastGame"]
		lastGame.skip_first = True
		await message.channel.send(f"{pseudo}'s session started\n")
		while pseudo in sessions.keys():
			print("update...")
			lastGame.update()
			if lastGame.changed:
				lastGame.save(f"{DIR}sessions/{pseudo}-{current_date}.pkl")
		
				await private_message(message, lastGame.to_str())
				target_perc = get_target_percentage(lastGame, message.author.name)
				target_xp = users[message.author.name]["target_xp"]
				if target_perc != None:
					score_per_sec = lastGame.score.acc / lastGame.duration_seconds.acc
					game_score_per_sec = lastGame.score.value / lastGame.duration_seconds.value
					day_score_per_sec = lastGame.score.acc / lastGame.total_sotd
					day_game_score_per_sec = lastGame.score.value / lastGame.total_sotd
					await private_message(message, f"""
:goal: Target xp: **{lastGame.score.acc}** / **{users[message.author.name]['target_xp']}** -> ***{target_perc:.2f}%***

:clock: (game) Tot. Time to target xp: **{seconds_to_time_str(target_xp // game_score_per_sec)}**
:clock: (game) Time to target xp: **{seconds_to_time_str((target_xp-lastGame.score.acc) // game_score_per_sec)}**

:clock: (in-game) Tot. Time to target xp: **{seconds_to_time_str(target_xp // score_per_sec)}**
:clock: (in-game) Time to target xp: **{seconds_to_time_str((target_xp-lastGame.score.acc) // score_per_sec)}**

:clock: (day-game) Tot. Time to target xp: **{seconds_to_time_str(target_xp // day_game_score_per_sec)}**
:clock: (day-game) Time to target xp: **{seconds_to_time_str((target_xp-lastGame.score.acc) // day_game_score_per_sec)}**

:clock: (day) Tot. Time to target xp: **{seconds_to_time_str(target_xp // day_score_per_sec)}**
:clock: (day) Time to target xp: **{seconds_to_time_str((target_xp-lastGame.score.acc) // day_score_per_sec)}**
""")
				if lastGame.medals_number.value > 0:
					image = lastGame.medals.create_image(pseudo)
					async with message.typing(): await private_image(message, discord.File(image, filename=f"{pseudo}-medals.png"))
			await asyncio.sleep(SLEEP_TIME)

@bot.command(name="stop")
async def stop_session(message, pseudo=None):
	logger.info(f"{message.author.name} used '!stop' command")
	pseudo = get_pseudo(message, pseudo)
	if pseudo in sessions.keys():
		del sessions[pseudo]
		await private_message(message, f"{pseudo}'s session stopped")
	else:
		await private_message(message, f"{pseudo} has no session")

@bot.command(name="pseudo")
async def register_pseudo(message, pseudo):
	logger.info(f"{message.author.name} used '!register' command")
	if message.author not in users.keys():
		users[message.author.name] = {"pseudo" : pseudo, "target_xp" : 0}
	else:
		users[message.author.name]["pseudo"] = pseudo
	save_users()
	await private_message(message, f"**{pseudo}** registered for ***{message.author}***")

@bot.command(name="target")
async def target(message, target_xp: int=None, pseudo=None):
	logger.info(f"{message.author.name} used '!target' command")
	pseudo = get_pseudo(message, pseudo)
	if message.author.name in users.keys() and target_xp != None:
		target_xp = int(target_xp)
		users[message.author.name]["target_xp"] = target_xp
		save_users()
		await private_message(message, f"Target xp set for **{pseudo}**: **{target_xp}xp**")
	elif target_xp == None:
		await private_message(message, f"Target xp for **{pseudo}** is **{users[message.author.name]['target_xp']}xp**")
	else:
		await private_message(message, f"Target xp not set for **{pseudo}**, please retry")

@bot.command(name="whoami")
async def whoami(message, pseudo=None):
	logger.info(f"{message.author.name} used '!whoami' command")
	pseudo = get_pseudo(message, pseudo)
	await private_message(message, f"You are **{pseudo}**")

@bot.event
async def on_ready():
	global users
	logger.info(f'{bot.user} has connected to Discord!')
	with open(f'{DIR}users.json', 'r') as file:
		users = json.load(file)
	logger.info(f"users loaded from {DIR}users.json")



#client.run(TOKEN)
bot.run(TOKEN)

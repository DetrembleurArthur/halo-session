# bot.py

import discord
from discord.ext import commands
import requests
import asyncio
import os

TOKEN = os.getenv("DISCORD_HALO_SESSION_BOT_TOKEN")

intents = discord.Intents.default()
intents.message_content = True

#client = discord.Client(intents=intents)
bot = commands.Bot(command_prefix="!",intents=intents)

sessions = {}

def get_stats(pseudo):
	result = requests.get(f"https://sr-nextjs.vercel.app/api/halodotapi?path=%2Fgames%2Fhalo-infinite%2Fstats%2Fmultiplayer%2Fplayers%2F{pseudo}%2Fservice-record%2Fmatchmade%3Ffilter%3Dall")
	return result.json()

async def general(message, pseudo=None):
	if pseudo is None: pseudo = message.author.nick
	data = get_stats(pseudo)
	xp = data["data"]["stats"]["core"]["scores"]["personal"]
	kills = data["data"]["stats"]["core"]["summary"]["kills"]
	await message.channel.send(f"""
***{pseudo}

Total experience: {xp}
Total kills: {kills}***
""")

async def start_session(message, pseudo=None):
	global sessions
	if pseudo is None: pseudo = message.author.nick
	data = get_stats(pseudo)
	sessions[pseudo] = {"last_data" : data, "begin_data" : data, "delta_data" : dict.fromkeys(data, 0), "pooling":False}
	xp = data["data"]["stats"]["core"]["scores"]["personal"]
	kills = data["data"]["stats"]["core"]["summary"]["kills"]
	await message.channel.send(f"""
***Session started for {pseudo}

Total experience: {xp}
Total kills: {kills}***
""")

async def check(message, pseudo=None, shownull=True):
	global sessions
	if pseudo is None: pseudo = message.author.nick
	current_data = get_stats(pseudo)
	begin_data = sessions[pseudo]["begin_data"]
	last_data = sessions[pseudo]["last_data"]
	delta_data = sessions[pseudo]["delta_data"]
	xp = current_data["data"]["stats"]["core"]["scores"]["personal"] - begin_data["data"]["stats"]["core"]["scores"]["personal"]
	kills = current_data["data"]["stats"]["core"]["summary"]["kills"] - begin_data["data"]["stats"]["core"]["summary"]["kills"]
	delta_xp = current_data["data"]["stats"]["core"]["scores"]["personal"] - last_data["data"]["stats"]["core"]["scores"]["personal"]
	delta_kills = current_data["data"]["stats"]["core"]["summary"]["kills"] - last_data["data"]["stats"]["core"]["summary"]["kills"]
	sessions[pseudo]["last_data"] = current_data
	if shownull or delta_xp > 0:
		await message.channel.send(f"""
	***Session started for {pseudo}

	Session experience: {xp}(+{delta_xp})
	Session kills: {kills}(+{delta_kills})***
	""")

@bot.command(name="start")
async def pooling(message, pseudo=None):
	global sessions
	if pseudo is None: pseudo = message.author.nick
	if pseudo not in sessions.keys(): await start_session(message, pseudo)
	if not sessions[pseudo]["pooling"]:
		sessions[pseudo]["pooling"] = True
		while True:
			await check(message, pseudo, False)
			if not sessions[pseudo]["pooling"]:
				del sessions[pseudo]
				await message.channel.send("***Sirarthurias session stopped***")
				break
			await asyncio.sleep(30)
	else:
		await message.channel.send("***\nAlready started***")

async def stop(message, pseudo=None):
	global sessions
	if pseudo is None: pseudo = message.author.nick
	if pseudo not in sessions.keys() or not sessions[pseudo]["pooling"]:
		await message.channel.send(f"***{pseudo} session not started***")
	else:
		sessions[pseudo]["pooling"] = False
		await message.channel.send(f"***{pseudo} session stopping***")


command_map = {
	"!general" : general,
	"!start": pooling,
	"!stop": stop
}

@bot.event
async def on_ready():
	print(f'{bot.user} has connected to Discord!')


#client.run(TOKEN)
bot.run(TOKEN)
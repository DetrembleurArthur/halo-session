import requests
import sys
import json
import os
import csv
from log import logger

"""import pymongo

mongo_client = pymongo.MongoClient("mongodb://localhost:27017/")
halodb = mongo_client["halodb"]
games = halodb["games"]
#db.games.aggregate({$group: {_id:"$pseudo", kills:{$sum:"$game.player.stats.core.summary.kills"}}})


def dump_games(pseudo):
	global games
	print(f"dump {pseudo} games")
	offset = 0
	while True:
		url = f"https://sr-nextjs.vercel.app/api/halodotapi?path=%2Fgames%2Fhalo-infinite%2Fstats%2Fmultiplayer%2Fplayers%2F{pseudo}%2Fmatches%3Ftype%3Dmatchmaking%26count%3D25%26offset%3D{offset}"
		result = requests.get(url)
		result = result.json()["data"]
		temp = []
		for game in result:
			temp.append({"game": game, "pseudo": pseudo})
		if len(result) == 0:
			break
		games.insert_many(temp)
		offset += 25
		print(f"{pseudo} games dumped: {offset}")
	print("games dumped into mongodb")
"""

class GameRecord:

	def __init__(self):
		self.id = None
		self.map = None
		self.mode = None
		self.playlist = None
		self.interaction = None
		self.rank = None
		self.outcome = None
		self.kills = None
		self.deaths = None
		self.assists = None
		self.betrayals = None
		self.suicides = None
		self.spawns = None
		self.max_killing_spree = None
		self.vehicles_destroyed = None
		self.vehicles_hijacked = None
		self.total_medals = None
		self.unique_medals = None
		self.objectives_completed = None
		self.damage_taken = None
		self.damage_dealt = None
		self.shots_fired = None
		self.shots_hit = None
		self.shots_missed = None
		self.shots_accuracy = None
		self.round_won = None
		self.round_lost = None
		self.round_tied = None
		self.kills_melee = None
		self.kills_grenades = None
		self.kills_headshots = None
		self.kills_power_weapons = None
		self.kills_sticks = None
		self.kills_assassinations = None
		self.kills_splatters = None
		self.kills_repulsor = None
		self.kills_fusion_coils = None
		self.kdr = None
		self.kda = None
		self.avg_life_duration = None
		self.score = None
		self.points = None
		self.joined_in_progress = None
		self.joined_at = None
		self.left_at = None
		self.present_at_beginning = None
		self.game_completed = None
		self.kills_expected = None
		self.kills_expected_sd = None
		self.deaths_expected = None
		self.deaths_expected_sd = None
		self.season = None
		self.duration = None
		self.started_at = None
		self.ended_at = None

	def update(self, json):
		self.id = json["id"]
		self.map = json["details"]["map"]["name"]
		self.mode = json["details"]["ugcgamevariant"]["name"]
		self.playlist = json["details"]["playlist"]["name"]
		self.interaction = json["properties"]["interaction"]

		self.rank = json["player"]["rank"]
		self.outcome = json["player"]["outcome"]

		self.kills = json["player"]["stats"]["core"]["summary"]["kills"]
		self.deaths = json["player"]["stats"]["core"]["summary"]["deaths"]
		self.assists = json["player"]["stats"]["core"]["summary"]["assists"]
		self.betrayals = json["player"]["stats"]["core"]["summary"]["betrayals"]
		self.suicides = json["player"]["stats"]["core"]["summary"]["suicides"]
		self.spawns = json["player"]["stats"]["core"]["summary"]["spawns"]
		self.max_killing_spree = json["player"]["stats"]["core"]["summary"]["max_killing_spree"]
		self.vehicles_destroyed = json["player"]["stats"]["core"]["summary"]["vehicles"]["destroys"]
		self.vehicles_hijacked = json["player"]["stats"]["core"]["summary"]["vehicles"]["hijacks"]
		self.total_medals = json["player"]["stats"]["core"]["summary"]["medals"]["total"]
		self.unique_medals = json["player"]["stats"]["core"]["summary"]["medals"]["unique"]
		self.objectives_completed = json["player"]["stats"]["core"]["summary"]["objectives_completed"]

		self.damage_taken = json["player"]["stats"]["core"]["damage"]["taken"]
		self.damage_dealt = json["player"]["stats"]["core"]["damage"]["dealt"]

		self.shots_fired = json["player"]["stats"]["core"]["shots"]["fired"]
		self.shots_hit = json["player"]["stats"]["core"]["shots"]["hit"]
		self.shots_missed = json["player"]["stats"]["core"]["shots"]["missed"]
		self.shots_accuracy = json["player"]["stats"]["core"]["shots"]["accuracy"]

		self.round_won = json["player"]["stats"]["core"]["rounds"]["won"]
		self.round_lost = json["player"]["stats"]["core"]["rounds"]["lost"]
		self.round_tied = json["player"]["stats"]["core"]["rounds"]["tied"]

		self.kills_melee = json["player"]["stats"]["core"]["breakdown"]["kills"]["melee"]
		self.kills_grenades = json["player"]["stats"]["core"]["breakdown"]["kills"]["grenades"]
		self.kills_headshots = json["player"]["stats"]["core"]["breakdown"]["kills"]["headshots"]
		self.kills_power_weapons = json["player"]["stats"]["core"]["breakdown"]["kills"]["power_weapons"]
		self.kills_sticks = json["player"]["stats"]["core"]["breakdown"]["kills"]["sticks"]
		self.kills_assassinations = json["player"]["stats"]["core"]["breakdown"]["kills"]["assassinations"]
		self.kills_splatters = json["player"]["stats"]["core"]["breakdown"]["kills"]["vehicles"]["splatters"]
		self.kills_repulsor = json["player"]["stats"]["core"]["breakdown"]["kills"]["miscellaneous"]["repulsor"]
		self.kills_fusion_coils = json["player"]["stats"]["core"]["breakdown"]["kills"]["miscellaneous"]["fusion_coils"]

		self.kdr = json["player"]["stats"]["core"]["kdr"]
		self.kda = json["player"]["stats"]["core"]["kda"]

		self.avg_life_duration = json["player"]["stats"]["core"]["average_life_duration"]["seconds"]

		self.score = json["player"]["stats"]["core"]["scores"]["personal"]
		self.points = json["player"]["stats"]["core"]["scores"]["points"]

		self.joined_in_progress = json["player"]["participation"]["joined_in_progress"]
		self.joined_at = json["player"]["participation"]["joined_at"]
		self.left_at = json["player"]["participation"]["left_at"]
		self.present_at_beginning = json["player"]["participation"]["presence"]["beginning"]
		self.game_completed = json["player"]["participation"]["presence"]["completion"]

		if json["player"]["performances"] != None:
			self.kills_expected = json["player"]["performances"]["kills"]["expected"]
			self.kills_expected_sd = json["player"]["performances"]["kills"]["standard_deviation"]
			self.deaths_expected = json["player"]["performances"]["deaths"]["expected"]
			self.deaths_expected_sd = json["player"]["performances"]["deaths"]["standard_deviation"]

		self.season = json["season"]["properties"]["identifier"]

		self.duration = json["playable_duration"]["seconds"]
		self.started_at = json["started_at"]
		self.ended_at = json["ended_at"]

	def save(self, writer):
		writer.writerow(list(self.__dict__.values()))

	def header(self):
		return list(self.__dict__.keys())


DIR = "/var/www/html/"
NGINX_HTML = "index.nginx-debian.html"

def dump_games(pseudo):
	logger.info(f"dump {pseudo} games")
	offset = 0
	filename = f"{DIR}halo_games/{pseudo}_games.csv"
	last_gameid_filename = f"{DIR}halo_games/.{pseudo}_lastgameid"
	last_gameid = ""
	exists = os.path.exists(filename)
	if os.path.exists(last_gameid_filename):
		with open(last_gameid_filename, "rt") as file: last_gameid = file.readline()
	first = True
	game = GameRecord()
	running = True
	with open(filename, "at") as file:
		writer = csv.writer(file, delimiter=';', quotechar='"', quoting=csv.QUOTE_NONNUMERIC)
		if not exists:
			writer.writerow(game.header())
			with open(f"{DIR}{NGINX_HTML}", "at") as nginx: nginx.write(f"<a href='./halo_games/{pseudo}_games.csv' download>{pseudo}:csv</a><br>\n")
		while running:
			url = f"https://sr-nextjs.vercel.app/api/halodotapi?path=%2Fgames%2Fhalo-infinite%2Fstats%2Fmultiplayer%2Fplayers%2F{pseudo}%2Fmatches%3Ftype%3Dmatchmaking%26count%3D25%26offset%3D{offset}"
			result = requests.get(url)
			if not "data" in result.json():
				running = False
				break
			result = result.json()["data"]
			if len(result) == 0:
				break
			for json_game in result:
				if first:
					with open(last_gameid_filename, "wt") as lgifile:
						lgifile.write(json_game["id"])
					first = False
				if json_game["id"] == last_gameid:
					running = False
					break
				game.update(json_game)
				game.save(writer)
				offset += 1
			print(f"{pseudo} games dumped: {offset}")
		logger.info(f"games saved to {filename}")
	return offset

if __name__ == "__main__":
	dump_games(sys.argv[1])

import requests
import sys
import json

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


def dump_games(pseudo):
	print(f"dump {pseudo} games")
	games = []
	offset = 0
	while True:
		url = f"https://sr-nextjs.vercel.app/api/halodotapi?path=%2Fgames%2Fhalo-infinite%2Fstats%2Fmultiplayer%2Fplayers%2F{pseudo}%2Fmatches%3Ftype%3Dmatchmaking%26count%3D25%26offset%3D{offset}"
		result = requests.get(url)
		result = result.json()["data"]
		if len(result) == 0:
			break
		games.append(result)
		offset += 25
		print(f"{pseudo} games dumped: {offset}")
	print("saving")
	with open(f"{pseudo}_games.json", "wt") as file:
		file.write(json.dumps({f"games": games}, indent=4))
	print("games saved")

if __name__ == "__main__":
	dump_games(sys.argv[1])

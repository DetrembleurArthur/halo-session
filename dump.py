import requests
import sys
import json


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

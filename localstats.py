import sys
import numpy as np
import pymongo
import matplotlib.pyplot as plt

mongo_client = pymongo.MongoClient("mongodb://localhost:27017/")
halodb = mongo_client["halodb"]
games = halodb["games"]
pseudo = sys.argv[1]

if __name__ == "__main__":
	cursor = games.find({"pseudo": pseudo}, {"kills":"$game.player.stats.core.summary.kills", "deaths":"$game.player.stats.core.summary.deaths", "mode":"$game.details.ugcgamevariant.name"})#.sort({"game.started_at":1})
	kills = np.array([])
	deaths = np.array([])
	modes = []
	for game in cursor:
		kills = np.append(kills, game["kills"])
		deaths = np.append(deaths, game["deaths"])
		modes.append(game["mode"])
	plt.xlim(0, 100)
	plt.ylim(0, 100)
	plt.scatter(kills,deaths)

	#plt.plot(deaths,'.',  c="red")

	print(np.mean(kills)/ np.mean(deaths))
	plt.show()


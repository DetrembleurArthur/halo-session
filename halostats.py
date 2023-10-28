import haloapi as halo
from PIL import Image
import requests
from io import BytesIO
import time


def url_to_image(url):
	print(url)
	response = requests.get(url)
	image = Image.open(BytesIO(response.content))
	return image


class IncrementalVar:

	def __init__(self, value=0):
		self.value = value
		self.acc = self.value

	def set(self, value):
		self.acc += value
		self.value = value

class Medals:

	def __init__(self, json_medals_list: list):
		self.infos = [(medal["id"], medal["count"]) for medal in json_medals_list]
		self.size = 0
		for medal in self.infos:
			self.size += medal[1]

	def create_image(self, pseudo) -> Image:
		image = Image.new('RGBA', (5*128, self.size//5*128))
		print("size:", (5*128, self.size//5*128))
		temp = 0
		for medal in self.infos:
			url = halo.medal_url(medal[0])
			medal_count = medal[1]
			medal_image = url_to_image(url)
			for i in range(medal_count):
				print((temp%5*128, temp//5*128))
				image.paste(medal_image, box=(temp%5*128, temp//5*128))
				temp += 1
		binary = BytesIO()
		image.save(binary, "PNG")
		binary.seek(0)
		return binary


class LastGame:

	def __init__(self, pseudo):
		self.pseudo = pseudo

	def update(self):
		json = halo.get_last_game(self.pseudo)
		self.map_name = json["details"]["map"]["name"]
		self.game_mode = json["details"]["ugcgamevariant"]["name"]
		self.player_rank = json["player"]["rank"]
		self.winner = json["player"]["outcome"]
		self.player_team = json["player"]["properties"]["team"]["name"]
		self.player_kills = IncrementalVar(json["player"]["stats"]["core"]["summary"]["kills"])
		self.player_deaths = IncrementalVar(json["player"]["stats"]["core"]["summary"]["deaths"])
		self.player_assists = IncrementalVar(json["player"]["stats"]["core"]["summary"]["assists"])
		self.player_betrayals = IncrementalVar(json["player"]["stats"]["core"]["summary"]["betrayals"])
		self.player_suicides = IncrementalVar(json["player"]["stats"]["core"]["summary"]["suicides"])
		self.max_killing_spree = IncrementalVar(json["player"]["stats"]["core"]["summary"]["max_killing_spree"])
		self.medals_number = IncrementalVar(json["player"]["stats"]["core"]["summary"]["medals"]["total"])
		self.damage_taken = IncrementalVar(json["player"]["stats"]["core"]["damage"]["taken"])
		self.damage_dealt = IncrementalVar(json["player"]["stats"]["core"]["damage"]["dealt"])
		self.shots_fired = IncrementalVar(json["player"]["stats"]["core"]["shots"]["fired"])
		self.shots_hit = IncrementalVar(json["player"]["stats"]["core"]["shots"]["hit"])
		self.shots_missed = IncrementalVar(json["player"]["stats"]["core"]["shots"]["missed"])
		self.shots_accuracy = json["player"]["stats"]["core"]["shots"]["accuracy"]
		self.medals = Medals(json["player"]["stats"]["core"]["breakdown"]["medals"])
		self.ratio = json["player"]["stats"]["core"]["kdr"]
		self.average_life_duration = json["player"]["stats"]["core"]["average_life_duration"]["human"]
		self.score = IncrementalVar(json["player"]["stats"]["core"]["scores"]["personal"])
		self.duration = json["playable_duration"]["human"]

	def to_str(self):
		return f"""
Last game for {self.pseudo}

Map: {self.map_name}
Mode: {self.game_mode}
Status: {self.winner}

Score: {self.score.acc} (+{self.score.value})

Team: {self.player_team}
Rank: {self.player_rank}

Kills: {self.player_kills.acc} (+{self.player_kills.value})
Deaths: {self.player_deaths.acc} (+{self.player_deaths.value})
Assists: {self.player_assists.acc} (+{self.player_assists.value})
Betrayals: {self.player_betrayals.acc} (+{self.player_betrayals.value})
Suicides: {self.player_suicides.acc} (+{self.player_suicides.value})
Max killing spree: {self.max_killing_spree.acc} (+{self.max_killing_spree.value})
Medals number: {self.medals_number.acc} (+{self.medals_number.value})

Damage taken: {self.damage_taken.acc} (+{self.damage_taken.value})
Damage dealt: {self.damage_dealt.acc} (+{self.damage_dealt.value})

Shots fired: {self.shots_fired.acc} (+{self.shots_fired.value})
Shots hit: {self.shots_hit.acc} (+{self.shots_hit.value})
Shots missed: {self.shots_missed.acc} (+{self.shots_missed.value})
Shot accuracy: {self.shots_accuracy}

Average life duration: {self.average_life_duration}
Game duration: {self.duration}
"""

if __name__ == "__main__":
	lastGame = LastGame("SirArthurias")
	lastGame.update()
	lastGame.medals.create_image()

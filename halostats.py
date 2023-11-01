import haloapi as halo
from PIL import Image
import requests
from io import BytesIO
import time
import os
import json
import pickle
from datetime import datetime
from datetime import timedelta
from log import logger

DIR = "/etc/halo-session/"

def seconds_to_time_str(seconds):
	return " ".join([data[0]+data[1] for data in zip(str(timedelta(seconds=seconds)).split(':'), ["h", "m", "s"])])

def local_medal_file_exists(medal_id):
	return os.path.exists(f"{DIR}medals/{medal_id}.png")


def url_to_image(url):
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
		width = 8
		image = Image.new('RGBA', (width*128, self.size//width*128+int(self.size%width!=0)*128))
		print("size:", (width*128, self.size//width*128))
		temp = 0
		for medal in self.infos:
			medal_image = None
			if not local_medal_file_exists(medal[0]):
				url = halo.medal_url(medal[0])
				medal_image = url_to_image(url)
				medal_image.save(f"{DIR}medals/{medal[0]}.png")
				logger.info(f"save local medal image {DIR}medals/{medal[0]}.png")
			else:
				medal_image = Image.open(f"{DIR}medals/{medal[0]}.png")
				logger.info(f"load local medal image {DIR}medals/{medal[0]}.png")
			medal_count = medal[1]
			for i in range(medal_count):
				image.paste(medal_image, box=(temp%width*128, temp//width*128))
				temp += 1
		binary = BytesIO()
		image.save(binary, "PNG")
		binary.seek(0)
		return binary


class LastGame:

	def __init__(self, pseudo, skip_first=False):
		self.pseudo = pseudo
		self.update_counter = 0
		self.game_id = "empty"
		self.changed = False
		self.skip_first = skip_first
		self.player_kills = IncrementalVar()
		self.player_deaths = IncrementalVar()
		self.player_assists = IncrementalVar()
		self.player_betrayals = IncrementalVar()
		self.player_suicides = IncrementalVar()
		self.max_killing_spree = 0
		self.medals_number = IncrementalVar()
		self.damage_taken = IncrementalVar()
		self.damage_dealt = IncrementalVar()
		self.shots_fired = IncrementalVar()
		self.shots_hit = IncrementalVar()
		self.shots_missed = IncrementalVar()
		self.score = IncrementalVar()
		self.duration_seconds = IncrementalVar()

	def update_from_json(self, json):
		self.winner = json["player"]["outcome"]
		if self.winner == "dnf":
			logger.info("ignore this game : crash or quit")
			return False
		self.game_id = json["id"]
		self.map_name = json["details"]["map"]["name"]
		self.game_mode = json["details"]["ugcgamevariant"]["name"]
		self.player_rank = json["player"]["rank"]
		self.player_team = json["player"]["properties"]["team"]
		if self.player_team != None: self.player_team = self.player_team["name"]
		self.player_kills.set(json["player"]["stats"]["core"]["summary"]["kills"])
		self.player_deaths.set(json["player"]["stats"]["core"]["summary"]["deaths"])
		self.player_assists.set(json["player"]["stats"]["core"]["summary"]["assists"])
		self.player_betrayals.set(json["player"]["stats"]["core"]["summary"]["betrayals"])
		self.player_suicides.set(json["player"]["stats"]["core"]["summary"]["suicides"])
		self.max_killing_spree = json["player"]["stats"]["core"]["summary"]["max_killing_spree"]
		self.medals_number.set(json["player"]["stats"]["core"]["summary"]["medals"]["total"])
		self.damage_taken.set(json["player"]["stats"]["core"]["damage"]["taken"])
		self.damage_dealt.set(json["player"]["stats"]["core"]["damage"]["dealt"])
		self.shots_fired.set(json["player"]["stats"]["core"]["shots"]["fired"])
		self.shots_hit.set(json["player"]["stats"]["core"]["shots"]["hit"])
		self.shots_missed.set(json["player"]["stats"]["core"]["shots"]["missed"])
		self.shots_accuracy = json["player"]["stats"]["core"]["shots"]["accuracy"]
		self.medals = Medals(json["player"]["stats"]["core"]["breakdown"]["medals"])
		self.ratio = json["player"]["stats"]["core"]["kdr"]
		self.average_life_duration = json["player"]["stats"]["core"]["average_life_duration"]["human"]
		self.score.set(json["player"]["stats"]["core"]["scores"]["personal"])
		self.duration = json["playable_duration"]["human"]
		self.duration_seconds.set(json["playable_duration"]["seconds"])
		return True

	def update(self):
		json = halo.get_last_game(self.pseudo)
		if self.skip_first:
			self.game_id = json["id"]
			self.skip_first = False
		self.changed = self.game_id != json["id"]
		if self.changed:
			logger.info("change detected")
			if self.update_from_json(json):
				self.update_counter += 1
			else:
				self.changed = False


	def save(self, filename):
		with open(filename, 'wb') as file:
			pickle.dump(self, file)
			logger.info(f'LastGame successfully saved to "{filename}"')

	@staticmethod
	def load(pseudo, filename):
		try:
			with open(filename, 'rb') as file:
				obj = pickle.load(file)
			logger.info(f"{filename} LastGame restored")
			return obj
		except FileNotFoundError:
			return LastGame(pseudo)


	def to_str(self):
		return f"""

Last game for **{self.pseudo}** :sunglasses:

:map: Map: **{self.map_name}**
:triangular_flag_on_post: Mode: **{self.game_mode}**
:v: Status: **{self.winner}**

:video_game: Score: **{self.score.acc}** (+{self.score.value})

:person_in_steamy_room: Team: **{self.player_team}**
:man_student: Rank: **{self.player_rank}**

:archery: Kills: **{self.player_kills.acc}** (***+{self.player_kills.value}***)
:skull: Deaths: **{self.player_deaths.acc}** (***+{self.player_deaths.value}***)
:smiling_face_with_tear: Assists: **{self.player_assists.acc}** (***+{self.player_assists.value}***)
:cold_face: Betrayals: **{self.player_betrayals.acc}** (***+{self.player_betrayals.value}***)
:zany_face: Suicides: **{self.player_suicides.acc}** (***+{self.player_suicides.value}***)
:ok_hand: Max killing spree: **{self.max_killing_spree}**
:medal: Medals number: **{self.medals_number.acc}** (***+{self.medals_number.value}***)

:dagger: Damage taken: **{self.damage_taken.acc}** (***+{self.damage_taken.value}***)
:boom: Damage dealt: **{self.damage_dealt.acc}** (***+{self.damage_dealt.value}***)

:fire: Shots fired: **{self.shots_fired.acc}** (***+{self.shots_fired.value}***)
:heart_on_fire: Shots hit: **{self.shots_hit.acc}** (***+{self.shots_hit.value}***)
:firefighter: Shots missed: **{self.shots_missed.acc}** (***+{self.shots_missed.value}***)
:dart: Shot accuracy: **{self.shots_accuracy:.2f}%**

:alarm_clock: Average life duration: **{self.average_life_duration}**

:clock: Game duration: **{self.duration}**
:clock: Game Score per second: **{self.score.value / self.duration_seconds.value:.2f}xp/s**
:clock: Game Score per minute: **{self.score.value / (self.duration_seconds.value / 60):.2f}xp/m**
:clock: Game Score per hour: **{self.score.value / (self.duration_seconds.value / (60 * 60)):.2f}xp/h**

:clock: Total in-game time: **{seconds_to_time_str(self.duration_seconds.acc)}**
:clock: Total Score per second: **{self.score.acc / self.duration_seconds.acc:.2f}xp/s**
:clock: Total Score per minute: **{self.score.acc / (self.duration_seconds.acc / 60):.2f}xp/m**
:clock: Total Score per hour: **{self.score.acc / (self.duration_seconds.acc / (60 * 60)):.2f}xp/h**

:nerd: Number of games today: **{self.update_counter}**

Last update at ***{datetime.now().strftime('%d/%m/%Y %H:%M:%S')}***


"""

if __name__ == "__main__":
	pass






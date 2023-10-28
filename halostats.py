import haloapi as halo
from PIL import Image
import requests
from io import BytesIO
import time
import os

def local_medal_file_exists(medal_id):
	return os.path.exists(f"/home/arthur/Documents/halo-session/medals/{medal_id}.png")


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
			medal_image = None
			if not local_medal_file_exists(medal[0]):
				url = halo.medal_url(medal[0])
				medal_image = url_to_image(url)
				medal_image.save(f"/home/arthur/Documents/halo-session/medals/{medal[0]}.png")
				print(f"save local medal image /home/arthur/Documents/halo-session/medals/{medal[0]}.png")
			else:
				medal_image = Image.open(f"/home/arthur/Documents/halo-session/medals/{medal[0]}.png")
				print(f"load local medal image /home/arthur/Documents/halo-session/medals/{medal[0]}.png")
			medal_count = medal[1]
			for i in range(medal_count):
				print((temp%5*128, temp//5*128))
				image.paste(medal_image, box=(temp%5*128, temp//5*128))
				temp += 1
		binary = BytesIO()
		image.save(binary, "PNG")
		binary.seek(0)
		return binary

	@staticmethod
	def fetch_images():
		pass


class LastGame:

	def __init__(self, pseudo, skip_first=False):
		self.pseudo = pseudo
		self.game_id = "empty"
		self.changed = False
		self.skip_first = skip_first
		self.player_kills = IncrementalVar()
		self.player_deaths = IncrementalVar()
		self.player_assists = IncrementalVar()
		self.player_betrayals = IncrementalVar()
		self.player_suicides = IncrementalVar()
		self.max_killing_spree = IncrementalVar()
		self.medals_number = IncrementalVar()
		self.damage_taken = IncrementalVar()
		self.damage_dealt = IncrementalVar()
		self.shots_fired = IncrementalVar()
		self.shots_hit = IncrementalVar()
		self.shots_missed = IncrementalVar()
		self.score = IncrementalVar()

	def update(self):
		json = halo.get_last_game(self.pseudo)
		if self.skip_first:
			self.game_id = json["id"]
			self.skip_first = False
		self.changed = self.game_id != json["id"]
		if self.changed:
			self.game_id = json["id"]
			self.map_name = json["details"]["map"]["name"]
			self.game_mode = json["details"]["ugcgamevariant"]["name"]
			self.player_rank = json["player"]["rank"]
			self.winner = json["player"]["outcome"]
			self.player_team = json["player"]["properties"]["team"]["name"]
			self.player_kills.set(json["player"]["stats"]["core"]["summary"]["kills"])
			self.player_deaths.set(json["player"]["stats"]["core"]["summary"]["deaths"])
			self.player_assists.set(json["player"]["stats"]["core"]["summary"]["assists"])
			self.player_betrayals.set(json["player"]["stats"]["core"]["summary"]["betrayals"])
			self.player_suicides.set(json["player"]["stats"]["core"]["summary"]["suicides"])
			self.max_killing_spree.set(json["player"]["stats"]["core"]["summary"]["max_killing_spree"])
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
:ok_hand: Max killing spree: **{self.max_killing_spree.acc}** (***+{self.max_killing_spree.value}***)
:medal: Medals number: **{self.medals_number.acc}** (***+{self.medals_number.value}***)

:dagger: Damage taken: **{self.damage_taken.acc}** (***+{self.damage_taken.value}***)
:boom: Damage dealt: **{self.damage_dealt.acc}** (***+{self.damage_dealt.value}***)

:fire: Shots fired: **{self.shots_fired.acc}** (***+{self.shots_fired.value}***)
:heart_on_fire: Shots hit: **{self.shots_hit.acc}** (***+{self.shots_hit.value}***)
:firefighter: Shots missed: **{self.shots_missed.acc}** (***+{self.shots_missed.value}***)
:dart: Shot accuracy: **{self.shots_accuracy:.2f}%**

:alarm_clock: Average life duration: **{self.average_life_duration}**
:clock: Game duration: **{self.duration}**
"""

if __name__ == "__main__":
	Medals.fetch_images()





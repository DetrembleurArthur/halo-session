import requests
import json
import time
from datetime import datetime
import os
import smtplib
from email.mime.text import MIMEText

file = "/home/arthur/Documents/halo-session/session_infos.txt"

email = ""
pseudo = ""
sender_email = ""
sender_password = ""

with open(file, "r") as f:
	email = f.readline()
	pseudo = f.readline()
	sender_email = f.readline()
	sender_password = f.readline()

mailing = True

today = datetime.now()
dt_string = today.strftime("%d/%m/%Y %H:%M:%S")

#https://etxvqmdrjezgtwgueiar.supabase.co/storage/v1/render/image/public/assets/games/halo-infinite/metadata/multiplayer/medals/4086138034.png?width=128&height=128
# image de médaille avec l'id

def medal_url(medal_id):
	return f"https://etxvqmdrjezgtwgueiar.supabase.co/storage/v1/render/image/public/assets/games/halo-infinite/metadata/multiplayer/medals/{medal_id}.png?width=128&height=128"

from email.message import EmailMessage
def send_email(text, subject, dst, src, password):
	if mailing:
		msg = EmailMessage()
		msg.set_content(text, subtype="html")
		msg['Subject'] = subject
		msg['From'] = src
		msg['To'] = dst
		s = smtplib.SMTP_SSL('smtp.gmail.com', 465)
		s.login(src, password)
		s.sendmail(src, [dst], msg.as_string())
		s.quit()

#SirArthurias
def get_stats(player):
	result = requests.get(f"https://sr-nextjs.vercel.app/api/halodotapi?path=%2Fgames%2Fhalo-infinite%2Fstats%2Fmultiplayer%2Fplayers%2F{player}%2Fservice-record%2Fmatchmade%3Ffilter%3Dall")
	data = result.json()
	return data

def medals_images(temp_medals_dict, delta_medals):
	buffer = ""
	for medal in temp_medals_dict.items():
		if medal[1] - delta_medals[medal[0]] > 0:
			print(f"<br><img src='{medal_url(medal[0])}'/><br>")
			buffer += f"<br>{medal[1]} (+{medal[1] - delta_medals[medal[0]]})x <img src='{medal_url(medal[0])}'/><br>"
	return buffer

begin_stats = get_stats(pseudo)
begin_xp = begin_stats["data"]["stats"]["core"]["scores"]["personal"]
begin_kills = begin_stats["data"]["stats"]["core"]["summary"]["kills"]
begin_medals = begin_stats["data"]["stats"]["core"]["breakdown"]["medals"]
begin_medals_dict = {}
for medal in begin_medals:
	begin_medals_dict[medal["id"]] = medal["count"]

send_email(f"""
Hello {pseudo} !<br><br>

Start session at {dt_string}<br><br>
xp: {begin_xp}<br>
kills: {begin_kills}<br>

<img src='https://upload.wikimedia.org/wikipedia/commons/thumb/d/d7/Halo_%28series%29_logo.svg/2560px-Halo_%28series%29_logo.svg.png'/>
""", "Halo session", dst=email, src=sender_email, password=sender_password)

delta_xp = 0
delta_kills = 0
delta_medals = {}
while True:
	current_stats = get_stats(pseudo)
	temp_xp = current_stats["data"]["stats"]["core"]["scores"]["personal"] - begin_xp
	temp_kills = current_stats["data"]["stats"]["core"]["summary"]["kills"] - begin_kills
	temp_medals = current_stats["data"]["stats"]["core"]["breakdown"]["medals"]
	temp_medals_dict = {}
	for medal in temp_medals:
		temp_medals_dict[medal["id"]] = medal["count"] - begin_medals_dict[medal["id"]]
	if temp_xp > delta_xp:
		send_email(
f"""
Hello {pseudo} !<br><br>

Stats update at {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}<br><br>

xp: {temp_xp} (+{temp_xp-delta_xp})<br>
kills: {temp_kills} (+{temp_kills-delta_kills})<br><br>

medals:<br>
{medals_images(temp_medals_dict, delta_medals)}
""", "Halo session", dst=email, src=sender_email, password=sender_password)
		os.system("clear")
		print("Start session at ", dt_string, "\n")
		print("Stats at the begining of the session:")
		print(f"\txp: {begin_xp}\n\tkills: {begin_kills}\n")
		print("Stats from the begining of the session:")
		print(f"\txp: {temp_xp} (+{temp_xp-delta_xp})\n\tkills: {temp_kills} (+{temp_kills-delta_kills})\n")
		for medal in temp_medals_dict.items():
			if medal[1] - delta_medals[medal[0]] > 0:
				print(f"{medal[1]} (+{medal[1] - delta_medals[medal[0]]}) medals earned with id {medal[0]}")
	delta_xp = temp_xp
	delta_kills = temp_kills
	delta_medals = temp_medals_dict
	print(f"Last update at {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
	time.sleep(60)

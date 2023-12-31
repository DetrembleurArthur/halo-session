import requests
from log import logger

def get_stats(pseudo):
	url = f"https://sr-nextjs.vercel.app/api/halodotapi?path=%2Fgames%2Fhalo-infinite%2Fstats%2Fmultiplayer%2Fplayers%2F{pseudo}%2Fservice-record%2Fmatchmade%3Ffilter%3Dall"
	result = requests.get(url)
	return result.json()

def get_last_game(pseudo):
	url = f"https://sr-nextjs.vercel.app/api/halodotapi?path=%2Fgames%2Fhalo-infinite%2Fstats%2Fmultiplayer%2Fplayers%2F{pseudo}%2Fmatches%3Ftype%3Dmatchmaking%26count%3D1%26offset%3D0"
	result = requests.get(url)
	return result.json()["data"][0]

def get_game_details(game_id):
	url = f"https://sr-nextjs.vercel.app/api/halodotapi?path=%2Fgames%2Fhalo-infinite%2Fstats%2Fmultiplayer%2Fmatches%2F{game_id}"
	result = requests.get(url)
	return result.json()["data"]

def medal_url(medal_id, size=128):
        return f"https://etxvqmdrjezgtwgueiar.supabase.co/storage/v1/render/image/public/assets/games/halo-infinite/metadata/multiplayer/medals/{medal_id}.png?width={size}&height={size}"

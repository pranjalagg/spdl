import requests
from config import CUSTOM_HEADER
from utils import make_unique_song_objects

def get_track_info(link, token):
    track_id = link.split("/")[-1].split("?")[0]
    response = requests.get(f"https://api.spotidownloader.com/download/{track_id}?token={token}", headers=CUSTOM_HEADER)
    return response.json()

def get_playlist_info(link, trackname_convention, mode, token):
    playlist_id = link.split("/")[-1].split("?")[0]
    response = requests.get(f"https://api.spotidownloader.com/metadata/{mode}/{playlist_id}?token={token}", headers=CUSTOM_HEADER)
    metadata = response.json()
    playlist_name = metadata['title']
    if metadata['success']:
        print("-" * 40)
        print(f"Name: {playlist_name} by {metadata['artists']}")
    
    print(f"Getting songs from {mode} (this might take a while ...)")
    track_list = []
    response = requests.get(f"https://api.spotidownloader.com/tracks/{mode}/{playlist_id}?token={token}", headers=CUSTOM_HEADER)
    tracks_data = response.json()
    track_list.extend(tracks_data['trackList'])
    next_offset = tracks_data['nextOffset']
    while next_offset:
        response = requests.get(f"https://api.spotidownloader.com/tracks/{mode}/{playlist_id}?offset={next_offset}&token={token}", headers=CUSTOM_HEADER)
        tracks_data = response.json()
        track_list.extend(tracks_data['trackList'])
        next_offset = tracks_data['nextOffset']

    song_list_dict = make_unique_song_objects(track_list, trackname_convention, playlist_name, mode)
    return song_list_dict, playlist_name

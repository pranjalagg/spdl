import requests
from config import CUSTOM_HEADER

def get_track_info(link, token):
    track_id = link.split("/")[-1].split("?")[0]
    response = requests.get(f"https://api.spotidownloader.com/download/{track_id}?token={token}",
                            headers=CUSTOM_HEADER)
    return response.json()

def get_playlist_info(link, trackname_convention, mode):
    playlist_id = link.split("/")[-1].split("?")[0]
    # Fetch playlist metadata
    response = requests.get(f"https://api.spotidownloader.com/metadata/{mode}/{playlist_id}",
                            headers=CUSTOM_HEADER)
    metadata = response.json()
    playlist_name = metadata['title']
    if metadata['success']:
        print("-" * 40)
        print(f"Name: {playlist_name} by {metadata['artists']}")
    
    print(f"Getting songs from {mode} (this might take a while ...)")
    track_list = []
    response = requests.get(f"https://api.spotidownloader.com/tracks/{mode}/{playlist_id}",
                            headers=CUSTOM_HEADER)
    track_data = response.json()
    track_list.extend(track_data['trackList'])
    next_offset = track_data['nextOffset']
    while next_offset:
        response = requests.get(f"https://api.spotidownloader.com/tracks/{mode}/{playlist_id}?offset={next_offset}",
                                headers=CUSTOM_HEADER)
        track_data = response.json()
        track_list.extend(track_data['trackList'])
        next_offset = track_data['nextOffset']
    
    return track_list, playlist_name

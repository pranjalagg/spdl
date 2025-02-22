import requests
import logging
from file_operations import save_audio, attach_track_metadata
from utils import resolve_path
import re
import os
import json

CUSTOM_HEADER = {
    'Host': 'api.spotidownloader.com',
    'Referer': 'https://spotidownloader.com/',
    'Origin': 'https://spotidownloader.com',
}

def check_track_playlist(link, outpath, create_folder, trackname_convention, token):
    resolve_path(outpath)
    if re.search(r".*spotify\.com\/(?:intl-[a-zA-Z]{2}\/)?track\/", link):
        download_track(link, outpath, trackname_convention, token)
    elif re.search(r".*spotify\.com\/playlist\/", link):
        download_playlist_tracks(link, outpath, create_folder, trackname_convention, token)
    elif re.search(r".*spotify\.com\/album\/", link):
        download_playlist_tracks(link, outpath, create_folder, trackname_convention, mode='album', token=token)
    else:
        logging.error(f"{link} is not a valid Spotify track or playlist link")

def get_track_info(link, token):
    track_id = link.split("/")[-1].split("?")[0]
    response = requests.get(f"https://api.spotidownloader.com/download/{track_id}?token={token}", headers=CUSTOM_HEADER)
    return response.json()

def get_token(reset=False):
    if os.path.exists("./.cache") and not reset:
        with open(".cache") as f:
            token = json.load(f).get("token")
    else: 
        token = input("Enter Token: ").strip()
        with open(".cache", "w") as f:
            json.dump({
                "token": token,
            }, f)
    return token 
import os
import json
import re
import logging
from downloader import check_track_playlist
from utils import get_token, trackname_convention
from spotify_api import get_playlist_info

def sync_playlist_folders(sync_file):
    with open(sync_file, "r") as file:
        data_to_sync = json.load(file)
        set_trackname_convention = 1
        for data in data_to_sync:
            if data.get("convention_code"):
                set_trackname_convention = data["convention_code"]
                continue
            check_track_playlist(data['link'], data['download_location'], data['create_folder'],
                                 set_trackname_convention, token=get_token())

def handle_sync_file(sync_file):
    if (os.path.exists(sync_file)):
        print("Syncing local album/playlist folders with Spotify")
        sync_playlist_folders(sync_file)
        print("-" * 40)
        print("Sync complete!")
    else:
        create_sync_file = input("Sync file does not exist. Do you want to create it? (y/N):")
        if create_sync_file.lower() == "y":
            data_for_sync_file = []
            trackname_type, set_trackname_convention = trackname_convention()
            data_for_sync_file.append(
                {
                    "convention_code": set_trackname_convention,
                    "trackname_convention": trackname_type,
                }
            )
            while True:
                print("-" * 40)
                playlist_link = input("Album/Playlist link (leave empty to finish): ")
                if not playlist_link:
                    break
                
                mode = 'playlist'
                if re.search(r".*spotify\.com\/album\/", playlist_link):
                    mode = 'album'
                create_folder = input(f"Create a folder for this {mode}? (y/N): ")
                download_location = input(f"Download location for tracks of this {mode} (leave empty to default to current directory): ")
                try:
                    _, playlist_name = get_playlist_info(playlist_link, set_trackname_convention, mode)
                except Exception as e:
                    print(f"Probable error with the link --> {e}. Try again!")
                    continue
                data_for_sync_file.append(
                    {
                        "name": playlist_name,
                        "link": playlist_link,
                        "create_folder": create_folder.lower() == "y",
                        "download_location": download_location if download_location else os.getcwd()
                    }
                )
            with open(sync_file, "w") as file:
                json.dump(data_for_sync_file, file)
            print("Sync file created successfully")
            print("-" * 40)
        else:
            print("Exiting program")
            exit()

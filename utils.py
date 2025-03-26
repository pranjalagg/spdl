import os
import re
import json
import time
from config import NAME_SANITIZE_REGEX
from models import Song

def resolve_path(outpath, playlist_folder=False):
    if not os.path.exists(outpath):
        if not playlist_folder:
            create_folder = input("Directory specified does not exist. Do you want to create it? (y/N): ")
        if playlist_folder or create_folder.lower() == "y":
            os.mkdir(outpath)
        else:
            print("Exiting program")
            exit()

def dict_unique(song_list, trackname_convention):
    unique_songs = {}
    duplicate_songs = []
    for song in song_list:
        trackname = f"{song.title} - {song.artists}"
        if trackname_convention == 2:
            trackname = f"{song.artists} - {song.title}"
        if len(trackname) > 260: # Added because you can't have filenames with more that 260 chars
            trackname = song.title[:255] + "..." # Just in case there is a song out there with a very very large title
        if (unique_songs.get(trackname)):
            duplicate_songs.append(trackname)
        else:
            unique_songs.setdefault(trackname, song)
    return unique_songs, duplicate_songs

def make_unique_song_objects(track_list, trackname_convention, album_name, mode):
    song_list = []
    for i, track in enumerate(track_list, 1):
        song_list.append(
            Song(
                title=re.sub(NAME_SANITIZE_REGEX, "_", track['title']),
                artists=re.sub(NAME_SANITIZE_REGEX, "_", track['artists']),
                album = album_name if mode == 'album' else track.get('album'),
                cover=track.get('cover', 'default_cover.png'),
                link=f"https://open.spotify.com/track/{track['id']}",
                track_number=i if mode == 'playlist' else track.get('trackNumber')
            )
        )
    # unique_songs = set_unique(song_list)
    unique_songs, duplicate_songs = dict_unique(song_list, trackname_convention)

    if (len(duplicate_songs)):
        print("\tDuplicate songs: ", len(duplicate_songs))
        for index, song_name in enumerate(duplicate_songs, 1):
            print(f"\t\t{index}: {song_name}")

    print("\n\tUnique Songs in playlist: ", len(unique_songs))
    for index, song_name in enumerate(unique_songs.keys(), 1):
        print(f"\t\t{index}: {song_name}")
    
    return unique_songs

def trackname_convention():
    print("How would you like to name the tracks?")
    print("1. Title - Artist (default)")
    print("2. Artist - Title")
    num = input("Enter the number corresponding to the naming convention: ").strip()
    if num == "" or num == "1":
        return "Title - Artist", 1
    elif num == "2":
        return "Artist - Title", 2
    else:
        print("Invalid input. Defaulting to Title - Artist")
        return "Title - Artist", 1

def get_token(reset=False):
    cache_file = "./.cache"
    if os.path.exists(cache_file) and not reset:

        file_age = time.time() - os.path.getmtime(cache_file)

        if file_age > 540:
            reset = True

    if reset or not os.path.exists(cache_file):
        token = input("Enter Token: ").strip()
        with open(cache_file, "w") as f:
            json.dump({"token": token}, f)
    else:
        with open(cache_file) as f:
            token = json.load(f).get("token")
    return token

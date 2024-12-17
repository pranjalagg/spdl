import argparse
import os
import requests
import re
import logging
import json
import sys
import time
from dataclasses import dataclass
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC, error, TRCK
from pathlib import Path
from typing import Optional, Dict, Tuple

if sys.version_info >= (3, 9):
    logging.basicConfig(
        filename="spdl.log",
        filemode="a",
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        encoding="utf-8"
    )
else:
    file_handler = logging.FileHandler("spdl.log", mode="a", encoding="utf-8")
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logger.addHandler(file_handler)

CUSTOM_HEADER = {
    'Host': 'api.spotifydown.com',
    'Referer': 'https://spotifydown.com/',
    'Origin': 'https://spotifydown.com',
}

SPOTIFY_PATTERNS = {
    'track': re.compile(r".*spotify\.com\/(?:intl-[a-zA-Z]{2}\/)?track\/"),
    'playlist': re.compile(r".*spotify\.com\/playlist\/"),
    'album': re.compile(r".*spotify\.com\/album\/")
}

NAME_SANITIZE_REGEX = re.compile(r"[<>:\"\/\\|?*]")

@dataclass(init=True, eq=True, frozen=True)
class Song:
    title: str
    artists: str
    album: str
    cover: str
    link: str
    track_number: int

def validate_spotify_url(url: str) -> tuple[bool, str]:
    """Validate a Spotify URL and return its type."""
    if not url:
        return False, "Empty URL provided"
        
    for media_type, pattern in SPOTIFY_PATTERNS.items():
        if pattern.match(url):
            return True, media_type
            
    return False, "Invalid Spotify URL format"

def check_track_playlist(link, outpath, create_folder, trackname_convention, token):
    resolve_path(outpath)
    is_valid, media_type = validate_spotify_url(link)
    
    if not is_valid:
        logging.error(f"{link} is not a valid Spotify URL: {media_type}")
        print(f"\n{link} is not a valid Spotify URL: {media_type}")
        return
    
    if media_type == 'track':
        download_track(link, outpath, trackname_convention, token)
    else:  # playlist or album
        download_playlist_tracks(link, outpath, create_folder, trackname_convention, mode=media_type, token=token)

def get_track_info(link, token):
    track_id = link.split("/")[-1].split("?")[0]
    response = requests.get(f"https://api.spotifydown.com/download/{track_id}?token={token}", headers=CUSTOM_HEADER)
    return response.json()

def attach_cover_art(trackname, cover_art, outpath, is_high_quality, track_number=0):
    trackname = re.sub(NAME_SANITIZE_REGEX, "_", trackname)
    filepath = os.path.join(outpath, f"{trackname}.mp3") if is_high_quality else os.path.join(outpath, "low_quality", f"{trackname}.mp3")
    try:
        audio = MP3(filepath, ID3=ID3)
    except error as e:
        logging.error(f"Error loading MP3 file from {filepath} --> {e}")
        print(f"\t Error loading MP3 file --> {e}")
        return

    if audio.tags is None:
        try:
            audio.add_tags()
        except error as e:
            logging.error(f"Error adding ID3 tags to {filepath} --> {e}")
            print(f"\tError adding ID3 tags --> {e}")
            return 
        
    audio.tags.add(
        APIC(
            encoding=1,
            mime='image/jpeg',
            type=3,
            desc=u'Cover',
            data=cover_art)
        )
    
    if track_number > 0:
        audio.tags.add(TRCK(encoding=3, text=str(track_number)))
    
    audio.save(filepath, v2_version=3, v1=2)

def save_audio(trackname, link, outpath):
    if len(trackname) > 250:  # Windows max path is 260, leave room for extension and path
        trackname = trackname[:247] + "..."
    
    trackname = re.sub(NAME_SANITIZE_REGEX, "_", trackname)
    low_quality_path = os.path.join(outpath, "low_quality")
    
    # Use pathlib for better path handling
    normal_path = Path(outpath) / f"{trackname}.mp3"
    low_qual_path = Path(low_quality_path) / f"{trackname}.mp3"
    
    if normal_path.exists() or low_qual_path.exists():
        logging.info(f"{trackname} already exists in {outpath}")
        print("\t This track already exists in the directory. Skipping download!")
        return None
    
    audio_response = requests.get(link)

    if audio_response.status_code == 200:
        temp_file = os.path.join(outpath, f"temp_{trackname}.mp3")
        with open(temp_file, "wb") as file:
            file.write(audio_response.content)
        
        # Check bitrate
        audio = MP3(temp_file)
        bitrate = audio.info.bitrate / 1000  # Convert to kbps
        
        if bitrate >= 320:
            final_path = str(normal_path)
            is_high_quality = True
        else:
            if not os.path.exists(low_quality_path):
                os.makedirs(low_quality_path)
            final_path = str(low_qual_path)
            is_high_quality = False
        
        os.rename(temp_file, final_path)
        return is_high_quality

    else:
        logging.error(f"Failed to download {trackname}. Status code: {audio_response.status_code}")
        print(f"\t Failed to download {trackname}. Status code: {audio_response.status_code}")
        return None

def resolve_path(outpath, playlist_folder=False):
    if not os.path.exists(outpath):
        if not playlist_folder:
            create_folder = input("Directory specified does not exist. Do you want to create it? (y/N): ")
        if playlist_folder or create_folder.lower() == "y":
            os.makedirs(outpath, exist_ok=True)
        else:
            print("Exiting program")
            sys.exit(1)

def dict_unique(song_list, trackname_convention):
    unique_songs = {}
    duplicate_songs = []
    for song in song_list:
        trackname = f"{song.title} - {song.artists}"
        if trackname_convention == 2:
            trackname = f"{song.artists} - {song.title}"
        if len(trackname) > 250:
            trackname = trackname[:247] + "..."
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
                track_number=i
            )
        )
    unique_songs, duplicate_songs = dict_unique(song_list, trackname_convention)

    if duplicate_songs:
        print("\tDuplicate songs: ", len(duplicate_songs))
        for index, song_name in enumerate(duplicate_songs, 1):
            print(f"\t\t{index}: {song_name}")

    print("\n\tUnique Songs in playlist: ", len(unique_songs))
    for index, song_name in enumerate(unique_songs.keys(), 1):
        print(f"\t\t{index}: {song_name}")
    
    return unique_songs

def get_playlist_info(link, trackname_convention, mode):
    playlist_id = link.split("/")[-1].split("?")[0]
    
    # Get playlist metadata
    metadata = requests.get(f"https://api.spotifydown.com/metadata/{mode}/{playlist_id}", 
                          headers=CUSTOM_HEADER).json()
    if not metadata['success']:
        raise ValueError(f"Failed to get playlist metadata: {metadata.get('message')}")
    
    playlist_name = metadata['title']
    print("-" * 40)
    print(f"Name: {playlist_name} by {metadata['artists']}")
    
    # Get all tracks with better pagination handling
    print(f"Getting songs from {mode} (this might take a while ...)")
    track_list = []
    offset = None
    
    while True:
        url = f"https://api.spotifydown.com/tracklist/{mode}/{playlist_id}"
        if offset:
            url += f"?offset={offset}"
            
        response = requests.get(url, headers=CUSTOM_HEADER).json()
        track_list.extend(response['trackList'])
        
        if not response['nextOffset']:
            break
        offset = response['nextOffset']

    song_list_dict = make_unique_song_objects(track_list, trackname_convention, playlist_name, mode)
    return song_list_dict, playlist_name

def remove_empty_files(outpath):
    """Remove any empty MP3 files from the given directory and its low_quality subdirectory."""
    for root in [outpath, os.path.join(outpath, "low_quality")]:
        if not os.path.exists(root):
            continue
        for file in os.listdir(root):
            if file.endswith(".mp3"):
                filepath = os.path.join(root, file)
                if os.path.getsize(filepath) == 0:
                    os.remove(filepath)

def sync_playlist_folders(sync_file):
    with open(sync_file, "r") as file:
        data_to_sync = json.load(file)
        set_trackname_convention = 1
        for data in data_to_sync:
            if data.get("convention_code"):
                set_trackname_convention = data["convention_code"]
                continue
            check_track_playlist(data['link'], data['download_location'], data['create_folder'], set_trackname_convention, token=get_token())

def download_track(track_link, outpath, trackname_convention, token, max_attempts=3):
    print("\nTrack link identified")

    for attempt in range(max_attempts):
        try:
            resp = get_track_info(track_link, token)
            if resp["statusCode"] == 403:
                token = get_token(reset=True)
                resp = get_track_info(track_link, token)
            elif resp["statusCode"] != 200:
                raise ValueError(f"API returned status {resp['statusCode']}: {resp.get('message')}")
                
            if not resp['success']:
                raise ValueError(f"Track info failed: {resp.get('message')}")
            
            trackname = f"{resp['metadata']['title']} - {resp['metadata']['artists']}"
            if trackname_convention == 2:
                trackname = f"{resp['metadata']['artists']} - {resp['metadata']['title']}"

            print(f"\nDownloading {trackname} to ({outpath})")
            is_high_quality = save_audio(trackname, resp['link'], outpath)
            if is_high_quality is not None:
                cover_art = requests.get(resp['metadata']['cover']).content
                attach_cover_art(trackname, cover_art, outpath, is_high_quality)
            break
            
        except requests.RequestException as e:
            logging.error(f"Network error on attempt {attempt + 1}: {e}")
        except json.JSONDecodeError as e:
            logging.error(f"Invalid JSON response on attempt {attempt + 1}: {e}")
        except Exception as e:
            logging.error(f"Unexpected error on attempt {attempt + 1}: {e}")
            print(f"\tAttempt {attempt + 1}/{max_attempts} failed with error: ", e)
            
        if attempt < max_attempts - 1:
            wait_time = 2 ** attempt  # Exponential backoff
            logging.info(f"Waiting {wait_time} seconds before retry...")
            time.sleep(wait_time)
            
    remove_empty_files(outpath)

def check_existing_tracks(song_list_dict, outpath):
    existing_tracks = os.listdir(outpath)
    return {
        track: song for track, song in song_list_dict.items()
        if not (track + ".mp3") in existing_tracks
    }

def download_playlist_tracks(playlist_link, outpath, create_folder, trackname_convention, token, max_attempts=3, mode='playlist'):
    print(f"\n{mode.capitalize()} link identified")
    song_list_dict, playlist_name_old = get_playlist_info(playlist_link, trackname_convention, mode)
    playlist_name = re.sub(NAME_SANITIZE_REGEX, "_", playlist_name_old)
    if (playlist_name != playlist_name_old):
        print(f'\n"{playlist_name_old}" is not a valid folder name. Using "{playlist_name}" instead.')

    if create_folder == True:
        outpath = os.path.join(outpath, playlist_name)
    resolve_path(outpath, playlist_folder=True)

    if os.path.exists(outpath):
        song_list_dict = check_existing_tracks(song_list_dict, outpath)
    if not song_list_dict:
        print(f"\nAll tracks from {playlist_name} already exist in the directory ({outpath}).")
        return
    
    print(f"\nDownloading {len(song_list_dict)} new track(s) from {playlist_name} to ({outpath})")
    print("-" * 40)
    
    for index, (trackname, song) in enumerate(song_list_dict.items(), 1):
        print(f"{index}/{len(song_list_dict)}: {trackname}")
        for attempt in range(max_attempts):
            try:
                resp = get_track_info(song.link, token)
                if resp["statusCode"] == 403:
                    print("\t Status code 403: Unauthorized access. Please provide a new token.")
                    logging.error("Token expired. Requested new token")
                    token = get_token(reset=True)
                    resp = get_track_info(song.link, token)
                elif resp["statusCode"] != 200:
                    raise ValueError(f"API returned status {resp['statusCode']}: {resp.get('message')}")

                is_high_quality = save_audio(trackname, resp['link'], outpath)
                if is_high_quality is not None:
                    cover_url = song.cover
                    if not cover_url.startswith("http"):
                        cover_url = resp['metadata']['cover']
                    cover_art = requests.get(cover_url).content
                    attach_cover_art(trackname, cover_art, outpath, is_high_quality, song.track_number)
                    break
                    
            except requests.RequestException as e:
                logging.error(f"Network error on attempt {attempt + 1}: {e}")
            except json.JSONDecodeError as e:
                logging.error(f"Invalid JSON response on attempt {attempt + 1}: {e}")
            except Exception as e:
                logging.error(f"Unexpected error on attempt {attempt + 1}: {e}")
                print(f"\t\tAttempt {attempt + 1}/{max_attempts} failed with error: ", e)
                
            if attempt < max_attempts - 1:
                wait_time = 2 ** attempt  # Exponential backoff
                logging.info(f"Waiting {wait_time} seconds before retry...")
                time.sleep(wait_time)
            
    remove_empty_files(outpath)

def get_token(reset=False):
    """Get token from cache, auto-fetch, or user input."""
    cache_file = ".cache"
    
    # Try cache first if not resetting
    if not reset and os.path.exists(cache_file):
        try:
            with open(cache_file) as f:
                data = json.load(f)
                if data.get("token") and isinstance(data["token"], str) and len(data["token"]) > 0:
                    return data["token"]
        except (json.JSONDecodeError, IOError):
            pass
    
    # Try auto-fetching
    print("Attempting to fetch token automatically...")
    token = get_token_auto()
    if token:
        try:
            with open(cache_file, "w") as f:
                json.dump({"token": token}, f)
            return token
        except IOError as e:
            logging.warning(f"Could not save token to cache: {e}")
    
    # Fall back to manual input
    print("Automatic token fetch failed. Please enter manually:")
    token = input("Enter Token: ").strip()
    if not token:
        raise ValueError("Token cannot be empty")
        
    try:
        with open(cache_file, "w") as f:
            json.dump({"token": token}, f)
    except IOError as e:
        logging.warning(f"Could not save token to cache: {e}")
        
    return token

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
                
                is_valid, media_type = validate_spotify_url(playlist_link)
                if not is_valid:
                    print(f"Invalid link: {media_type}. Try again!")
                    continue
                    
                mode = media_type
                create_folder = input(f"Create a folder for this {mode}? (y/N): ")
                download_location = input(f"Download location for tracks of this {mode} (leave empty to default to current directory): ")
                try:
                    _, playlist_name = get_playlist_info(playlist_link, set_trackname_convention, mode)
                except Exception as e:
                    print(f"Error getting playlist info: {e}. Try again!")
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
                json.dump(data_for_sync_file, file, indent=2)
            print("Sync file created successfully")
            print("-" * 40)
        else:
            print("Exiting program")
            sys.exit(1)

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

def main():
    parser = argparse.ArgumentParser(description="Program to download tracks from Spotify via CLI")
    parser.add_argument("-link", nargs="+", help="URL of the Spotify track or playlist (optional)")
    parser.add_argument("-outpath", nargs="?", default=os.getcwd(), help="Path to save the downloaded track")
    parser.add_argument("-sync", nargs="?", const="sync.json", help="Path of sync.json file to sync local playlist folders with Spotify playlists")
    parser.add_argument("-folder", nargs="?", default=True, help="Create a folder for the playlist(s)")
    args = parser.parse_args()

    if args.sync:
        handle_sync_file(os.path.abspath(args.sync))
    else:
        token = get_token()
        _, set_trackname_convention = trackname_convention()
        
        links = args.link if args.link else []
        while not links:
            link = input("Enter Spotify URL (or press Enter to quit): ").strip()
            if not link:
                break
            links.append(link)
            
        if not links:
            print("No links provided. Exiting program.")
            return
            
        for link in links:
            check_track_playlist(link, args.outpath, create_folder=args.folder, 
                               trackname_convention=set_trackname_convention, token=token)
    
    print("\n" + "-"*25 + " Task complete ;) " + "-"*25 + "\n")

if __name__ == "__main__":
    try:
        logging.info("-" * 10 + "Program started" + "-" * 10)
        main()
        logging.info("-" * 10 + "Program ended" + "-" * 10)
    except KeyboardInterrupt:
        print("\n------ Exiting program ------")
        logging.info("Program exited by user")

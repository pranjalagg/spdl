import argparse
import os
import requests
import re
# import eyed3
import logging
import json
from dataclasses import dataclass
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC, error
# from eyed3.id3.frames import ImageFrame
# Suppress warnings
# eyed3.log.setLevel("ERROR")
logging.basicConfig(filename="spdl.log", filemode="a", level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', encoding="utf-8")
# logging.basicConfig(filename='app.log', level=logging.INFO)
CUSTOM_HEADER = {
    'Host': 'api.spotifydown.com',
    'Referer': 'https://spotifydown.com/',
    'Origin': 'https://spotifydown.com',
}

NAME_SANITIZE_REGEX = re.compile(r"[<>:\"\/\\|?*]")

@dataclass(init=True, eq=True, frozen=True)
class Song:
    title: str
    artists: str
    album: str
    cover: str
    link: str

    # def __eq__(self, other):
    #     if not isinstance(other, Song):
    #         return False
    #     return self.title == other.title and self.artists == other.artists and self.album == other.album
    
    # def __hash__(self):
    #     print("Hello 2")
    #     return hash((self.title, self.artists, self.album))

def check_track_playlist(link, outpath, create_folder, trackname_convention):
    resolve_path(outpath)
    # if "/track/" in link:
    if re.search(r".*spotify\.com\/track\/", link):
        # return "track"
        download_track(link, outpath, trackname_convention)
    # elif "/playlist/" in link:
    elif re.search(r".*spotify\.com\/(?:intl-[a-zA-Z]{2}\/)?track\/", link):
        # return "playlist"
        download_playlist_tracks(link, outpath, create_folder, trackname_convention)
    else:
        logging.error(f"{link} is not a valid Spotify track or playlist link")
        # return None
        print(f"\n{link} is not a valid Spotify track or playlist link")

def  get_track_info(link):
    track_id = link.split("/")[-1].split("?")[0]
    response = requests.get(f"https://api.spotifydown.com/download/{track_id}", headers=CUSTOM_HEADER)
    response = response.json()
    # print(response['success'])
    # print(f"Song: {response['metadata']['title']}, Artist: {response['metadata']['artists']}, Album: {response['metadata']['album']}")
    # print(response['link'])

    return response
# def attach_cover_art(trackname, cover_art, outpath):
#     # print(outpath)
#     trackname = re.sub(NAME_SANITIZE_REGEX, "_", trackname)
#     audio_file = eyed3.load(os.path.join(outpath, f"{trackname}.mp3"))

#     # https://stackoverflow.com/questions/38510694/how-to-add-album-art-to-mp3-file-using-python-3
#     try:
#         # raise Exception("Testing")
#         if (audio_file.tag is None):
#             audio_file.initTag()

#         audio_file.tag.images.set(ImageFrame.FRONT_COVER, cover_art.content, 'image/jpeg')
#         audio_file.tag.save()
#     except Exception as e:
#         logging.error(f"Error attaching cover art to {trackname} --> {e}")
#         print(f"\tError attaching cover art --> {e}")
#         # print(e)

def attach_cover_art(trackname, cover_art, outpath):
    trackname = re.sub(NAME_SANITIZE_REGEX, "_", trackname)
    filepath = os.path.join(outpath, f"{trackname}.mp3")
    try:
        # raise error("Testing")
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
    audio.save(filepath, v2_version=3, v1=2)

def save_audio(trackname, link, outpath):
    trackname = re.sub(NAME_SANITIZE_REGEX, "_", trackname)
    if os.path.exists(os.path.join(outpath, f"{trackname}.mp3")):
        logging.info(f"{trackname} already exists in the directory ({outpath}). Skipping download!")
        print("\t This track already exists in the directory. Skipping download!")
        return False
    
    # filename = re.sub(r"[<>:\"/\\|?*]", "_", f"{trackname}.mp3")
    audio_response = requests.get(link)

    if audio_response.status_code == 200:
        with open(os.path.join(outpath, f"{trackname}.mp3"), "wb") as file:
            file.write(audio_response.content)
        return True

def resolve_path(outpath, playlist_folder=False):
    # if playlist_name and playlist_folder:
    #     outpath = os.path.join(outpath, playlist_name)
    # print("Path: ", outpath)
    if not os.path.exists(outpath):
        if not playlist_folder:
            create_folder = input("Directory specified does not exist. Do you want to create it? (y/N): ")
        if playlist_folder or create_folder.lower() == "y":
            os.mkdir(outpath)
        else:
            print("Exiting program")
            exit()

# def set_unique(song_list):
#     print("----------- Set ----------")
#     unique_songs = set(song_list)
#     duplicate_songs = [song for song in song_list if song not in unique_songs]
#     print("Duplicate songs ", duplicate_songs)
#     print("Unique songs ", unique_songs)
#     return unique_songs

def dict_unique(song_list, trackname_convention):
    # print("----------- Dict ----------")
    unique_songs = {}
    duplicate_songs = []
    for song in song_list:
        trackname = f"{song.title} - {song.artists}"
        if trackname_convention == 2:
            trackname = f"{song.artists} - {song.title}"
        if (unique_songs.get(trackname)):
            duplicate_songs.append(trackname)
        else:
            unique_songs.setdefault(trackname, song)
    return unique_songs, duplicate_songs

def make_unique_song_objects(track_list, trackname_convention):
    song_list = []
    for track in track_list:
        song_list.append(
            Song(
                title=re.sub(NAME_SANITIZE_REGEX, "_", track['title']),
                artists=re.sub(NAME_SANITIZE_REGEX, "_", track['artists']),
                album=track['album'],
                cover=track['cover'],
                link=f"https://open.spotify.com/track/{track['id']}"
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

def get_playlist_info(link, trackname_convention):
    playlist_id = link.split("/")[-1].split("?")[0]
    response = requests.get(f"https://api.spotifydown.com/metadata/playlist/{playlist_id}", headers=CUSTOM_HEADER)
    response = response.json()
    playlist_name = response['title']
    if response['success']:
        print("-" * 40)
        print(f"Name: {playlist_name} by {response['artists']}")
    
    print("Getting songs from playlist (this might take a while ...)")
    track_list = []
    response = requests.get(f"https://api.spotifydown.com/tracklist/playlist/{playlist_id}", headers=CUSTOM_HEADER)
    response = response.json()
    track_list.extend(response['trackList'])
    next_offset = response['nextOffset']
    while next_offset:
        response = requests.get(f"https://api.spotifydown.com/tracklist/playlist/{playlist_id}?offset={next_offset}", headers=CUSTOM_HEADER)
        response = response.json()
        track_list.extend(response['trackList'])
        next_offset = response['nextOffset']

    song_list_dict = make_unique_song_objects(track_list, trackname_convention)
    # print(track_list)
    # exit()
    return song_list_dict, playlist_name

    # return track_list, playlist_name

def sync_playlist_folders(sync_file):
    with open(sync_file, "r") as file:
        data_to_sync = json.load(file)
        # print(data_to_sync)
        set_trackname_convention = 1
        for data in data_to_sync:
            if data.get("convention_code"):
                set_trackname_convention = data["convention_code"]
                continue
            check_track_playlist(data['link'], data['download_location'], data['create_folder'], set_trackname_convention)
            # download_playlist_tracks(data['link'], data['download_location'])

def download_track(track_link, outpath, trackname_convention, max_attempts=3):
    print("\nTrack link identified")

    resp = get_track_info(track_link)
    if resp['success'] == False:
        print(f"Error: {resp['message']}")
        logging.error(f"Error: {resp['message']}")
        return
    
    trackname = f"{resp['metadata']['title']} - {resp['metadata']['artists']}"
    if trackname_convention == 2:
        trackname = f"{resp['metadata']['artists']} - {resp['metadata']['title']}"

    print(f"\nDownloading {trackname} to ({outpath})")
    # trackname = re.sub(r"[<>:\"/\\|?*]", "_", trackname)
    # print(trackname)
    for attempt in range(max_attempts):
        try:
            # raise Exception("Testing")
            save_status = save_audio(trackname, resp['link'], outpath)
            # print("Save status: ", save_status)
            if save_status:
                cover_art = requests.get(resp['metadata']['cover']).content
                # print("------", trackname)
                attach_cover_art(trackname, cover_art, outpath)
            break
        except Exception as e:
            logging.error(f"Attempt {attempt+1} - {trackname} --> {e}")
            print(f"\tAttempt {attempt+1} failed with error: ", e)
    remove_empty_files(outpath)

def check_existing_tracks(song_list_dict, outpath):
    existing_tracks = os.listdir(outpath)
    for track in existing_tracks:
        if track.endswith(".mp3"):
            track = track.split(".mp3")[0]
            if song_list_dict.get(track):
                # logging.info(f"{track} already exists in the directory ({outpath}). Skipping download!")
                # print(f"\t{track} already exists in the directory. Skipping download!")
                song_list_dict.pop(track)
    
    return song_list_dict

def remove_empty_files(outpath):
    for file in os.listdir(outpath):
        if os.path.getsize(os.path.join(outpath, file)) == 0:
            os.remove(os.path.join(outpath, file))

def download_playlist_tracks(playlist_link, outpath, create_folder, trackname_convention, max_attempts=3):
    print("\nPlaylist link identified")
    song_list_dict, playlist_name_old = get_playlist_info(playlist_link, trackname_convention)
    playlist_name = re.sub(NAME_SANITIZE_REGEX, "_", playlist_name_old)
    if (playlist_name != playlist_name_old):
        print(f'\n"{playlist_name_old}" is not a valid folder name. Using "{playlist_name}" instead.')



    if create_folder == True:
        outpath = os.path.join(outpath, playlist_name)

    if os.path.exists(outpath):
        song_list_dict = check_existing_tracks(song_list_dict, outpath)
    if not song_list_dict:
        print(f"\nAll tracks from {playlist_name} already exist in the directory ({outpath}).")
        return
    
    print(f"\nDownloading {len(song_list_dict)} new track(s) from {playlist_name} to ({outpath})")
    print("-" * 40 )
    for index, trackname in enumerate(song_list_dict.keys(), 1):
        # trackname = track
        # trackname = re.sub(r"[<>:\"/\\|?*]", "_", trackname)
        print(f"{index}/{len(song_list_dict)}: {trackname}")
        for attempt in range(max_attempts):
            try:
                # raise Exception("Testing")
                resp = get_track_info(song_list_dict[trackname].link)
                resolve_path(outpath, playlist_folder=True)
                save_status = save_audio(trackname, resp['link'], outpath)
                if save_status:
                    cover_art = requests.get(song_list_dict[trackname].cover).content
                    attach_cover_art(trackname, cover_art, outpath)
                    break
            except Exception as e:
                logging.error(f"Attempt {attempt+1} - {playlist_name}: {trackname} --> {e}")
                print(f"\t\tAttempt {attempt+1} failed with error: ", e)
            
    remove_empty_files(outpath)

def handle_sync_file(sync_file):
    if (os.path.exists(sync_file)):
        print("Syncing local playlist folders with Spotify playlists")
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
                playlist_link = input("Playlist link (leave empty to finish): ")
                if not playlist_link:
                    break
                create_folder = input("Create a folder for this playlist? (y/N): ")
                download_location = input("Download location for tracks of this playlist (leave empty to default to current directory): ")
                _, playlist_name = get_playlist_info(playlist_link, set_trackname_convention)
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

def trackname_convention():
    print("How would you like to name the tracks?")
    print("1. Title - Artist")
    print("2. Artist - Title")
    num = int(input("Enter the number corresponding to the naming convention: "))
    if num != 1 and num != 2:
        print("Invalid input. Defaulting to Title - Artist")
        return "Title - Artist", 1
    return "Artist - Title", num

def main():
    # Initialize parser
    parser = argparse.ArgumentParser(description="Program to download tracks from Spotify via CLI")

    # Add arguments
    parser.add_argument("-link", nargs="+", help="URL of the Spotify track or playlist ")
    parser.add_argument("-outpath", nargs="?", default=os.getcwd(), help="Path to save the downloaded track")
    parser.add_argument("-sync", nargs="?", const="sync.json", help="Path of sync.json file to sync local playlist folders with Spotify playlists")
    parser.add_argument("-folder", nargs="?", default=True, help="Create a folder for the playlist(s)")


    args = parser.parse_args()
    # print(args)


    if args.sync:
        handle_sync_file(os.path.abspath(args.sync))


    # print(args.link)

    else:
        _, set_trackname_convention = trackname_convention()
        # resolve_path(args.outpath)
        for link in args.link:
            check_track_playlist(link, args.outpath, create_folder=args.folder, trackname_convention=set_trackname_convention)
            # if link_type == "track":
            #     download_track(link, args.outpath)

            # elif link_type == "playlist":
            #     download_playlist_tracks(link, args.outpath)

            # else:
            #     print(f"{link} is not a valid Spotify track or playlist link")
    
    print("\n" + "-"*25 + " Task complete ;) " + "-"*25 + "\n")




    # https://open.spotify.com/track/0b4a1iklB8w8gsE38nzyEx?si=d5986255e2464129

if __name__ == "__main__":
    logging.info("-" * 10 + "Program started" + "-" * 10)
    main()
    logging.info("-" * 10 + "Program ended" + "-" * 10)
import argparse
import os
import requests
import re
import eyed3
import logging
import json
from eyed3.id3.frames import ImageFrame
# Suppress warnings
eyed3.log.setLevel("ERROR")
logging.basicConfig(filename="spdl.log", filemode="a", level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', encoding="utf-8")
# logging.basicConfig(filename='app.log', level=logging.INFO)
CUSTOM_HEADER = {
    'Host': 'api.spotifydown.com',
    'Referer': 'https://spotifydown.com/',
    'Origin': 'https://spotifydown.com',
}

def check_track_playlist(link):
    # if "/track/" in link:
    if re.search(r".*spotify\.com\/track\/", link):
        return "track"
    # elif "/playlist/" in link:
    elif re.search(r".*spotify\.com\/playlist\/", link):
        return "playlist"
    else:
        return None
        # print(f"{link} is not a valid Spotify track or playlist link")

def  get_track_info(link):
    track_id = link.split("/")[-1].split("?")[0]
    response = requests.get(f"https://api.spotifydown.com/download/{track_id}", headers=CUSTOM_HEADER)
    response = response.json()
    # print(response['success'])
    # print(f"Song: {response['metadata']['title']}, Artist: {response['metadata']['artists']}, Album: {response['metadata']['album']}")
    # print(response['link'])

    return response

def attach_cover_art(trackname, cover_art, outpath):
    # print(outpath)
    audio_file = eyed3.load(os.path.join(outpath, f"{trackname}.mp3"))

    # https://stackoverflow.com/questions/38510694/how-to-add-album-art-to-mp3-file-using-python-3
    if (audio_file.tag is None):
        audio_file.initTag()

    audio_file.tag.images.set(ImageFrame.FRONT_COVER, cover_art.content, 'image/jpeg')
    audio_file.tag.save()

def save_audio(trackname, link, outpath):
    if os.path.exists(os.path.join(outpath, f"{trackname}.mp3")):
        print("\t This track already exists in the directory. Skipping download!")
        return False
    
    # filename = re.sub(r"[<>:\"/\\|?*]", "_", f"{trackname}.mp3")
    audio_response = requests.get(link)

    if audio_response.status_code == 200:
        with open(os.path.join(outpath, f"{trackname}.mp3"), "wb") as file:
            file.write(audio_response.content)
        return True

def resolve_path(outpath, playlist_folder=False):
    if not os.path.exists(outpath):
        if not playlist_folder:
            create_dir = input("Directory entered does not exist. Do you want to create it? (y/N): ")
        if playlist_folder or create_dir.lower() == "y":
            os.mkdir(outpath)
        else:
            print("Exiting program")
            exit()


def get_playlist_info(link):
    playlist_id = link.split("/")[-1].split("?")[0]
    response = requests.get(f"https://api.spotifydown.com/metadata/playlist/{playlist_id}", headers=CUSTOM_HEADER)
    response = response.json()
    playlist_name = response['title']
    if response['success']:
        print("-" * 40)
        print(f"Name: {playlist_name} by {response['artists']}")
    
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

    # print(len(set(track_list)))
    # print(len(dict.fromkeys(track_list)))

    return track_list, playlist_name

def sync_playlist_folders(sync_file):
    with open(sync_file, "r") as file:
        data_to_sync = json.load(file)
        # print(data_to_sync)
        for data in data_to_sync:
            print("Link: ", data['link'])
            print("Folder: ", data['create_folder'])

def download_track(track_link, outpath):
    print("\nTrack link identified")

    resp = get_track_info(track_link)
    trackname = resp['metadata']['title']
    trackname = re.sub(r"[<>:\"/\\|?*]", "_", trackname)
    # print(trackname)
    try:
        # raise Exception("Testing")
        save_status = save_audio(trackname, resp['link'], outpath)
        # print("Save status: ", save_status)
        if save_status:
            cover_art = requests.get(resp['metadata']['cover'])
            # print("------", trackname)
            attach_cover_art(trackname, cover_art, outpath)
    except Exception as e:
        logging.error(f"{trackname} --> {e}")
        print("Error: ", e)

def download_playlist_tracks(playlist_link, outpath):
    print("\nPlaylist link identified")
    resp_track_list, playlist_name = get_playlist_info(playlist_link)
    print(f"Downloading {len(resp_track_list)} tracks from {playlist_name}")
    print("-" * 40 )
    for index, track in enumerate(resp_track_list, 1):
        trackname = track['title']
        trackname = re.sub(r"[<>:\"/\\|?*]", "_", trackname)
        print(f"{index}/{len(resp_track_list)}: {trackname}")
        try:
            # raise Exception("Testing")
            resp = get_track_info(f"https://open.spotify.com/track/{track['id']}")
            resolve_path(os.path.join(outpath, playlist_name), playlist_folder=True)
            save_status = save_audio(trackname, resp['link'], os.path.join(outpath, playlist_name))
            if save_status:
                cover_art = requests.get(track['cover'])
                attach_cover_art(trackname, cover_art, os.path.join(outpath, playlist_name))
        except Exception as e:
            logging.error(f"{playlist_name}: {trackname} --> {e}")
            print("Error: ", e)

def handle_sync_file(sync_file):
    if (os.path.exists(sync_file)):
        print("Syncing local playlist folders to your Spotify account")
        sync_playlist_folders(sync_file)
    else:
        create_sync_file = input("Sync file does not exist. Do you want to create it? (y/N):")
        if create_sync_file.lower() == "y":
            data_for_sync_file = []
            while True:
                print("-" * 40)
                playlist_link = input("Playlist link (leave empty to finish): ")
                if not playlist_link:
                    break
                create_folder = input("Do you want to create a folder for this playlist? (y/N): ")
                download_location = input("Download location for tracks of this playlist (leave empty to default to current directory): ")
                data_for_sync_file.append({"link": playlist_link, "create_folder": create_folder.lower() == "y", "download_location": download_location if download_location else os.getcwd()})
            with open(sync_file, "w") as file:
                json.dump(data_for_sync_file, file)
            print("Sync file created successfully")
            print("-" * 40)
        else:
            print("Exiting program")
            exit()


def main():
    # Initialize parser
    parser = argparse.ArgumentParser(description="Program to download tracks from Spotify via CLI")

    # Add arguments
    parser.add_argument("-link", nargs="+", help="URL of the Spotify track")
    parser.add_argument("-outpath", nargs="?", default=os.getcwd(), help="Path to save the downloaded track")
    parser.add_argument("-sync", nargs="?", const="sync.json", help="Sync local playlist folders to your Spotify account")


    args = parser.parse_args()
    # print(args)

    if args.sync:
        handle_sync_file(os.path.abspath(args.sync))


    # print(args.link)

    else:
        resolve_path(args.outpath)
        for link in args.link:
            link_type = check_track_playlist(link)
            if link_type == "track":
                download_track(link, args.outpath)

            elif link_type == "playlist":
                download_playlist_tracks(link, args.outpath)

            else:
                print(f"{link} is not a valid Spotify track or playlist link")
    
    print("\n" + "-"*25 + " Task complete ;) " + "-"*25 + "\n")




    # https://open.spotify.com/track/0b4a1iklB8w8gsE38nzyEx?si=d5986255e2464129

main()
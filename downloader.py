import os
import re
import requests
import logging
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC, error, TRCK, TIT2, TALB, TPE1, TDRC
from config import NAME_SANITIZE_REGEX
from spotify_api import get_track_info, get_playlist_info
from utils import resolve_path, get_token, resolve_path

def attach_track_metadata(trackname, outpath, is_high_quality, metadata, track_number=0):
    trackname = re.sub(NAME_SANITIZE_REGEX, "_", trackname)
    filepath = os.path.join(outpath, f"{trackname}.mp3") if is_high_quality else os.path.join(outpath, "low_quality", f"{trackname}.mp3")
    try:
        # raise error("Testing")
        audio = MP3(filepath, ID3=ID3)
    except error as e:
        logging.error(f"Error loading MP3 file from {filepath} --> {e}")
        print(f"\tError loading MP3 file --> {e}")
        return

    if audio.tags is None:
        try:
            title = metadata['title']
            artist = metadata['artists']
            album = metadata['album']
            year = metadata['releaseDate']
            # audio.tags = ID3()
            audio.add_tags()
            audio.tags.add(TIT2(encoding=3, text=title))
            audio.tags.add(TPE1(encoding=3, text=artist))
            audio.tags.add(TALB(encoding=3, text=album))
            audio.tags.add(TDRC(encoding=3, text=year))
        except error as e:
            logging.error(f"Error adding ID3 tags to {filepath} --> {e}")
            print(f"\tError adding ID3 tags --> {e}")
            return 

    cover_art = requests.get(metadata['cover']).content
    audio.tags.add(
        APIC(
            encoding=1,
            mime='image/jpeg',
            type=3,
            desc=u'Cover',
            data=cover_art
        )
    )
    # Add track number
    # print(f"\t Adding track number: {track_number}")
    if track_number > 0:
        audio.tags.add(TRCK(encoding=3, text=str(track_number)))
    
    audio.save(filepath, v2_version=3, v1=2)

def save_audio(trackname, link, outpath):
    trackname = re.sub(NAME_SANITIZE_REGEX, "_", trackname)
    low_quality_path = os.path.join(outpath, "low_quality")
    
    if os.path.exists(os.path.join(outpath, f"{trackname}.mp3")) or \
       os.path.exists(os.path.join(low_quality_path, f"{trackname}.mp3")):
        logging.info(f"{trackname} already exists in the directory ({outpath}). Skipping download!")
        print("\tThis track already exists in the directory. Skipping download!")
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
            final_path = os.path.join(outpath, f"{trackname}.mp3")
            is_high_quality = True
        else:
            if not os.path.exists(low_quality_path):
                os.makedirs(low_quality_path)
            final_path = os.path.join(low_quality_path, f"{trackname}.mp3")
            is_high_quality = False
        
        os.rename(temp_file, final_path)
        # print(f"\t Saved {trackname} ({bitrate:.0f}kbps) to {'current' if is_high_quality else 'low_quality'} folder")
        return is_high_quality

    else:
        logging.error(f"Failed to download {trackname}. Status code: {audio_response.status_code}")
        print(f"\tFailed to download {trackname}. Status code: {audio_response.status_code}")
        return None

def check_track_playlist(link, outpath, create_folder, trackname_convention, token):
    # from utils import resolve_path  # local import to avoid circular dependency
    resolve_path(outpath)
    # if "/track/" in link:
    if re.search(r".*spotify\.com\/(?:intl-[a-zA-Z]{2}\/)?track\/", link):
        download_track(link, outpath, trackname_convention, token)
    # elif "/playlist/" in link:
    elif re.search(r".*spotify\.com\/playlist\/", link):
        download_playlist_tracks(link, outpath, create_folder, trackname_convention, token)
    # elif "/album/" in link:
    elif re.search(r".*spotify\.com\/album\/", link):
        download_playlist_tracks(link, outpath, create_folder, trackname_convention, mode='album', token=token)
    else:
        logging.error(f"{link} is not a valid Spotify track or playlist link")
        print(f"\n{link} is not a valid Spotify track or playlist link")

def download_track(track_link, outpath, trackname_convention, token, max_attempts=3):
    print("\nTrack link identified")

    resp = get_track_info(track_link, token)
    if resp["statusCode"] == 403:
        print("\tStatus code 403: Unauthorized access. Please provide a new token.")
        logging.error("Token expired, request new token")
        token = get_token(reset=True) # Resets the cache
        resp = get_track_info(track_link, token)  # Retry with new token
    if resp['success'] == False:
        print(f"Error: {resp['message']}")
        logging.error(f"Error: {resp['message']}")
        return

    trackname = f"{resp['metadata']['title']} - {resp['metadata']['artists']}"
    if trackname_convention == 2:
        trackname = f"{resp['metadata']['artists']} - {resp['metadata']['title']}"

    print(f"\nDownloading {trackname} to ({outpath})")
    for attempt in range(max_attempts):
        try:
            # raise Exception("Testing")
            is_high_quality = save_audio(trackname, resp['link'], outpath)
            if is_high_quality is not None:  # Check if download was successful
                # cover_art = requests.get(resp['metadata']['cover']).content
                attach_track_metadata(trackname, outpath, is_high_quality, resp['metadata'])
            break
        except Exception as e:
            logging.error(f"Attempt {attempt+1}/{max_attempts} - {trackname} --> {e}")
            print(f"\tAttempt {attempt+1}/{max_attempts} failed with error: ", e)
    remove_empty_files(outpath)

def check_existing_tracks(song_list_dict, outpath):
    existing_tracks = os.listdir(outpath)
    for track in existing_tracks:
        if track.endswith(".mp3"):
            track = track.split(".mp3")[0]
            if song_list_dict.get(track):
                song_list_dict.pop(track)
    
    return song_list_dict

def cleanup(outpath):
    for file in os.listdir(outpath):
        if file.endswith(".mp3") and os.path.getsize(os.path.join(outpath, file)) == 0:
            os.remove(os.path.join(outpath, file))

def remove_empty_files(outpath):
    # Check main directory
    cleanup(outpath)
    
    # Check low_quality directory if it exists
    low_quality_path = os.path.join(outpath, "low_quality")
    if os.path.exists(low_quality_path):
        cleanup(low_quality_path)

def download_playlist_tracks(playlist_link, outpath, create_folder, trackname_convention, token, max_attempts=3, mode='playlist'):
    # print(f"\n{mode[0].upper()}{mode[1:]} link identified")
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
    for index, trackname in enumerate(song_list_dict.keys(), 1):
        print(f"{index}/{len(song_list_dict)}: {trackname}")
        for attempt in range(max_attempts):
            try:
                # raise Exception("Testing")
                resp = get_track_info(song_list_dict[trackname].link, token)
                if resp["statusCode"] == 403:
                    print("\tStatus code 403: Unauthorized access. Please provide a new token.")
                    logging.error("Token expired. Requested new token")
                    token = get_token(reset=True) # Resets the cache
                    resp = get_track_info(song_list_dict[trackname].link, token)  # Retry with new token
                is_high_quality = save_audio(trackname, resp['link'], outpath)
                if is_high_quality is not None:  # Check if download was successful
                    cover_url = song_list_dict[trackname].cover
                    if not cover_url.startswith("http"):
                        cover_url = resp['metadata']['cover']
                    # cover_art = requests.get(cover_url).content
                    attach_track_metadata(trackname, outpath, is_high_quality, resp['metadata'], song_list_dict[trackname].track_number)
                    break # This break is here because we want to break out of the loop of the track was downloaded successfully
            except Exception as e:
                logging.error(f"Attempt {attempt+1}/{max_attempts} - {playlist_name}: {trackname} --> {e}")
                print(f"\t\tAttempt {attempt+1}/{max_attempts} failed with error: ", e)
            
    remove_empty_files(outpath)

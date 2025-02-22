import os
import requests
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC, error, TRCK, TIT2, TALB, TPE1, TDRC
import logging
import re

NAME_SANITIZE_REGEX = re.compile(r"[<>:\"\/\\|?*]")

def save_audio(trackname, link, outpath):
    trackname = re.sub(NAME_SANITIZE_REGEX, "_", trackname)
    low_quality_path = os.path.join(outpath, "low_quality")
    
    if os.path.exists(os.path.join(outpath, f"{trackname}.mp3")) or \
       os.path.exists(os.path.join(low_quality_path, f"{trackname}.mp3")):
        logging.info(f"{trackname} already exists in the directory ({outpath}). Skipping download!")
        print("\t This track already exists in the directory. Skipping download!")
        return None
    
    audio_response = requests.get(link)

    if audio_response.status_code == 200:
        temp_file = os.path.join(outpath, f"temp_{trackname}.mp3")
        with open(temp_file, "wb") as file:
            file.write(audio_response.content)
        
        audio = MP3(temp_file)
        bitrate = audio.info.bitrate / 1000
        
        if bitrate >= 320:
            final_path = os.path.join(outpath, f"{trackname}.mp3")
            is_high_quality = True
        else:
            if not os.path.exists(low_quality_path):
                os.makedirs(low_quality_path)
            final_path = os.path.join(low_quality_path, f"{trackname}.mp3")
            is_high_quality = False
        
        os.rename(temp_file, final_path)
        return is_high_quality

    else:
        logging.error(f"Failed to download {trackname}. Status code: {audio_response.status_code}")
        print(f"\t Failed to download {trackname}. Status code: {audio_response.status_code}")
        return None

def attach_track_metadata(trackname, outpath, is_high_quality, metadata, track_number=0):
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
            title = metadata['title']
            artist = metadata['artists']
            album = metadata['album']
            year = metadata['releaseDate']
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
            data=cover_art)
        )
    if track_number > 0:
        audio.tags.add(TRCK(encoding=3, text=str(track_number)))
    
    audio.save(filepath, v2_version=3, v1=2) 
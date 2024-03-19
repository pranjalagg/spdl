import argparse
import os
import requests
import re
import eyed3
from eyed3.id3.frames import ImageFrame

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
    print(response['success'])
    # print(f"Song: {response['metadata']['title']}, Artist: {response['metadata']['artists']}, Album: {response['metadata']['album']}")
    print(response['link'])

    return response

def attach_cover_art(trackname, cover_art, outpath):
    audio_file = eyed3.load(os.path.join(outpath, f"{trackname}.mp3"))

    if (audio_file.tag is None):
        audio_file.initTag()

    audio_file.tag.images.set(ImageFrame.FRONT_COVER, cover_art.content, 'image/jpeg')
    audio_file.tag.save()

def save_audio(trackname, link, outpath):
    filename = re.sub(r"[<>:\"/\\|?*]", "_", f"{trackname}.mp3")
    audio_response = requests.get(link)

    if audio_response.status_code == 200:
        with open(os.path.join(outpath, filename), "wb") as file:
            file.write(audio_response.content)

def main():
    # Initialize parser
    parser = argparse.ArgumentParser(description="Program to download tracks from Spotify via CLI")

    # Add arguments
    parser.add_argument("-link", nargs="+", help="URL of the Spotify track")
    parser.add_argument("outpath", nargs="?", default=os.getcwd(), help="Path to save the downloaded track")

    args = parser.parse_args()

    # print(args.link)

    for link in args.link:
        link_type = check_track_playlist(link)
        if link_type == "track":
            print("Track link identified")

            resp = get_track_info(link)
            trackname = resp['metadata']['title']
            print(trackname)
            save_audio(trackname, resp['link'], args.outpath)
            cover_art = requests.get(resp['metadata']['cover'])
            print(trackname)
            attach_cover_art(trackname, cover_art, args.outpath)

        elif link_type == "playlist":
            print("Playlist support coming soon")
        
        else:
            print(f"{link} is not a valid Spotify track or playlist link")




    # https://open.spotify.com/track/0b4a1iklB8w8gsE38nzyEx?si=d5986255e2464129

main()
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

def main():
    # Initialize parser
    parser = argparse.ArgumentParser(description="Program to download tracks from Spotify via CLI")

    # Add arguments
    parser.add_argument("-link", nargs="+", help="URL of the Spotify track")
    parser.add_argument("outpath", nargs="?", default=os.getcwd(), help="Path to save the downloaded track")

    args = parser.parse_args()

    print(args.link)

    for link in args.link:
        track_id = link.split("/")[-1].split("?")[0]
        response = requests.get(f"https://api.spotifydown.com/download/{track_id}", headers=CUSTOM_HEADER)
        # print(response.json())
        response = response.json()
        print(response['success'])
        print(f"Song: {response['metadata']['title']}, Artist: {response['metadata']['artists']}, Album: {response['metadata']['album']}")
        print(response['link'])

        trackname = response['metadata']['title']
        filename = re.sub(r"[<>:\"/\\|?*]", "_", f"{trackname}.mp3")

        audio_response = requests.get(response['link'])

        if audio_response.status_code == 200:
            with open(os.path.join(args.outpath, filename), "wb") as file:
                file.write(audio_response.content)

        # cover_art = response['metadata'].get('cover')
        # print(cover_art)
        print(response['metadata']['cover'])
        cover_art = requests.get(response['metadata']['cover'])

        # https://stackoverflow.com/questions/38510694/how-to-add-album-art-to-mp3-file-using-python-3
        audio_file = eyed3.load(os.path.join(args.outpath, filename))

        if (audio_file.tag is None):
            audio_file.initTag()
        
        audio_file.tag.images.set(ImageFrame.FRONT_COVER, cover_art.content, 'image/jpeg')

        audio_file.tag.save()




    # https://open.spotify.com/track/0b4a1iklB8w8gsE38nzyEx?si=d5986255e2464129

main()
import argparse
import os
import requests

CUSTOM_HEADER = {
    'Host': 'api.spotifydown.com',
    'Referer': 'https://spotifydown.com/',
    'Origin': 'https://spotifydown.com',
}

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
    print(response)



# https://open.spotify.com/track/0b4a1iklB8w8gsE38nzyEx?si=d5986255e2464129
import argparse
import os
import logging
from utils import resolve_path, trackname_convention, handle_sync_file
from spotify_api import check_track_playlist, get_token
from logging_setup import setup_logging

def main():
    parser = argparse.ArgumentParser(description="Program to download tracks from Spotify via CLI")
    parser.add_argument("-link", nargs="+", help="URL of the Spotify track or playlist ")
    parser.add_argument("-outpath", nargs="?", default=os.getcwd(), help="Path to save the downloaded track")
    parser.add_argument("-sync", nargs="?", const="sync.json", help="Path of sync.json file to sync local playlist folders with Spotify playlists")
    parser.add_argument("-folder", nargs="?", default=True, help="Create a folder for the playlist(s)")

    args = parser.parse_args()

    if args.sync:
        handle_sync_file(os.path.abspath(args.sync))
    else:
        token = get_token()
        _, set_trackname_convention = trackname_convention()
        for link in args.link:
            check_track_playlist(link, args.outpath, create_folder=args.folder, trackname_convention=set_trackname_convention, token=token)

    print("\n" + "-"*25 + " Task complete ;) " + "-"*25 + "\n")

if __name__ == "__main__":
    try:
        setup_logging()
        logging.info("-" * 10 + "Program started" + "-" * 10)
        main()
        logging.info("-" * 10 + "Program ended" + "-" * 10)
    except KeyboardInterrupt:
        print("\n------ Exiting program ------")
        logging.info("Program exited by user")

import argparse
import os
import logging
import sys
from utils import get_token, trackname_convention
from downloader import check_track_playlist
from sync import handle_sync_file

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

def main():
    # Initialize parser
    parser = argparse.ArgumentParser(description="Program to download tracks from Spotify via CLI")
    # Add arguments
    parser.add_argument("-link", nargs="+", help="URL of the Spotify track or playlist")
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
        # PRINT("HERE")
            check_track_playlist(link, args.outpath, create_folder=args.folder, trackname_convention=set_trackname_convention, token=token)
    
    print("\n" + "-"*25 + " Task complete ;) " + "-"*25 + "\n")

if __name__ == "__main__":
    try:
        logging.info("-" * 10 + "Program started" + "-" * 10)
        main()
        logging.info("-" * 10 + "Program ended" + "-" * 10)
    except KeyboardInterrupt:
        print("\n------ Exiting program ------")
        logging.info("Program exited by user")

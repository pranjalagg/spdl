import argparse
import os

# Initialize parser
parser = argparse.ArgumentParser(description="Program to download tracks from Spotify via CLI")

# Add arguments
parser.add_argument("-link", help="URL of the Spotify track")
parser.add_argument("outpath", nargs="?", default=os.getcwd(), help="Path to save the downloaded track")

args = parser.parse_args()

# print(args.link)
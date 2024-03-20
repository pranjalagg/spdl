# SPDL


## Description

This project is a tool to allow users to effortlessy download tracks and playlists fetched from Spotify, complete with metadata and album art.

> [!IMPORTANT]
>
> <sub>spdl is currently under development, so please expect frequent change to the way it works.</sub>


## Requirements and Installation
**System Requirements:**

* **Python**: `version 3.8` or above
* **Pip** package manager (Use `pip --version` to check, otherwise instructions to install pip can be found [here](https://pip.pypa.io/en/stable/installation/))

**Installation:**
1. Lauch your terminal instance and navigate to the `spdl` directory
2. Execute `pip install -r requirements.txt` to install the dependencies

## Usage
To download a track or playlist, run the main file using the following command:\
    `python main.py -link <link to your track or playlist>`\

Optionally the download directory can be specified using the `-outpath` flag. If no outpath is provided, downloads default to the current directory.

Example: `python main.py -link "https://open.spotify.com/track/6UVEJw6Ikma86JNK55KPkc?si=78dd2cdb137c4214" -outpath "F:/Songs/"`

_Note 1: You can paste more than one link one after the other seperated by space to download mutiple tracks at once_
_Note 2: For playlists, by default the program saves the tracks in a folder with the name of the playlist_

## Feedback
I would greatly appreciate your feedback after using the tool. Your insights helps it improve!

# SPDL


## Description

This project is a tool to allow users to effortlessy download tracks and playlists fetched from Spotify, complete with metadata and album art.

> [!IMPORTANT]
>
> <sub>spdl is currently under development, so please expect frequent changes to the way it works.</sub>


## Requirements and Installation
**System Requirements:**

* **Python**: `version 3.8` or above
* **Pip** package manager (Use `pip --version` to check, otherwise instructions to install pip can be found [here](https://pip.pypa.io/en/stable/installation/))

**Installation:**
1. Lauch your terminal instance and navigate to the `spdl` directory
2. Execute `pip install -r requirements.txt` to install the dependencies

## Usage
To download a track or playlist, run the main file using the following command:\
    `python main.py -link <link to your track or playlist>`

Optionally the download directory can be specified using the `-outpath` flag. If no outpath is provided, downloads default to the current directory.

Example: `python main.py -link "https://open.spotify.com/track/6UVEJw6Ikma86JNK55KPkc?si=78dd2cdb137c4214" -outpath "F:/Songs/"`

_Note 1: You can paste more than one link one after the other seperated by space to download mutiple tracks at once_
_Note 2: For playlists, by default the program saves the tracks in a folder with the name of the playlist_

## Different Use Cases
1. Download a single track or playlist:\
   `python main.py -link "https://open.spotify.com/track/6UVEJw6Ikma86JNK55KPkc?si=78dd2cdb137c4214"`
2. Download a single track or playlist at a specified location:
   `python main.py -link "https://open.spotify.com/track/6UVEJw6Ikma86JNK55KPkc?si=78dd2cdb137c4214" -outpath "F:/Songs"`
3. Download multiple  tracks / multiple playlists / or a combination:
   `python main.py -link "https://open.spotify.com/track/6UVEJw6Ikma86JNK55KPkc?si=78dd2cdb137c4214" "https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M?si=9fab95ad8ab349a7"`
4. Download multiple  tracks / multiple playlists / or a combination to a specified location:
   `python main.py -link "https://open.spotify.com/track/6UVEJw6Ikma86JNK55KPkc?si=78dd2cdb137c4214" "https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M?si=9fab95ad8ab349a7" -outpath "F:/Songs`
5. Download playlist(s) track in a single folder (default is to make playlist folder(s)):
   `python main.py -link "https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M?si=9fab95ad8ab349a7" -outpath "F:/Songs" -folder False`
6. Download / Sync Spotify playlists with local playlists when sync.json is not present or is in present directory:
   `python main.py -sync`
7. Download / Sync Spotify playlists with local playlists when sync.json is in a specified directory:
   `python main.py -sync "F:/Songs/sync.json"`


## Feedback
I would greatly appreciate your feedback after using the tool. Your insights helps it improve!

## Feature Request
As mentioned this project is under development and I would love to take feature requests. To request a feature, please raise it as an issue under the [Issues](https://github.com/pranjalagg/spdl/issues) tab.

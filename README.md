# SPDL


## Description

This project is a tool that allows users to effortlessly download tracks and playlists fetched from Spotify, complete with metadata and album art.

> [!IMPORTANT]
> Due to the new updates to the API, a token is needed every once in a while. Thus, every time prompted, you'll have to provide the token. Get the token using the below steps:
> 1. Go to https://spotifydown.com/ and open the "Network" tab in the browser devtools (right click > Inspect > navigate to the Network tab or use the key combination: `Ctrl + Shift + I`)
> 2. If you see a lot of things in the Network tab, press `Ctrl + L` to clear all of those
> 3. While the Network tab is open, paste any URL of a track from Spotify and press the download button. You will see some activity in the Network tab.
> 4. Now, click the download button beside the track name on the UI. You will again see some activity in the Network tab.
> 5. _(Optional)_ Filter to only show `fetch` requests (from the "Type" column)
> 6. Click on the `fetch` request that came after clicking the download button in Step 4.
> 
>    <img width="831" alt="image" src="https://github.com/user-attachments/assets/fe258188-36d1-4cfe-9d29-740d9b362b98" />
> 8. Copy only the token part ( ...?token=***0.SA6dCVY...*** ) [Yellow portion of text only in the screenshot below]
> 
>    <img width="797" alt="image" src="https://github.com/user-attachments/assets/37b9b327-e959-4e90-a411-4c591bb28cbd" />
> 
> <sub>spdl is currently under development, so please expect frequent changes to the way it works.</sub>


## Requirements and Installation
**System Requirements:**

* **Python**: `version 3.8` or above
* **Pip** package manager (Use `pip --version` to check if you have it, otherwise instructions to install pip can be found [here](https://pip.pypa.io/en/stable/installation/))

**Installation:**
1. Lauch your terminal instance and navigate to the `spdl` directory
2. Execute `pip install -r requirements.txt` to install the dependencies

## Usage
To download a track or playlist, run the main file using the following command:
```ps1
python main.py -link <link to your track or playlist>
```

Optionally the download directory can be specified using the `-outpath` flag. If no outpath is provided, downloads default to the current directory.

Example:
```ps1
python main.py -link "https://open.spotify.com/track/6UVEJw6Ikma86JNK55KPkc?si=78dd2cdb137c4214" -outpath "F:/Songs/"
```

_Note 1: You can paste more than one link one after the other separated by space to download multiple tracks at once_
_Note 2: For playlists, by default the program saves the tracks in a folder with the name of the playlist_

## Different Use Cases
1. Download a single track or playlist:
   ```ps1
   python main.py -link "https://open.spotify.com/track/6UVEJw6Ikma86JNK55KPkc?si=78dd2cdb137c4214"
   ```
2. Download a single track or playlist at a specified location:
   ```ps1
   python main.py -link "https://open.spotify.com/track/6UVEJw6Ikma86JNK55KPkc?si=78dd2cdb137c4214" -outpath "F:/Songs"
   ```
3. Download multiple  tracks / multiple playlists / or a combination:
   ```ps1
   python main.py -link "https://open.spotify.com/track/6UVEJw6Ikma86JNK55KPkc?si=78dd2cdb137c4214" "https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M?si=9fab95ad8ab349a7"
   ```
4. Download multiple  tracks / multiple playlists / or a combination to a specified location:
   ```ps1
   python main.py -link "https://open.spotify.com/track/6UVEJw6Ikma86JNK55KPkc?si=78dd2cdb137c4214" "https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M?si=9fab95ad8ab349a7" -outpath "F:/Songs
   ```
5. Download playlist(s) track in a single folder (default is to make playlist folder(s)):
   ```ps1
   python main.py -link "https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M?si=9fab95ad8ab349a7" -outpath "F:/Songs" -folder False
   ```
6. Download / Sync Spotify playlists with local playlists when sync.json is not present or is in present directory:
   ```ps1
   python main.py -sync
   ```
7. Download / Sync Spotify playlists with local playlists when sync.json is in a specified directory:
   ```ps1
    python main.py -sync "F:/Songs/sync.json"
   ```

### sync.json Structure
The first time you try to run the sync command, the program will ask you for the playlist info and the sync.json will be created automatically. If you wish to manually create a sync.json file or modify the existing one, use the following structure:
```json
[
    {
        "name": "<Playlist Name 1>",
        "link": "<Playlist Link>",
        "create_folder": true,
        "download_location": "F:/Songs"
    },
    {
        "name": "<Playlist Name 2>",
        "link": "<Playlist Link>",
        "create_folder": true,
        "download_location": "F:/Songs"
    }
]
```


## Feedback
I would greatly appreciate your feedback after using the tool. Your insights helps it improve!

## Feature Request/Contributions
I would not be able to take in feature requests at this point, but I would love to accept contributions/pull requests if anyone is willing to work on any issue.

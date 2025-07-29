# SPDL - Spotify Downloader

A command-line tool to download songs from Spotify with high-quality audio support.

## Features

- 🎵 Download individual tracks and playlists
- 🔄 Sync playlists automatically
- 🎚️ Multiple quality options (128kbps, 192kbps, 320kbps)
- 🔑 Token-based authentication to bypass Cloudflare protection
- 📁 Organized file naming and directory structure
- 🚀 Fast and efficient downloads

## Installation

1. Clone the repository:
```bash
git clone https://github.com/pranjalagg/spdl.git
cd spdl
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Quick Start

### 1. Setup Token (Required)

Due to Cloudflare protection, you need to obtain a token from spotifydown.com:

```bash
python main.py setup
```

Follow the instructions to get your token. This is a one-time setup.

### 2. Download a Single Track

```bash
python main.py download "https://open.spotify.com/track/your-track-id"
```

### 3. Download a Playlist

```bash
python main.py playlist "https://open.spotify.com/playlist/your-playlist-id"
```

### 4. Sync All Playlists

```bash
python main.py sync
```

## Usage

### Commands

- `setup` - Setup token for SpotifyDown API
- `download <url>` - Download a single track
- `playlist <url>` - Download all tracks from a playlist
- `sync` - Sync all playlists from sync.json

### Options

- `--quality <128|192|320>` - Set download quality (default: 320)
- `--verbose` - Enable verbose logging

### Examples

```bash
# Setup token (first time only)
python main.py setup

# Download a track with 192kbps quality
python main.py download "https://open.spotify.com/track/4iV5W9uYEdYUVa79Axb7Rh" --quality 192

# Download a playlist
python main.py playlist "https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M"

# Sync all playlists
python main.py sync

# Enable verbose logging
python main.py download "https://open.spotify.com/track/4iV5W9uYEdYUVa79Axb7Rh" --verbose
```

## Token Setup Instructions

### Method 1: Browser Developer Tools

1. Visit [spotifydown.com](https://spotifydown.com)
2. Open browser developer tools (F12)
3. Go to Network tab
4. Try to download any song
5. Look for requests to `api.spotifydown.com`
6. Find the 'token' parameter in the request URL
7. Copy the token value

### Method 2: Direct URL Extraction

1. Go to [spotifydown.com](https://spotifydown.com)
2. Complete any captcha if needed
3. Try to download a song
4. Check the download URL for the token parameter
5. Copy the token from the URL

### Method 3: Environment Variable

You can also set the token as an environment variable:

```bash
export SPOTIFYDOWN_TOKEN="your_token_here"
python main.py download "https://open.spotify.com/track/your-track-id"
```

## Configuration

### File Naming Patterns

The application supports custom file naming patterns:

- `default` - `{artist} - {title}`
- `track_number` - `{track_number:02d} - {title}`
- `artist_title` - `{artist} - {title}`
- `title_only` - `{title}`
- `artist_title_number` - `{track_number:02d} - {artist} - {title}`

### Quality Options

- `320` - 320kbps (highest quality)
- `192` - 192kbps (medium quality)
- `128` - 128kbps (standard quality)

## Troubleshooting

### Common Issues

1. **Token Invalid**: Run `python main.py setup` to update your token
2. **Download Failures**: Check your internet connection and try again
3. **Cloudflare Protection**: Update your token using the setup command

### Error Messages

- `Token validation failed`: Run setup to get a new token
- `Invalid Spotify URL`: Check the URL format
- `Download failed`: Try again or check your token

## File Structure

```
spdl/
├── main.py              # Main application
├── downloader.py        # Download functionality
├── spotify_api.py       # Spotify API integration
├── sync.py             # Playlist synchronization
├── utils.py            # Utility functions
├── config.py           # Configuration
├── models.py           # Data models
├── requirements.txt    # Dependencies
├── sync.json          # Playlist configuration
├── .token             # Token storage (auto-generated)
└── downloads/         # Downloaded files
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Disclaimer

This tool is for educational purposes only. Please respect copyright laws and only download music you have the right to access.

## Changelog

### v2.0.0
- Added token-based authentication
- Improved error handling
- Better user experience
- Enhanced documentation

### v1.0.0
- Initial release
- Basic download functionality
- Playlist support
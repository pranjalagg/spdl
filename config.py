import os
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).parent

# Download directory
DOWNLOAD_DIR = BASE_DIR / "downloads"

# Sync file path
SYNC_FILE = BASE_DIR / "sync.json"

# Spotify API configuration
SPOTIFY_CLIENT_ID = "your_client_id_here"
SPOTIFY_CLIENT_SECRET = "your_client_secret_here"

# SpotifyDown API configuration
SPOTIFYDOWN_BASE_URL = "https://api.spotifydown.com"
SPOTIFYDOWN_DOWNLOAD_URL = f"{SPOTIFYDOWN_BASE_URL}/download"

# Token configuration for bypassing Cloudflare
SPOTIFYDOWN_TOKEN = os.getenv("SPOTIFYDOWN_TOKEN", "")
TOKEN_FILE = BASE_DIR / ".token"

# Request headers
CUSTOM_HEADER = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
}

# Retry configuration
MAX_RETRIES = 3
RETRY_DELAY = 2  # seconds

# Download quality options
QUALITY_OPTIONS = {
    "320": "320kbps",
    "192": "192kbps", 
    "128": "128kbps"
}

# Default quality
DEFAULT_QUALITY = "320"

# File naming patterns
NAMING_PATTERNS = {
    "default": "{artist} - {title}",
    "track_number": "{track_number:02d} - {title}",
    "artist_title": "{artist} - {title}",
    "title_only": "{title}",
    "artist_title_number": "{track_number:02d} - {artist} - {title}"
}

DEFAULT_NAMING_PATTERN = "default"
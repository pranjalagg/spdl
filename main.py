#!/usr/bin/env python3
"""
SPDL - Spotify Downloader
A command-line tool to download songs from Spotify
"""

import argparse
import sys
import logging
from pathlib import Path
from typing import List, Optional

from config import DOWNLOAD_DIR, SYNC_FILE
from spotify_api import spotify_api
from downloader import Downloader
from sync import SyncManager
from utils import setup_logging, validate_spotify_url

def setup_token() -> bool:
    """Setup token for SpotifyDown API"""
    print("🔑 Token Setup for SpotifyDown API")
    print("=" * 50)
    
    # Check if token already exists
    if spotify_api.token:
        print(f"✅ Token found: {spotify_api.token[:10]}...")
        if spotify_api.validate_token():
            print("✅ Token is valid!")
            return True
        else:
            print("❌ Token appears to be invalid")
    
    print("\n📋 Instructions to get a token:")
    print(spotify_api.get_token_instructions())
    
    # Get token from user
    token = input("\n🔑 Enter your SpotifyDown token: ").strip()
    
    if not token:
        print("❌ No token provided. Setup cancelled.")
        return False
    
    try:
        spotify_api.set_token(token)
        if spotify_api.validate_token():
            print("✅ Token setup successful!")
            return True
        else:
            print("❌ Token validation failed. Please check your token.")
            return False
    except Exception as e:
        print(f"❌ Error setting up token: {e}")
        return False

def download_single_track(url: str, quality: str = "320") -> bool:
    """Download a single track"""
    try:
        if not validate_spotify_url(url):
            print("❌ Invalid Spotify URL")
            return False
        
        # Validate token before downloading
        if not spotify_api.validate_token():
            print("❌ Token validation failed. Please run setup first.")
            return False
        
        downloader = Downloader()
        success = downloader.download_track(url, quality)
        
        if success:
            print("✅ Download completed successfully!")
        else:
            print("❌ Download failed")
        
        return success
        
    except Exception as e:
        print(f"❌ Error downloading track: {e}")
        return False

def download_playlist(url: str, quality: str = "320") -> bool:
    """Download all tracks from a playlist"""
    try:
        if not validate_spotify_url(url):
            print("❌ Invalid Spotify URL")
            return False
        
        # Validate token before downloading
        if not spotify_api.validate_token():
            print("❌ Token validation failed. Please run setup first.")
            return False
        
        downloader = Downloader()
        success = downloader.download_playlist(url, quality)
        
        if success:
            print("✅ Playlist download completed successfully!")
        else:
            print("❌ Playlist download failed")
        
        return success
        
    except Exception as e:
        print(f"❌ Error downloading playlist: {e}")
        return False

def sync_playlists() -> bool:
    """Sync playlists from sync.json"""
    try:
        # Validate token before syncing
        if not spotify_api.validate_token():
            print("❌ Token validation failed. Please run setup first.")
            return False
        
        sync_manager = SyncManager()
        success = sync_manager.sync_all_playlists()
        
        if success:
            print("✅ Sync completed successfully!")
        else:
            print("❌ Sync failed")
        
        return success
        
    except Exception as e:
        print(f"❌ Error syncing playlists: {e}")
        return False

def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description="SPDL - Spotify Downloader",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py setup                    # Setup token
  python main.py download <url>          # Download single track
  python main.py playlist <url>          # Download playlist
  python main.py sync                    # Sync all playlists
  python main.py download <url> --quality 192  # Download with specific quality
        """
    )
    
    parser.add_argument(
        "command",
        choices=["setup", "download", "playlist", "sync"],
        help="Command to execute"
    )
    
    parser.add_argument(
        "url",
        nargs="?",
        help="Spotify URL (required for download/playlist commands)"
    )
    
    parser.add_argument(
        "--quality",
        choices=["128", "192", "320"],
        default="320",
        help="Download quality (default: 320)"
    )
    
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging"
    )
    
    args = parser.parse_args()
    
    # Setup logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    setup_logging(log_level)
    
    # Create download directory
    DOWNLOAD_DIR.mkdir(exist_ok=True)
    
    # Execute command
    if args.command == "setup":
        success = setup_token()
        sys.exit(0 if success else 1)
    
    elif args.command == "download":
        if not args.url:
            print("❌ URL is required for download command")
            sys.exit(1)
        success = download_single_track(args.url, args.quality)
        sys.exit(0 if success else 1)
    
    elif args.command == "playlist":
        if not args.url:
            print("❌ URL is required for playlist command")
            sys.exit(1)
        success = download_playlist(args.url, args.quality)
        sys.exit(0 if success else 1)
    
    elif args.command == "sync":
        success = sync_playlists()
        sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
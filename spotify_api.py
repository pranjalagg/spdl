import requests
import json
import time
import logging
from typing import Dict, Optional, Any
from config import (
    SPOTIFYDOWN_BASE_URL, 
    SPOTIFYDOWN_DOWNLOAD_URL, 
    CUSTOM_HEADER, 
    SPOTIFYDOWN_TOKEN,
    TOKEN_FILE,
    MAX_RETRIES,
    RETRY_DELAY
)

logger = logging.getLogger(__name__)

class SpotifyAPI:
    def __init__(self):
        self.token = self._load_token()
        self.session = requests.Session()
        self.session.headers.update(CUSTOM_HEADER)
    
    def _load_token(self) -> str:
        """Load token from environment variable or token file"""
        # First try environment variable
        if SPOTIFYDOWN_TOKEN:
            return SPOTIFYDOWN_TOKEN
        
        # Then try token file
        if TOKEN_FILE.exists():
            try:
                with open(TOKEN_FILE, 'r') as f:
                    return f.read().strip()
            except Exception as e:
                logger.warning(f"Failed to load token from file: {e}")
        
        return ""
    
    def _save_token(self, token: str) -> None:
        """Save token to file"""
        try:
            with open(TOKEN_FILE, 'w') as f:
                f.write(token)
            logger.info("Token saved to file")
        except Exception as e:
            logger.error(f"Failed to save token: {e}")
    
    def _make_request(self, url: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """Make HTTP request with retry logic and token support"""
        for attempt in range(MAX_RETRIES):
            try:
                # Add token to params if available
                if self.token and params is None:
                    params = {}
                if self.token:
                    params['token'] = self.token
                
                response = self.session.get(url, params=params, timeout=30)
                
                # Check if token is invalid (401 or 403)
                if response.status_code in [401, 403] and self.token:
                    logger.warning(f"Token may be invalid (status {response.status_code}). Please update your token.")
                    # Don't retry with invalid token
                    break
                
                # Check for Cloudflare protection
                if response.status_code == 403 and "cloudflare" in response.text.lower():
                    logger.error("Cloudflare protection detected. Please update your token.")
                    break
                
                response.raise_for_status()
                return response.json()
                
            except requests.exceptions.RequestException as e:
                logger.warning(f"Attempt {attempt + 1}/{MAX_RETRIES} failed: {e}")
                if attempt < MAX_RETRIES - 1:
                    time.sleep(RETRY_DELAY)
                else:
                    raise
        
        raise Exception(f"Failed to make request after {MAX_RETRIES} attempts")
    
    def get_track_info(self, link: str) -> Dict[str, Any]:
        """Get track information from SpotifyDown API with token support"""
        try:
            track_id = link.split("/")[-1].split("?")[0]
            url = f"{SPOTIFYDOWN_DOWNLOAD_URL}/{track_id}"
            
            logger.info(f"Fetching track info for {track_id}")
            response_data = self._make_request(url)
            
            if not response_data.get('success', False):
                error_msg = response_data.get('message', 'Unknown error')
                logger.error(f"API returned error: {error_msg}")
                raise Exception(f"API error: {error_msg}")
            
            return response_data
            
        except Exception as e:
            logger.error(f"Failed to get track info: {e}")
            raise
    
    def validate_token(self) -> bool:
        """Validate if the current token is working"""
        if not self.token:
            logger.warning("No token available")
            return False
        
        try:
            # Try to get info for a test track (using a popular song)
            test_url = "https://open.spotify.com/track/4iV5W9uYEdYUVa79Axb7Rh"  # Test track
            self.get_track_info(test_url)
            logger.info("Token validation successful")
            return True
        except Exception as e:
            logger.warning(f"Token validation failed: {e}")
            return False
    
    def set_token(self, token: str) -> None:
        """Set a new token"""
        self.token = token.strip()
        self._save_token(self.token)
        logger.info("Token updated")
    
    def get_token_instructions(self) -> str:
        """Get instructions for obtaining a token"""
        return """
To get a SpotifyDown token:

1. Visit https://spotifydown.com
2. Open browser developer tools (F12)
3. Go to Network tab
4. Try to download any song
5. Look for requests to api.spotifydown.com
6. Find the 'token' parameter in the request URL
7. Copy the token value
8. Use this token in the application

Alternatively, you can:
1. Go to https://spotifydown.com
2. Complete the captcha if needed
3. Try to download a song
4. Check the download URL for the token parameter
5. Copy the token from the URL

The token will be saved automatically for future use.
"""

# Global instance
spotify_api = SpotifyAPI()
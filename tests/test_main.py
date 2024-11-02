import pytest
from unittest.mock import patch, MagicMock
import requests
from ..main import (
    Song,
    check_track_playlist,
    get_track_info,
    attach_cover_art,
    save_audio,
    resolve_path,
    make_unique_song_objects,
    dict_unique,
    get_playlist_info,
    sync_playlist_folders,
    download_track,
    check_existing_tracks,
    cleanup, remove_empty_files,
    download_playlist_tracks,
    handle_sync_file,
    trackname_convention,
    NAME_SANITIZE_REGEX
)

@pytest.fixture
def sample_track():
    return Song(
        title="Sample Track",
        artists=["Sample Artist1", "Sample Artist2"],
        album="Sample Album",
        cover="https://example.com/sample_cover.jpg",
        link="https://example.com/sample_track.mp3",
        track_number=1
    )

@pytest.fixture
def sample_track_response():
    return {
        "success": True,
        "metadata": {
            "title": "Sample Track",
            "artists": ["Sample Artist1", "Sample Artist2"],
            "album": "Sample Album",
            "cover": "https://example.com/sample_cover.jpg",
        },
        "link": "https://example.com/sample_track.mp3"
    }

def test_song_creation(sample_track):
    assert sample_track.title == "Sample Track"
    assert sample_track.artists == ["Sample Artist1", "Sample Artist2"]
    assert sample_track.album == "Sample Album"
    assert sample_track.cover == "https://example.com/sample_cover.jpg"
    assert sample_track.link == "https://example.com/sample_track.mp3"
    assert sample_track.track_number == 1

def test_name_sanitize_regex():
    dirty_name = "Test: Sample? Track* (feat. Invalid/ Characters)"
    clean_name = NAME_SANITIZE_REGEX.sub("_", dirty_name)
    assert clean_name == "Test_ Sample_ Track_ (feat. Invalid_ Characters)"
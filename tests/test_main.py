import pytest
from unittest.mock import patch, MagicMock, mock_open, call
import requests
from ..main import *

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

@patch('main.requests.get')
def test_get_track_info(mock_get):
    track_info = {'title': 'Test Song', 'artists': 'Test Artist'}
    mock_get.return_value.json.return_value = track_info

    result = get_track_info("https://open.spotify.com/track/12345")
    assert result == track_info
    mock_get.assert_called_once_with("https://api.spotifydown.com/download/12345", headers=CUSTOM_HEADER)


def test_dict_unique():
    songs = [
        Song("Song1", "Artist1", "Album1", "cover1", "link1", 1),
        Song("Song2", "Artist2", "Album2", "cover2", "link2", 2),
        Song("Song1", "Artist1", "Album1", "cover1", "link1", 1)  # Duplicate
    ]
    unique_songs, duplicates = dict_unique(songs, trackname_convention=1)
    assert len(unique_songs) == 2
    assert len(duplicates) == 1


def test_make_unique_song_objects():
    track_list = [
        {'title': 'Song1', 'artists': 'Artist1', 'album': 'Album1', 'id': '123'},
        {'title': 'Song2', 'artists': 'Artist2', 'album': 'Album2', 'id': '456'}
    ]
    unique_songs = make_unique_song_objects(track_list, 1, "Album1", mode='album')
    assert len(unique_songs) == 2

@patch("main.os.path.exists")
@patch("main.os.mkdir")
def test_resolve_path(mock_mkdir, mock_exists):
    mock_exists.return_value = False
    with patch("builtins.input", return_value="y"):
        resolve_path("output/path")
        mock_mkdir.assert_called_once_with("output/path")

@patch("main.requests.get")
def test_get_playlist_info(mock_get):
    mock_get.return_value.json.side_effect = [
        {'title': 'Test Playlist', 'artists': 'Test Artist', 'success': True},
        {'trackList': [{'title': 'Song1', 'artists': 'Artist1', 'id': '123'}], 'nextOffset': None}
    ]

    songs, playlist_name = get_playlist_info("https://open.spotify.com/playlist/12345", 1, 'playlist')
    assert playlist_name == "Test Playlist"
    assert len(songs) == 1
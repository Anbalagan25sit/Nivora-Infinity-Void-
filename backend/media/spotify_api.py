"""
Spotify Web API client for playback control, search, and playlists.
Requires .env: SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET, SPOTIFY_REFRESH_TOKEN.

Get refresh token: run get_spotify_token.py (one-time) and add SPOTIFY_REFRESH_TOKEN to .env.
"""

import logging
import os
from typing import Any

import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")

logger = logging.getLogger(__name__)

TOKEN_URL = "https://accounts.spotify.com/api/token"
API_BASE = "https://api.spotify.com/v1"
SCOPES = (
    "user-modify-playback-state user-read-playback-state user-read-currently-playing "
    "playlist-modify-public playlist-modify-private user-library-read user-library-modify user-read-email"
)


def _env(key: str, default: str = "") -> str:
    return (os.getenv(key) or "").strip()


def is_configured() -> bool:
    return bool(
        _env("SPOTIFY_CLIENT_ID")
        and _env("SPOTIFY_CLIENT_SECRET")
        and _env("SPOTIFY_REFRESH_TOKEN")
    )


def get_access_token() -> str | None:
    """Get a valid access token using refresh token."""
    client_id = _env("SPOTIFY_CLIENT_ID")
    client_secret = _env("SPOTIFY_CLIENT_SECRET")
    refresh_token = _env("SPOTIFY_REFRESH_TOKEN")
    if not all([client_id, client_secret, refresh_token]):
        return None
    try:
        r = requests.post(
            TOKEN_URL,
            data={
                "grant_type": "refresh_token",
                "refresh_token": refresh_token,
                "client_id": client_id,
            },
            auth=(client_id, client_secret),
            timeout=10,
        )
        r.raise_for_status()
        return r.json().get("access_token")
    except Exception as e:
        logger.warning("Spotify token refresh failed: %s", e)
        return None


def _headers() -> dict[str, str]:
    token = get_access_token()
    if not token:
        return {}
    return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}


def _get(path: str, params: dict | None = None) -> dict | None:
    if not _headers():
        return None
    try:
        r = requests.get(API_BASE + path, headers=_headers(), params=params or {}, timeout=10)
        if r.status_code == 204:
            return {}
        r.raise_for_status()
        return r.json() if r.content else {}
    except Exception as e:
        logger.warning("Spotify API GET %s: %s", path, e)
        return None


def _put(path: str, json: dict | None = None) -> bool:
    if not _headers():
        return False
    try:
        r = requests.put(API_BASE + path, headers=_headers(), json=json or {}, timeout=10)
        if r.status_code in (200, 204):
            return True
        r.raise_for_status()
        return False
    except Exception as e:
        logger.warning("Spotify API PUT %s: %s", path, e)
        return False


def _post(path: str, json: dict | None = None) -> dict | None:
    if not _headers():
        return None
    try:
        r = requests.post(API_BASE + path, headers=_headers(), json=json or {}, timeout=10)
        if r.status_code == 204:
            return {}
        r.raise_for_status()
        return r.json() if r.content else {}
    except Exception as e:
        logger.warning("Spotify API POST %s: %s", path, e)
        return None


# ---------------------------------------------------------------------------
# Playback control
# ---------------------------------------------------------------------------


def play(context_uri: str | None = None, uris: list[str] | None = None) -> bool:
    """Start or resume playback. Optionally play context_uri (e.g. spotify:playlist:xxx) or uris (track uris)."""
    body: dict[str, Any] = {}
    if context_uri:
        body["context_uri"] = context_uri
    if uris:
        body["uris"] = uris
    return _put("/me/player/play", json=body if body else None)


def pause() -> bool:
    return _put("/me/player/pause")


def next_track() -> bool:
    if not _headers():
        return False
    try:
        r = requests.post(API_BASE + "/me/player/next", headers=_headers(), timeout=10)
        return r.status_code in (200, 204)
    except Exception as e:
        logger.warning("Spotify next: %s", e)
        return False


def previous_track() -> bool:
    if not _headers():
        return False
    try:
        r = requests.post(API_BASE + "/me/player/previous", headers=_headers(), timeout=10)
        return r.status_code in (200, 204)
    except Exception as e:
        logger.warning("Spotify previous: %s", e)
        return False


def set_volume(percent: int) -> bool:
    """Set volume 0-100."""
    percent = max(0, min(100, percent))
    try:
        r = requests.put(
            API_BASE + "/me/player/volume",
            headers=_headers(),
            params={"volume_percent": percent},
            timeout=10,
        )
        return r.status_code in (200, 204)
    except Exception as e:
        logger.warning("Spotify volume: %s", e)
        return False


def set_shuffle(state: bool) -> bool:
    try:
        r = requests.put(
            API_BASE + "/me/player/shuffle",
            headers=_headers(),
            params={"state": str(state).lower()},
            timeout=10,
        )
        return r.status_code in (200, 204)
    except Exception as e:
        logger.warning("Spotify shuffle: %s", e)
        return False


def toggle_shuffle() -> bool:
    """Toggle shuffle mode. Returns True on success."""
    try:
        # Get current playback state to check shuffle status
        data = get_current_playback()
        if not data:
            return False
        current_shuffle = data.get("shuffle_state", False)
        return set_shuffle(not current_shuffle)
    except Exception as e:
        logger.warning("Spotify toggle shuffle: %s", e)
        return False


def set_repeat(state: str) -> bool:
    """state: 'track' | 'context' | 'off'"""
    try:
        r = requests.put(
            API_BASE + "/me/player/repeat",
            headers=_headers(),
            params={"state": state},
            timeout=10,
        )
        return r.status_code in (200, 204)
    except Exception as e:
        logger.warning("Spotify repeat: %s", e)
        return False


def toggle_repeat() -> bool:
    """Cycle through repeat modes: off -> context -> track -> off."""
    try:
        data = get_current_playback()
        if not data:
            return False
        current_repeat = data.get("repeat_state", "off")

        # Cycle: off -> context -> track -> off
        next_state = {"off": "context", "context": "track", "track": "off"}.get(current_repeat, "off")
        return set_repeat(next_state)
    except Exception as e:
        logger.warning("Spotify toggle repeat: %s", e)
        return False


def get_current_playback() -> dict | None:
    """Get currently playing track and context. Returns None if no API or nothing playing."""
    data = _get("/me/player/currently-playing")
    if not data:
        data = _get("/me/player")  # fallback to player state
    return data


def get_now_playing_text() -> str:
    """Human-readable 'Now playing: Song - Artist (Album)' or 'Nothing playing'."""
    data = get_current_playback()
    if not data or not data.get("item"):
        return "Nothing is playing right now."
    item = data["item"]
    name = item.get("name") or "Unknown"
    artists = ", ".join(a.get("name", "") for a in item.get("artists", []))
    album = (item.get("album") or {}).get("name") or ""
    return f"Now playing: {name} by {artists}" + (f" (from {album})" if album else "")


# ---------------------------------------------------------------------------
# Search and play
# ---------------------------------------------------------------------------


def search(q: str, type: str = "track,album,artist,playlist", limit: int = 5) -> dict | None:
    """Search tracks, albums, artists, playlists. type comma-separated."""
    return _get("/search", params={"q": q, "type": type, "limit": limit})


def search_and_play_track(query: str) -> tuple[bool, str]:
    """Search for a track and start playing the first result. Returns (success, message)."""
    data = search(query, type="track", limit=1)
    if not data:
        return False, "Spotify API not configured or search failed. Open Spotify and try again."
    tracks = (data.get("tracks") or {}).get("items") or []
    if not tracks:
        return False, f"No tracks found for '{query}'."
    uri = tracks[0].get("uri")
    if not uri:
        return False, "Could not get track URI."
    if play(uris=[uri]):
        name = tracks[0].get("name", "Track")
        artist = (tracks[0].get("artists") or [{}])[0].get("name", "")
        return True, f"Playing: {name}" + (f" by {artist}" if artist else "")
    return False, "Playback failed. Is Spotify open and a device active?"


def search_and_play_playlist(query: str) -> tuple[bool, str]:
    """Search playlists and play the first result."""
    data = search(query, type="playlist", limit=1)
    if not data:
        return False, "Spotify API not configured or search failed."
    playlists = (data.get("playlists") or {}).get("items") or []
    if not playlists:
        return False, f"No playlists found for '{query}'."
    uri = playlists[0].get("uri")
    if not uri:
        return False, "Could not get playlist URI."
    if play(context_uri=uri):
        name = playlists[0].get("name", "Playlist")
        return True, f"Playing playlist: {name}"
    return False, "Playback failed. Is Spotify open and a device active?"


def search_and_play_artist(query: str) -> tuple[bool, str]:
    """Search artists and play artist's top tracks (via first album or top tracks)."""
    data = search(query, type="artist", limit=1)
    if not data:
        return False, "Spotify API not configured or search failed."
    artists = (data.get("artists") or {}).get("items") or []
    if not artists:
        return False, f"No artist found for '{query}'."
    uri = artists[0].get("uri")
    if not uri:
        return False, "Could not get artist URI."
    if play(context_uri=uri):
        name = artists[0].get("name", "Artist")
        return True, f"Playing artist: {name}"
    return False, "Playback failed. Is Spotify open and a device active?"


def search_and_play_album(query: str) -> tuple[bool, str]:
    """Search albums and play the first result."""
    data = search(query, type="album", limit=1)
    if not data:
        return False, "Spotify API not configured or search failed."
    albums = (data.get("albums") or {}).get("items") or []
    if not albums:
        return False, f"No album found for '{query}'."
    uri = albums[0].get("uri")
    if not uri:
        return False, "Could not get album URI."
    if play(context_uri=uri):
        name = albums[0].get("name", "Album")
        artist = (albums[0].get("artists") or [{}])[0].get("name", "")
        return True, f"Playing album: {name}" + (f" by {artist}" if artist else "")
    return False, "Playback failed. Is Spotify open and a device active?"


# Mood/activity -> search query mapping for "play chill music" etc.
MOOD_SEARCH = {
    "happy": "happy upbeat music",
    "sad": "sad relaxing music",
    "chill": "chill lofi",
    "party": "party dance music",
    "workout": "workout gym music",
    "focus": "focus study concentration",
    "romantic": "romantic love songs",
    "sleep": "sleep relaxation",
    "motivation": "motivation pump up",
}


def play_by_mood(mood: str) -> tuple[bool, str]:
    """Play music by mood/activity. Uses MOOD_SEARCH mapping or raw mood as query."""
    mood_lower = mood.strip().lower()
    query = MOOD_SEARCH.get(mood_lower, mood)
    return search_and_play_playlist(query)


# ---------------------------------------------------------------------------
# Playlists (create, add track)
# ---------------------------------------------------------------------------


def get_my_playlists(limit: int = 20) -> list[dict] | None:
    data = _get("/me/playlists", params={"limit": limit})
    if not data:
        return None
    return data.get("items") or []


def create_playlist(name: str, public: bool = True) -> str | None:
    """Create a playlist. Returns playlist ID or None."""
    user = _get("/me")
    if not user:
        return None
    uid = user.get("id")
    if not uid:
        return None
    body = {"name": name, "public": public}
    data = _post(f"/users/{uid}/playlists", json=body)
    if not data:
        return None
    return data.get("id")


def add_track_to_playlist(playlist_id: str, track_uri: str) -> bool:
    """Add a track by URI to a playlist."""
    try:
        r = requests.post(
            API_BASE + f"/playlists/{playlist_id}/tracks",
            headers=_headers(),
            params={"uris": track_uri},
            timeout=10,
        )
        return r.status_code in (200, 201)
    except Exception as e:
        logger.warning("Spotify add to playlist: %s", e)
        return False


def get_current_track_uri() -> str | None:
    """Get URI of currently playing track (for 'add this to playlist')."""
    data = get_current_playback()
    if not data or not data.get("item"):
        return None
    return data["item"].get("uri")


def save_track_to_library(track_id: str) -> bool:
    """Add track to user's Liked Songs (favorites). track_id is Spotify ID, not URI."""
    try:
        r = requests.put(
            API_BASE + "/me/tracks",
            headers=_headers(),
            params={"ids": track_id},
            timeout=10,
        )
        return r.status_code in (200, 201)
    except Exception as e:
        logger.warning("Spotify save track: %s", e)
        return False


def save_current_track_to_library() -> tuple[bool, str]:
    """Add currently playing track to Liked Songs. Returns (success, message)."""
    data = get_current_playback()
    if not data or not data.get("item"):
        return False, "Nothing is playing right now."
    item = data["item"]
    track_id = item.get("id")
    if not track_id:
        return False, "Could not get track ID."
    if save_track_to_library(track_id):
        name = item.get("name", "Track")
        return True, f"Added '{name}' to your Liked Songs."
    return False, "Could not add to Liked Songs."

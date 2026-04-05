"""
Spotify tool layer — thin wrappers over spotify_api.py.
Used by bridge.py endpoints and any other caller that needs clean return dicts.
"""

import logging
from typing import Any

import spotify_api as _sp

logger = logging.getLogger(__name__)


def spotify_play(query: str) -> dict[str, Any]:
    """Search for a track by name/artist and start playing it."""
    try:
        ok, msg = _sp.search_and_play_track(query)
        if ok:
            return {"status": "ok", "message": msg}
        return {"status": "error", "message": msg}
    except Exception as e:
        logger.error("spotify_play failed: %s", e)
        return {"status": "error", "message": str(e)}


def spotify_pause() -> dict[str, Any]:
    """Pause the currently playing track."""
    try:
        ok = _sp.pause()
        if ok:
            return {"status": "ok", "message": "Playback paused."}
        return {"status": "error", "message": "Pause failed. Is Spotify open with an active device?"}
    except Exception as e:
        logger.error("spotify_pause failed: %s", e)
        return {"status": "error", "message": str(e)}


def spotify_search(query: str, limit: int = 5) -> list[dict[str, Any]]:
    """
    Search Spotify for tracks matching *query*.
    Returns a list of dicts with keys: name, artist, album, uri.
    """
    try:
        data = _sp.search(query, type="track", limit=limit)
        if not data:
            return []
        raw_tracks = (data.get("tracks") or {}).get("items") or []
        tracks = []
        for t in raw_tracks:
            tracks.append({
                "name": t.get("name", ""),
                "artist": ", ".join(a.get("name", "") for a in t.get("artists") or []),
                "album": (t.get("album") or {}).get("name", ""),
                "uri": t.get("uri", ""),
            })
        return tracks
    except Exception as e:
        logger.error("spotify_search failed: %s", e)
        return []


def spotify_shuffle(state: bool) -> dict[str, Any]:
    """Enable or disable shuffle mode."""
    try:
        ok = _sp.set_shuffle(state)
        if ok:
            return {"status": "ok", "shuffle": state}
        return {"status": "error", "message": "Shuffle change failed. Is Spotify open?"}
    except Exception as e:
        logger.error("spotify_shuffle failed: %s", e)
        return {"status": "error", "message": str(e)}

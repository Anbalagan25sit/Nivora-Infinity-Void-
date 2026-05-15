"""
Comprehensive Spotify Automation Tools using Spotipy
-----------------------------------------------------
Full Spotify control: play, search, queue, like, playlists, and more.

Features:
- Play songs, albums, artists, playlists
- Search with filters
- Queue management (add to queue)
- Like/unlike songs
- Playlist creation and management
- Get current playback info
- Control playback (pause, resume, next, previous, shuffle, repeat)
- Volume control
- Recently played tracks
- User's top tracks and artists
"""

import logging
from typing import Annotated, Optional
from livekit.agents import RunContext, function_tool
import spotify_api

logger = logging.getLogger(__name__)

# ============================================================================
# PLAYBACK CONTROL
# ============================================================================

@function_tool()
async def spotify_play_track(
    context: RunContext,
    query: Annotated[str, "Song name to search and play. Can include artist name. E.g. 'Blinding Lights', 'Shape of You Ed Sheeran'"],
) -> str:
    """
    Search for a song and play it immediately on Spotify using Web API.

    This function:
    1. Searches Spotify for the track
    2. Gets the track URI
    3. Directly plays it using Spotify Web API

    Examples:
    - spotify_play_track("Blinding Lights")
    - spotify_play_track("Bohemian Rhapsody Queen")
    - spotify_play_track("mutta kalaki")
    - spotify_play_track("As It Was Harry Styles")
    """
    try:
        if not spotify_api.is_configured():
            return "Spotify API is not configured. Please add SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET, and SPOTIFY_REFRESH_TOKEN to .env"

        # Step 1: Search for the track
        logger.info(f"[Spotify] Searching for: {query}")
        search_results = spotify_api.search(query, type="track", limit=5)

        if not search_results:
            return f"Search failed for '{query}'. Make sure Spotify is open and active."

        tracks = (search_results.get("tracks") or {}).get("items") or []

        if not tracks:
            return f"No tracks found for '{query}'. Try a different search term."

        # Get the best match (first result)
        track = tracks[0]
        track_uri = track.get("uri")
        track_name = track.get("name", "Unknown")
        track_artists = ", ".join(a.get("name", "") for a in track.get("artists", []))

        if not track_uri:
            return f"Found '{track_name}' but couldn't get track URI."

        logger.info(f"[Spotify] Found: {track_name} by {track_artists} ({track_uri})")

        # Step 2: Play the track using Web API
        import requests

        headers = spotify_api._headers()
        if not headers:
            return "Failed to get Spotify authorization. Check your refresh token."

        play_data = {
            "uris": [track_uri]
        }

        response = requests.put(
            f"{spotify_api.API_BASE}/me/player/play",
            headers=headers,
            json=play_data,
            timeout=10
        )

        if response.status_code in (200, 204):
            logger.info(f"[Spotify] Successfully playing: {track_name}")
            return f"Playing: {track_name} by {track_artists}"
        elif response.status_code == 404:
            logger.info(f"No active Spotify device found. Falling back to local app with exact URI: {track_uri}")
            try:
                import os
                import sys
                import subprocess
                
                # Path to the spotify_control.py script
                control_script = os.path.join(os.path.dirname(__file__), 'spotify_control.py')
                
                # Direct URIs (track, album, artist) auto-play, no need for UI macros
                result = subprocess.run(
                    [sys.executable, control_script, 'search', '--uri', track_uri],
                    capture_output=True,
                    text=True,
                    check=False
                )
                if result.returncode != 0:
                    return f"No active Spotify device found. Tried to launch desktop app with exact track URI but it failed."
                return f"No active device, so I launched the desktop app and played the exact track '{track_name}' by {track_artists}!"
            except Exception as fallback_err:
                return f"No active Spotify device found. Fallback to launch desktop app also failed: {fallback_err}"
        elif response.status_code == 403:
            return "Playback restricted. Make sure you have Spotify Premium."
        else:
            error_msg = response.text
            logger.error(f"[Spotify] Play failed: {response.status_code} - {error_msg}")
            return f"Failed to play track. Status {response.status_code}. Is Spotify open and active?"

    except Exception as e:
        logger.error(f"spotify_play_track error: {e}", exc_info=True)
        return f"Error playing track: {e}"


@function_tool()
async def spotify_play_album(
    context: RunContext,
    query: Annotated[str, "Album name to search and play. Include artist for better results. E.g. 'Midnights Taylor Swift', 'After Hours'"],
) -> str:
    """
    Search for an album and play it immediately on Spotify using Web API.

    Examples:
    - spotify_play_album("Midnights")
    - spotify_play_album("After Hours The Weeknd")
    - spotify_play_album("1989 Taylor Swift")
    """
    try:
        if not spotify_api.is_configured():
            return "Spotify API is not configured."

        # Search for album
        logger.info(f"[Spotify] Searching album: {query}")
        search_results = spotify_api.search(query, type="album", limit=1)

        if not search_results:
            return f"Album search failed for '{query}'."

        albums = (search_results.get("albums") or {}).get("items") or []

        if not albums:
            return f"No albums found for '{query}'."

        album = albums[0]
        album_uri = album.get("uri")
        album_name = album.get("name", "Unknown")
        album_artists = ", ".join(a.get("name", "") for a in album.get("artists", []))

        if not album_uri:
            return f"Found album but couldn't get URI."

        # Play album using Web API
        import requests
        headers = spotify_api._headers()

        play_data = {"context_uri": album_uri}

        response = requests.put(
            f"{spotify_api.API_BASE}/me/player/play",
            headers=headers,
            json=play_data,
            timeout=10
        )

        if response.status_code in (200, 204):
            return f"Playing album: {album_name} by {album_artists}"
        elif response.status_code == 404:
            logger.info(f"No active Spotify device found. Falling back to local app with exact URI: {album_uri}")
            try:
                import os
                import sys
                import subprocess
                control_script = os.path.join(os.path.dirname(__file__), 'spotify_control.py')
                result = subprocess.run(
                    [sys.executable, control_script, 'search', '--uri', album_uri],
                    capture_output=True, text=True, check=False
                )
                if result.returncode != 0:
                    return f"No active Spotify device found. Tried to launch desktop app with album URI but it failed."
                return f"No active device, so I launched the desktop app and played the album '{album_name}' by {album_artists}!"
            except Exception as fallback_err:
                return f"No active Spotify device found. Fallback also failed: {fallback_err}"
        else:
            return f"Failed to play album. Is Spotify open?"

    except Exception as e:
        return f"Failed to play album: {e}"


@function_tool()
async def spotify_play_artist(
    context: RunContext,
    query: Annotated[str, "Artist name to play. E.g. 'Taylor Swift', 'The Weeknd', 'Drake'"],
) -> str:
    """
    Play an artist's music (top tracks) using Web API.

    Examples:
    - spotify_play_artist("Taylor Swift")
    - spotify_play_artist("Drake")
    - spotify_play_artist("Coldplay")
    """
    try:
        if not spotify_api.is_configured():
            return "Spotify API is not configured."

        # Search for artist
        logger.info(f"[Spotify] Searching artist: {query}")
        search_results = spotify_api.search(query, type="artist", limit=1)

        if not search_results:
            return f"Artist search failed for '{query}'."

        artists = (search_results.get("artists") or {}).get("items") or []

        if not artists:
            return f"No artist found for '{query}'."

        artist = artists[0]
        artist_uri = artist.get("uri")
        artist_name = artist.get("name", "Unknown")

        if not artist_uri:
            return f"Found artist but couldn't get URI."

        # Play artist using Web API
        import requests
        headers = spotify_api._headers()

        play_data = {"context_uri": artist_uri}

        response = requests.put(
            f"{spotify_api.API_BASE}/me/player/play",
            headers=headers,
            json=play_data,
            timeout=10
        )

        if response.status_code in (200, 204):
            return f"Playing artist: {artist_name}"
        elif response.status_code == 404:
            logger.info(f"No active Spotify device found. Falling back to local app with exact URI: {artist_uri}")
            try:
                import os
                import sys
                import subprocess
                control_script = os.path.join(os.path.dirname(__file__), 'spotify_control.py')
                result = subprocess.run(
                    [sys.executable, control_script, 'search', '--uri', artist_uri],
                    capture_output=True, text=True, check=False
                )
                if result.returncode != 0:
                    return f"No active Spotify device found. Tried to launch desktop app with artist URI but it failed."
                return f"No active device, so I launched the desktop app and played the artist '{artist_name}'!"
            except Exception as fallback_err:
                return f"No active Spotify device found. Fallback also failed: {fallback_err}"
        else:
            return f"Failed to play artist. Is Spotify open?"

    except Exception as e:
        return f"Failed to play artist: {e}"


@function_tool()
async def spotify_play_playlist(
    context: RunContext,
    query: Annotated[str, "Playlist name to search and play. E.g. 'Today\'s Top Hits', 'Chill Vibes', 'Workout'"],
) -> str:
    """
    Search for a playlist and play it immediately using Web API.

    Examples:
    - spotify_play_playlist("Today's Top Hits")
    - spotify_play_playlist("Chill Vibes")
    - spotify_play_playlist("Workout Mix")
    """
    try:
        if not spotify_api.is_configured():
            return "Spotify API is not configured."

        # Search for playlist
        logger.info(f"[Spotify] Searching playlist: {query}")
        search_results = spotify_api.search(query, type="playlist", limit=1)

        if not search_results:
            return f"Playlist search failed for '{query}'."

        playlists = (search_results.get("playlists") or {}).get("items") or []

        if not playlists:
            return f"No playlist found for '{query}'."

        playlist = playlists[0]
        playlist_uri = playlist.get("uri")
        playlist_name = playlist.get("name", "Unknown")

        if not playlist_uri:
            return f"Found playlist but couldn't get URI."

        # Play playlist using Web API
        import requests
        headers = spotify_api._headers()

        play_data = {"context_uri": playlist_uri}

        response = requests.put(
            f"{spotify_api.API_BASE}/me/player/play",
            headers=headers,
            json=play_data,
            timeout=10
        )

        if response.status_code in (200, 204):
            return f"Playing playlist: {playlist_name}"
        elif response.status_code == 404:
            logger.info(f"No active Spotify device found. Falling back to local app with exact URI: {playlist_uri}")
            try:
                import os
                import sys
                import subprocess
                control_script = os.path.join(os.path.dirname(__file__), 'spotify_control.py')
                result = subprocess.run(
                    [sys.executable, control_script, 'search', '--uri', playlist_uri],
                    capture_output=True, text=True, check=False
                )
                if result.returncode != 0:
                    return f"No active Spotify device found. Tried to launch desktop app with playlist URI but it failed."
                return f"No active device, so I launched the desktop app and played the playlist '{playlist_name}'!"
            except Exception as fallback_err:
                return f"No active Spotify device found. Fallback also failed: {fallback_err}"
        else:
            return f"Failed to play playlist. Is Spotify open?"

    except Exception as e:
        return f"Failed to play playlist: {e}"


@function_tool()
async def spotify_play_by_mood(
    context: RunContext,
    mood: Annotated[str, "Mood or activity. Options: happy, sad, chill, party, workout, focus, romantic, sleep, motivation"],
) -> str:
    """
    Play music based on mood or activity.

    Supported moods:
    - happy, sad, chill, party, workout, focus, romantic, sleep, motivation

    Examples:
    - spotify_play_by_mood("chill")
    - spotify_play_by_mood("workout")
    - spotify_play_by_mood("focus")
    """
    try:
        if not spotify_api.is_configured():
            return "Spotify API is not configured."

        success, message = spotify_api.play_by_mood(mood)
        return message
    except Exception as e:
        return f"Failed to play mood music: {e}"


@function_tool()
async def spotify_pause(context: RunContext) -> str:
    """Pause Spotify playback."""
    try:
        if spotify_api.pause():
            return "Paused playback."
        return "Failed to pause. Is Spotify playing?"
    except Exception as e:
        return f"Failed to pause: {e}"


@function_tool()
async def spotify_resume(context: RunContext) -> str:
    """Resume Spotify playback."""
    try:
        if spotify_api.play():
            return "Resumed playback."
        return "Failed to resume. Is Spotify active?"
    except Exception as e:
        return f"Failed to resume: {e}"


@function_tool()
async def spotify_next(context: RunContext) -> str:
    """Skip to next track on Spotify."""
    try:
        if spotify_api.next_track():
            return "Skipped to next track."
        return "Failed to skip. Is Spotify playing?"
    except Exception as e:
        return f"Failed to skip: {e}"


@function_tool()
async def spotify_previous(context: RunContext) -> str:
    """Go to previous track on Spotify."""
    try:
        if spotify_api.previous_track():
            return "Went to previous track."
        return "Failed to go back. Is Spotify playing?"
    except Exception as e:
        return f"Failed to go previous: {e}"


@function_tool()
async def spotify_set_volume(
    context: RunContext,
    volume: Annotated[int, "Volume level 0-100"],
) -> str:
    """
    Set Spotify volume (0-100).

    Examples:
    - spotify_set_volume(50)  # 50% volume
    - spotify_set_volume(100)  # Max volume
    - spotify_set_volume(0)  # Mute
    """
    try:
        volume = max(0, min(100, volume))
        if spotify_api.set_volume(volume):
            return f"Volume set to {volume}%."
        return "Failed to set volume. Is Spotify active?"
    except Exception as e:
        return f"Failed to set volume: {e}"


@function_tool()
async def spotify_shuffle(
    context: RunContext,
    enable: Annotated[bool, "True to enable shuffle, False to disable"],
) -> str:
    """
    Enable or disable shuffle mode.

    Examples:
    - spotify_shuffle(True)  # Enable shuffle
    - spotify_shuffle(False)  # Disable shuffle
    """
    try:
        if spotify_api.set_shuffle(enable):
            return f"Shuffle {'enabled' if enable else 'disabled'}."
        return "Failed to toggle shuffle."
    except Exception as e:
        return f"Failed to set shuffle: {e}"


@function_tool()
async def spotify_repeat(
    context: RunContext,
    mode: Annotated[str, "Repeat mode: 'off', 'track', or 'context' (repeat playlist/album)"],
) -> str:
    """
    Set repeat mode.

    Modes:
    - 'off' - No repeat
    - 'track' - Repeat current track
    - 'context' - Repeat current playlist/album

    Examples:
    - spotify_repeat("track")  # Repeat current song
    - spotify_repeat("context")  # Repeat playlist
    - spotify_repeat("off")  # Turn off repeat
    """
    try:
        if mode not in ["off", "track", "context"]:
            return "Invalid repeat mode. Use: 'off', 'track', or 'context'"

        if spotify_api.set_repeat(mode):
            return f"Repeat set to {mode}."
        return "Failed to set repeat mode."
    except Exception as e:
        return f"Failed to set repeat: {e}"


# ============================================================================
# CURRENT PLAYBACK INFO
# ============================================================================

@function_tool()
async def spotify_now_playing(context: RunContext) -> str:
    """
    Get currently playing song information.

    Returns: Song name, artist, album, and playback status.
    """
    try:
        if not spotify_api.is_configured():
            return "Spotify API is not configured."

        return spotify_api.get_now_playing_text()
    except Exception as e:
        return f"Failed to get now playing: {e}"


@function_tool()
async def spotify_current_playback_details(context: RunContext) -> str:
    """
    Get detailed information about current playback including progress, shuffle, repeat state.
    """
    try:
        data = spotify_api.get_current_playback()
        if not data or not data.get("item"):
            return "Nothing is playing right now."

        item = data["item"]
        name = item.get("name", "Unknown")
        artists = ", ".join(a.get("name", "") for a in item.get("artists", []))
        album = (item.get("album") or {}).get("name", "")

        is_playing = data.get("is_playing", False)
        shuffle = data.get("shuffle_state", False)
        repeat = data.get("repeat_state", "off")
        progress_ms = data.get("progress_ms", 0)
        duration_ms = item.get("duration_ms", 0)

        progress = f"{progress_ms // 60000}:{(progress_ms % 60000) // 1000:02d}"
        duration = f"{duration_ms // 60000}:{(duration_ms % 60000) // 1000:02d}"

        status = "Playing" if is_playing else "Paused"

        info = f"{status}: {name} by {artists}"
        if album:
            info += f" (from {album})"
        info += f"\nProgress: {progress} / {duration}"
        info += f"\nShuffle: {'On' if shuffle else 'Off'}, Repeat: {repeat}"

        return info
    except Exception as e:
        return f"Failed to get playback details: {e}"


# ============================================================================
# QUEUE MANAGEMENT
# ============================================================================

@function_tool()
async def spotify_add_to_queue(
    context: RunContext,
    query: Annotated[str, "Song name to add to queue. E.g. 'Starboy', 'Levitating Dua Lipa'"],
) -> str:
    """
    Search for a song and add it to the playback queue.

    The song will play after the current track and queue finishes.

    Examples:
    - spotify_add_to_queue("Starboy")
    - spotify_add_to_queue("Levitating Dua Lipa")
    - spotify_add_to_queue("Stay Justin Bieber")
    """
    try:
        if not spotify_api.is_configured():
            return "Spotify API is not configured."

        # Search for track
        data = spotify_api.search(query, type="track", limit=1)
        if not data:
            return "Search failed."

        tracks = (data.get("tracks") or {}).get("items") or []
        if not tracks:
            return f"No tracks found for '{query}'."

        uri = tracks[0].get("uri")
        if not uri:
            return "Could not get track URI."

        # Add to queue
        import requests
        headers = spotify_api._headers()
        r = requests.post(
            f"{spotify_api.API_BASE}/me/player/queue",
            headers=headers,
            params={"uri": uri},
            timeout=10,
        )

        if r.status_code in (200, 204):
            name = tracks[0].get("name", "Track")
            artist = (tracks[0].get("artists") or [{}])[0].get("name", "")
            return f"Added to queue: {name}" + (f" by {artist}" if artist else "")

        return "Failed to add to queue. Is Spotify active?"
    except Exception as e:
        logger.error(f"spotify_add_to_queue error: {e}")
        return f"Failed to add to queue: {e}"


# ============================================================================
# LIKE / SAVE TRACKS
# ============================================================================

@function_tool()
async def spotify_like_current_song(context: RunContext) -> str:
    """
    Like (save) the currently playing song to your Liked Songs library.

    This adds the current track to your favorites.
    """
    try:
        if not spotify_api.is_configured():
            return "Spotify API is not configured."

        success, message = spotify_api.save_current_track_to_library()
        return message
    except Exception as e:
        return f"Failed to like song: {e}"


@function_tool()
async def spotify_unlike_current_song(context: RunContext) -> str:
    """
    Unlike (remove) the currently playing song from your Liked Songs.
    """
    try:
        if not spotify_api.is_configured():
            return "Spotify API is not configured."

        data = spotify_api.get_current_playback()
        if not data or not data.get("item"):
            return "Nothing is playing right now."

        item = data["item"]
        track_id = item.get("id")
        if not track_id:
            return "Could not get track ID."

        import requests
        headers = spotify_api._headers()
        r = requests.delete(
            f"{spotify_api.API_BASE}/me/tracks",
            headers=headers,
            params={"ids": track_id},
            timeout=10,
        )

        if r.status_code in (200, 204):
            name = item.get("name", "Track")
            return f"Removed '{name}' from your Liked Songs."

        return "Failed to unlike song."
    except Exception as e:
        return f"Failed to unlike song: {e}"


# ============================================================================
# SEARCH
# ============================================================================

@function_tool()
async def spotify_search(
    context: RunContext,
    query: Annotated[str, "Search query"],
    search_type: Annotated[str, "Type: 'track', 'album', 'artist', 'playlist', or 'all'"] = "all",
    limit: Annotated[int, "Number of results (1-10)"] = 5,
) -> str:
    """
    Search Spotify for tracks, albums, artists, or playlists.

    Examples:
    - spotify_search("Taylor Swift", "artist")
    - spotify_search("Blinding Lights", "track")
    - spotify_search("chill vibes", "playlist")
    - spotify_search("folklore", "album")
    """
    try:
        if not spotify_api.is_configured():
            return "Spotify API is not configured."

        limit = max(1, min(10, limit))

        if search_type == "all":
            search_type = "track,album,artist,playlist"

        data = spotify_api.search(query, type=search_type, limit=limit)
        if not data:
            return "Search failed."

        results = []

        # Process tracks
        if "tracks" in data:
            tracks = (data["tracks"] or {}).get("items", [])
            if tracks:
                results.append("Tracks:")
                for t in tracks[:limit]:
                    name = t.get("name", "?")
                    artist = ", ".join(a.get("name", "") for a in t.get("artists", []))
                    results.append(f"  • {name} - {artist}")

        # Process albums
        if "albums" in data:
            albums = (data["albums"] or {}).get("items", [])
            if albums:
                results.append("\nAlbums:")
                for a in albums[:limit]:
                    name = a.get("name", "?")
                    artist = ", ".join(ar.get("name", "") for ar in a.get("artists", []))
                    results.append(f"  • {name} - {artist}")

        # Process artists
        if "artists" in data:
            artists = (data["artists"] or {}).get("items", [])
            if artists:
                results.append("\nArtists:")
                for ar in artists[:limit]:
                    name = ar.get("name", "?")
                    followers = (ar.get("followers") or {}).get("total", 0)
                    results.append(f"  • {name} ({followers:,} followers)")

        # Process playlists
        if "playlists" in data:
            playlists = (data["playlists"] or {}).get("items", [])
            if playlists:
                results.append("\nPlaylists:")
                for p in playlists[:limit]:
                    name = p.get("name", "?")
                    owner = (p.get("owner") or {}).get("display_name", "")
                    results.append(f"  • {name}" + (f" by {owner}" if owner else ""))

        if not results:
            return f"No results found for '{query}'."

        return "\n".join(results)
    except Exception as e:
        return f"Search error: {e}"


# ============================================================================
# PLAYLISTS
# ============================================================================

@function_tool()
async def spotify_create_playlist(
    context: RunContext,
    name: Annotated[str, "Playlist name"],
    public: Annotated[bool, "Make playlist public?"] = True,
) -> str:
    """
    Create a new Spotify playlist.

    Examples:
    - spotify_create_playlist("My Workout Mix", public=False)
    - spotify_create_playlist("Road Trip 2024")
    """
    try:
        if not spotify_api.is_configured():
            return "Spotify API is not configured."

        playlist_id = spotify_api.create_playlist(name, public)
        if playlist_id:
            visibility = "public" if public else "private"
            return f"Created {visibility} playlist '{name}'."
        return "Failed to create playlist."
    except Exception as e:
        return f"Failed to create playlist: {e}"


@function_tool()
async def spotify_add_current_to_playlist(
    context: RunContext,
    playlist_name: Annotated[str, "Name of your playlist to add to"],
) -> str:
    """
    Add currently playing song to one of your playlists.

    Example:
    - spotify_add_current_to_playlist("My Favorites")
    """
    try:
        if not spotify_api.is_configured():
            return "Spotify API is not configured."

        # Get current track URI
        current_uri = spotify_api.get_current_track_uri()
        if not current_uri:
            return "Nothing is playing right now."

        # Find playlist by name
        playlists = spotify_api.get_my_playlists(limit=50)
        if not playlists:
            return "Could not get your playlists."

        playlist_id = None
        for p in playlists:
            if p.get("name", "").lower() == playlist_name.lower():
                playlist_id = p.get("id")
                break

        if not playlist_id:
            return f"Playlist '{playlist_name}' not found in your library."

        # Add track to playlist
        if spotify_api.add_track_to_playlist(playlist_id, current_uri):
            data = spotify_api.get_current_playback()
            if data and data.get("item"):
                track_name = data["item"].get("name", "Track")
                return f"Added '{track_name}' to playlist '{playlist_name}'."
            return f"Added current track to '{playlist_name}'."

        return "Failed to add track to playlist."
    except Exception as e:
        return f"Failed to add to playlist: {e}"


@function_tool()
async def spotify_list_my_playlists(
    context: RunContext,
    limit: Annotated[int, "Number of playlists to show (max 50)"] = 20,
) -> str:
    """
    List your Spotify playlists.

    Example:
    - spotify_list_my_playlists(10)
    """
    try:
        if not spotify_api.is_configured():
            return "Spotify API is not configured."

        limit = max(1, min(50, limit))
        playlists = spotify_api.get_my_playlists(limit)

        if not playlists:
            return "No playlists found or failed to fetch."

        results = [f"Your playlists ({len(playlists)}):"]
        for p in playlists:
            name = p.get("name", "?")
            track_count = (p.get("tracks") or {}).get("total", 0)
            public = "Public" if p.get("public") else "Private"
            results.append(f"  • {name} ({track_count} tracks, {public})")

        return "\n".join(results)
    except Exception as e:
        return f"Failed to list playlists: {e}"


# ============================================================================
# ALL SPOTIFY TOOLS
# ============================================================================

ALL_SPOTIFY_TOOLS = [
    # Playback control
    spotify_play_track,
    spotify_play_album,
    spotify_play_artist,
    spotify_play_playlist,
    spotify_play_by_mood,
    spotify_pause,
    spotify_resume,
    spotify_next,
    spotify_previous,
    spotify_set_volume,
    spotify_shuffle,
    spotify_repeat,
    # Info
    spotify_now_playing,
    spotify_current_playback_details,
    # Queue
    spotify_add_to_queue,
    # Like/Save
    spotify_like_current_song,
    spotify_unlike_current_song,
    # Search
    spotify_search,
    # Playlists
    spotify_create_playlist,
    spotify_add_current_to_playlist,
    spotify_list_my_playlists,
]

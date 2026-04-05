#!/usr/bin/env python3
"""
Get currently playing Spotify track info from window title
"""

import subprocess
import sys
import time
import os

STATE_FILE = os.path.expanduser("~/.spotify_last_track.txt")
AD_WORDS = ["advertisement", "ad", "spotify", "premium", "free"]

def get_spotify_title():
    """Get Spotify window title via PowerShell"""
    try:
        result = subprocess.run(
            ["powershell", "-Command",
             "(Get-Process Spotify -ErrorAction SilentlyContinue).MainWindowTitle"],
            capture_output=True,
            text=True,
            timeout=5
        )
        return result.stdout.strip()
    except:
        return ""

def parse_title(title):
    """Parse window title into artist and song"""
    if not title:
        return None, None, "stopped"

    # Check if Spotify is showing just the app name (paused/stopped)
    if title.lower() in ["spotify", "spotify premium", "spotify free"]:
        return None, None, "paused"

    # Check for ads
    title_lower = title.lower()
    if any(word in title_lower for word in AD_WORDS):
        # Sometimes ad window titles contain "Advertisement" or similar
        if "advertisement" in title_lower or "ad" in title_lower:
            return None, None, "ad"

    # Parse "Artist - Song" format
    if " - " in title:
        parts = title.split(" - ", 1)
        if len(parts) == 2:
            artist, song = parts
            return artist.strip(), song.strip(), "playing"

    # Unknown format
    return None, None, "unknown"

def save_last_track(artist, song):
    """Save last known track"""
    try:
        with open(STATE_FILE, 'w', encoding='utf-8') as f:
            f.write(f"{artist} - {song}")
    except:
        pass

def read_last_track():
    """Read last known track"""
    try:
        with open(STATE_FILE, 'r', encoding='utf-8') as f:
            return f.read().strip()
    except:
        return ""

def display_track(artist, song, status):
    """Display track info"""
    if status == "playing" and artist and song:
        print("")
        print("🎵 Now Playing:")
        print(f"  Song   : {song}")
        print(f"  Artist : {artist}")
        print(f"  Status : Playing")
        print("─" * 40)
        save_last_track(artist, song)
    elif status == "paused":
        last = read_last_track()
        if last:
            print(f"⏸️  Paused: {last}")
        else:
            print("⏸️  Paused (nothing previously playing)")
    elif status == "ad":
        print("📢 Advertisement playing...")
    elif status == "stopped":
        print("⏹️  Nothing playing")
    else:
        print(f"❓ Unknown state: {status}")

def watch_mode():
    """Watch for track changes"""
    last_title = ""
    last_status = ""

    print("👀 Watching for track changes... (Ctrl+C to stop)")
    print("─" * 40)

    try:
        while True:
            title = get_spotify_title()
            artist, song, status = parse_title(title)

            # Detect change
            current_display = f"{artist} - {song}" if artist and song else status
            if title != last_title or status != last_status:
                if last_status != status or (artist != None or song != None):
                    display_track(artist, song, status)
                    last_title = title
                    last_status = status

            time.sleep(5)
    except KeyboardInterrupt:
        print("\n👋 Stopped watching")
        sys.exit(0)

def main():
    # Check for --watch flag
    watch = "--watch" in sys.argv

    if watch:
        watch_mode()
    else:
        title = get_spotify_title()

        if not title:
            print("Error: Could not connect to Spotify or Spotify is not running")
            sys.exit(1)

        if title.startswith("Spotify"):
            # Spotify window exists but might not be playing
            print(f"Spotify window title: {title}")
            print("")

        artist, song, status = parse_title(title)
        display_track(artist, song, status)

        sys.exit(0 if status in ["playing", "paused", "ad"] else 1)

if __name__ == "__main__":
    main()

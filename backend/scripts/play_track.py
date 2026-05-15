#!/usr/bin/env python3
"""
Python script to play Spotify track/album/playlist/artist via URI deep links
"""

import re
import subprocess
import sys
import os

def main():
    if len(sys.argv) < 2:
        print("Error: URI argument required")
        print("Usage: play_track.py spotify:track:<id>")
        print("       play_track.py spotify:album:<id>")
        print("       play_track.py spotify:playlist:<id>")
        print("       play_track.py spotify:artist:<id>")
        sys.exit(1)

    uri = sys.argv[1]
    pattern = r'^spotify:(track|album|playlist|artist):([a-zA-Z0-9]+)$'

    match = re.match(pattern, uri)
    if not match:
        print("Error: Invalid Spotify URI format")
        print("Expected formats:")
        print("  spotify:track:<id>")
        print("  spotify:album:<id>")
        print("  spotify:playlist:<id>")
        print("  spotify:artist:<id>")
        sys.exit(1)

    spotify_type = match.group(1)
    spotify_id = match.group(2)

    script_dir = os.path.dirname(os.path.abspath(__file__))
    open_script = os.path.join(script_dir, "open_spotify.ps1")

    result = subprocess.run(
        ["powershell", "-File", open_script],
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        print(result.stdout, end='')
        print(result.stderr, end='', file=sys.stderr)
        sys.exit(1)

    subprocess.run(['start', uri], shell=True, check=True)

    web_url = f"https://open.spotify.com/{spotify_type}/{spotify_id}"
    print(f"Opening {spotify_type} URI: {uri}")
    print(f"Web URL: {web_url}")

if __name__ == "__main__":
    main()

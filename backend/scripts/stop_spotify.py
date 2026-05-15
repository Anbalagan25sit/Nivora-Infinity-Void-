#!/usr/bin/env python3
"""
Stop Spotify with three modes: --pause, --quit, --kill-all
"""

import subprocess
import sys

VK_MEDIA_PLAY_PAUSE = 0xB3
KEYEVENTF_EXTENDEDKEY = 0x0001
KEYEVENTF_KEYUP = 0x0002

def check_spotify_running():
    """Check if Spotify process is running"""
    try:
        result = subprocess.run(
            ["tasklist", "/FI", "IMAGENAME eq Spotify.exe"],
            capture_output=True,
            text=True,
            shell=True
        )
        return "Spotify.exe" in result.stdout
    except:
        return False

def send_media_key(vk):
    """Send media key using ctypes"""
    try:
        import ctypes
        ctypes.windll.user32.keybd_event(vk, 0, KEYEVENTF_EXTENDEDKEY, 0)
        ctypes.windll.user32.keybd_event(vk, 0, KEYEVENTF_EXTENDEDKEY | KEYEVENTF_KEYUP, 0)
        return True
    except:
        return False

def mode_pause():
    """Just pause playback"""
    if not check_spotify_running():
        print("Spotify is not running")
        return 0

    if send_media_key(VK_MEDIA_PLAY_PAUSE):
        print("Spotify playback paused")
        return 0
    else:
        print("Error: Failed to pause Spotify")
        return 1

def mode_quit():
    """Fully close Spotify"""
    if not check_spotify_running():
        print("Spotify is not running")
        return 0

    try:
        subprocess.run(['taskkill', '/IM', 'Spotify.exe', '/F'],
                      check=True, capture_output=True)

        # Also kill SpotifyCrashService if running
        result = subprocess.run(
            ["tasklist", "/FI", "IMAGENAME eq SpotifyCrashService.exe"],
            capture_output=True,
            text=True,
            shell=True
        )
        if "SpotifyCrashService.exe" in result.stdout:
            subprocess.run(['taskkill', '/IM', 'SpotifyCrashService.exe', '/F'],
                          check=True, capture_output=True)

        print("Spotify has been closed")
        return 0
    except subprocess.CalledProcessError as e:
        print(f"Error: Failed to quit Spotify - {e}")
        return 1

def mode_kill_all():
    """Kill Spotify and all helper processes"""
    processes = ["Spotify.exe", "SpotifyCrashService.exe", "SpotifyWebHelper.exe"]
    killed_any = False

    for proc in processes:
        try:
            subprocess.run(['taskkill', '/IM', proc, '/F'],
                          check=False, capture_output=True)
            killed_any = True
        except:
            pass

    if killed_any:
        print("All Spotify processes terminated")
    else:
        print("No Spotify processes were running")
    return 0

def main():
    if len(sys.argv) > 1:
        mode = sys.argv[1].lower()
        if mode not in ["--pause", "--quit", "--kill-all"]:
            print("Error: Invalid mode")
            print("Usage: stop_spotify.py [--pause|--quit|--kill-all]")
            print("       Default: --pause")
            sys.exit(1)
        mode = mode[2:]  # Remove leading "--"
    else:
        mode = "pause"

    if mode == "pause":
        sys.exit(mode_pause())
    elif mode == "quit":
        sys.exit(mode_quit())
    elif mode == "kill-all":
        sys.exit(mode_kill_all())

if __name__ == "__main__":
    main()

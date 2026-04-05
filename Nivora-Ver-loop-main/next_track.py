#!/usr/bin/env python3
"""
Skip to next track in Spotify
"""

import ctypes
import os
import subprocess
import sys
import time

VK_MEDIA_NEXT_TRACK = 0xB0
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

def get_spotify_title():
    """Get Spotify window title"""
    try:
        result = subprocess.run(
            ["powershell", "-Command",
             "(Get-Process Spotify -ErrorAction SilentlyContinue).MainWindowTitle"],
            capture_output=True,
            text=True
        )
        return result.stdout.strip()
    except:
        return ""

def method_nircmd():
    """Try using nircmd"""
    nircmd_paths = [
        os.path.join(os.environ.get('LOCALAPPDATA', ''), r"Microsoft\WindowsApps\nircmd.exe"),
        r"C:\Program Files\nircmd\nircmd.exe",
        os.path.join(os.environ.get('APPDATA', ''), "nircmd.exe")
    ]

    for path in nircmd_paths:
        if os.path.exists(path):
            try:
                subprocess.run([path, "medianext"], check=True, capture_output=True)
                return True
            except:
                continue
    return False

def method_ctypes():
    """Use Windows API via ctypes"""
    try:
        ctypes.windll.user32.keybd_event(
            VK_MEDIA_NEXT_TRACK, 0, KEYEVENTF_EXTENDEDKEY, 0
        )
        ctypes.windll.user32.keybd_event(
            VK_MEDIA_NEXT_TRACK, 0, KEYEVENTF_EXTENDEDKEY | KEYEVENTF_KEYUP, 0
        )
        return True
    except:
        return False

def main():
    if not check_spotify_running():
        print("Error: Spotify is not running")
        sys.exit(1)

    # Try methods in order
    if method_nircmd():
        time.sleep(0.5)
        title = get_spotify_title()
        if title and not title.startswith("Spotify"):
            print(f"Skipped to: {title}")
        sys.exit(0)

    if method_ctypes():
        time.sleep(0.5)
        title = get_spotify_title()
        if title and not title.startswith("Spotify"):
            print(f"Skipped to: {title}")
        sys.exit(0)

    print("Error: Failed to skip track")
    sys.exit(1)

if __name__ == "__main__":
    main()

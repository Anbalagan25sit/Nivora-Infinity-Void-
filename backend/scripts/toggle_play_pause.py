#!/usr/bin/env python3
"""
Python script to toggle Spotify play/pause using media key
"""

import ctypes
import os
import subprocess
import sys
import time

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
                subprocess.run([path, "mediaplay"], check=True, capture_output=True)
                return True
            except:
                continue
    return False

def method_ctypes():
    """Use Windows API via ctypes"""
    try:
        ctypes.windll.user32.keybd_event(
            VK_MEDIA_PLAY_PAUSE, 0, KEYEVENTF_EXTENDEDKEY, 0
        )
        ctypes.windll.user32.keybd_event(
            VK_MEDIA_PLAY_PAUSE, 0, KEYEVENTF_EXTENDEDKEY | KEYEVENTF_KEYUP, 0
        )
        return True
    except:
        return False

def method_pyautogui():
    """Try using pyautogui if available"""
    try:
        import pyautogui
        pyautogui.press('playpause')
        return True
    except ImportError:
        return False
    except:
        return False

def main():
    if not check_spotify_running():
        print("Error: Spotify is not running")
        sys.exit(1)

    # Try methods in order of preference
    if method_nircmd():
        sys.exit(0)

    if method_ctypes():
        sys.exit(0)

    if method_pyautogui():
        sys.exit(0)

    print("Error: Failed to toggle play/pause")
    sys.exit(1)

if __name__ == "__main__":
    main()

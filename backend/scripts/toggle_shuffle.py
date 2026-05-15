#!/usr/bin/env python3
"""
Toggle Spotify shuffle mode using Ctrl+S shortcut
State tracked in ~/.spotify_state.json
"""

import json
import os
import subprocess
import sys
import time

STATE_FILE = os.path.expanduser("~/.spotify_state.json")

def ensure_state_file():
    """Create state file if it doesn't exist"""
    if not os.path.exists(STATE_FILE):
        with open(STATE_FILE, 'w') as f:
            json.dump({"shuffle": False}, f)

def get_shuffle_state():
    """Read current shuffle state"""
    ensure_state_file()
    try:
        with open(STATE_FILE, 'r') as f:
            state = json.load(f)
            return state.get("shuffle", False)
    except:
        return False

def set_shuffle_state(enabled):
    """Save shuffle state"""
    ensure_state_file()
    try:
        with open(STATE_FILE, 'r') as f:
            state = json.load(f)
    except:
        state = {}
    state["shuffle"] = enabled
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f)

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

def get_spotify_hwnd():
    """Get Spotify window handle"""
    try:
        import ctypes
        user32 = ctypes.windll.user32
        # Try multiple possible titles
        for title in ["Spotify Premium", "Spotify Free", "Spotify"]:
            hwnd = user32.FindWindowW(None, title)
            if hwnd:
                return hwnd
        return None
    except:
        return None

def send_ctrl_s(hwnd):
    """Send Ctrl+S to Spotify window"""
    try:
        import ctypes
        user32 = ctypes.windll.user32

        # Set foreground window
        if not user32.SetForegroundWindow(hwnd):
            return False

        time.sleep(0.2)

        # Send Ctrl+S using keybd_event
        VK_CONTROL = 0x11
        VK_S = 0x53
        KEYEVENTF_KEYUP = 0x0002

        ctypes.windll.user32.keybd_event(VK_CONTROL, 0, 0, 0)
        ctypes.windll.user32.keybd_event(VK_S, 0, 0, 0)
        ctypes.windll.user32.keybd_event(VK_S, 0, KEYEVENTF_KEYUP, 0)
        ctypes.windll.user32.keybd_event(VK_CONTROL, 0, KEYEVENTF_KEYUP, 0)

        time.sleep(0.2)
        return True
    except Exception as e:
        print(f"Error sending keys: {e}")
        return False

def main():
    if not check_spotify_running():
        print("Error: Spotify is not running")
        sys.exit(1)

    current_shuffle = get_shuffle_state()
    next_shuffle = not current_shuffle

    hwnd = get_spotify_hwnd()
    if not hwnd:
        print("Error: Could not find Spotify window")
        sys.exit(1)

    if send_ctrl_s(hwnd):
        set_shuffle_state(next_shuffle)
        if next_shuffle:
            print("Shuffle is now ON")
        else:
            print("Shuffle is now OFF")
        sys.exit(0)
    else:
        print("Error: Failed to send Ctrl+S to Spotify")
        sys.exit(1)

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Toggle Spotify repeat mode using Ctrl+R shortcut
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
            json.dump({"repeat": "off"}, f)

def get_repeat_state():
    """Read current repeat state"""
    ensure_state_file()
    try:
        with open(STATE_FILE, 'r') as f:
            state = json.load(f)
            return state.get("repeat", "off")
    except:
        return "off"

def set_repeat_state(mode):
    """Save repeat state"""
    ensure_state_file()
    try:
        with open(STATE_FILE, 'r') as f:
            state = json.load(f)
    except:
        state = {}
    state["repeat"] = mode
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
    """Get Spotify window handle using ctypes"""
    try:
        import ctypes
        user32 = ctypes.windll.user32
        # Try with different window titles
        for title in ["Spotify Premium", "Spotify Free", "Spotify"]:
            hwnd = user32.FindWindowW(None, title)
            if hwnd:
                return hwnd
        return None
    except:
        return None

def send_ctrl_r(hwnd):
    """Send Ctrl+R to Spotify window"""
    try:
        import ctypes
        user32 = ctypes.windll.user32

        # Set foreground window
        if not user32.SetForegroundWindow(hwnd):
            return False

        time.sleep(0.2)

        # Send Ctrl+R using keybd_event
        VK_CONTROL = 0x11
        VK_R = 0x52

        # Ctrl down
        ctypes.windll.user32.keybd_event(VK_CONTROL, 0, 0, 0)
        # R down
        ctypes.windll.user32.keybd_event(VK_R, 0, 0, 0)
        # R up
        ctypes.windll.user32.keybd_event(VK_R, 0, 2, 0)  # KEYEVENTF_KEYUP = 2
        # Ctrl up
        ctypes.windll.user32.keybd_event(VK_CONTROL, 0, 2, 0)

        time.sleep(0.2)
        return True
    except Exception as e:
        print(f"Error sending keys: {e}")
        return False

def main():
    if not check_spotify_running():
        print("Error: Spotify is not running")
        sys.exit(1)

    current_mode = get_repeat_state()
    modes = ["off", "context", "track"]
    next_index = (modes.index(current_mode) + 1) % len(modes)
    next_mode = modes[next_index]

    hwnd = get_spotify_hwnd()
    if not hwnd:
        print("Error: Could not find Spotify window")
        sys.exit(1)

    if send_ctrl_r(hwnd):
        set_repeat_state(next_mode)
        mode_names = {"off": "Repeat Off", "context": "Repeat All", "track": "Repeat One"}
        print(f"Repeat mode: {mode_names[next_mode]}")
        sys.exit(0)
    else:
        print("Error: Failed to send Ctrl+R to Spotify")
        sys.exit(1)

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Spotify volume control using pycaw
pip install pycaw
"""

import sys
import os

def check_spotify_running():
    """Check if Spotify process is running"""
    try:
        import subprocess
        result = subprocess.run(
            ["tasklist", "/FI", "IMAGENAME eq Spotify.exe"],
            capture_output=True,
            text=True,
            shell=True
        )
        return "Spotify.exe" in result.stdout
    except:
        return False

def control_volume_pycaw(action, value):
    """Control Spotify volume using pycaw"""
    try:
        from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
        from comtypes import CLSCTX_ALL
        from ctypes import cast, POINTER

        sessions = AudioUtilities.GetAllSessions()
        spotify_session = None

        for session in sessions:
            try:
                if session.Process and session.Process.name() == "Spotify.exe":
                    spotify_session = session
                    break
            except:
                continue

        if not spotify_session:
            print("Error: Spotify audio session not found")
            return 1

        volume = spotify_session._ctl.QueryInterface(IAudioEndpointVolume)

        if action == "set":
            vol_level = max(0.0, min(1.0, value / 100.0))
            volume.SetMasterVolumeLevelScalar(vol_level, None)
            print(f"Spotify volume: {value}%")

        elif action == "up":
            current = volume.GetMasterVolumeLevelScalar()
            new_vol = max(0.0, min(1.0, current + (value / 100.0)))
            volume.SetMasterVolumeLevelScalar(new_vol, None)
            print(f"Spotify volume: {round(new_vol * 100)}%")

        elif action == "down":
            current = volume.GetMasterVolumeLevelScalar()
            new_vol = max(0.0, current - (value / 100.0))
            volume.SetMasterVolumeLevelScalar(new_vol, None)
            print(f"Spotify volume: {round(new_vol * 100)}%")

        elif action == "mute":
            volume.SetMute(True, None)
            print("Spotify volume: muted")

        elif action == "unmute":
            volume.SetMute(False, None)
            print("Spotify volume: unmuted")

        return 0

    except ImportError:
        print("Error: pycaw not installed. Install with: pip install pycaw")
        return 1
    except Exception as e:
        print(f"pycaw method failed: {e}")
        return 2

def control_volume_nircmd(action, value):
    """Control volume using nircmd (system-wide)"""
    nircmd_paths = [
        os.path.join(os.environ.get('LOCALAPPDATA', ''), r"Microsoft\WindowsApps\nircmd.exe"),
        r"C:\Program Files\nircmd\nircmd.exe",
        os.path.join(os.environ.get('APPDATA', ''), "nircmd.exe")
    ]

    for path in nircmd_paths:
        if os.path.exists(path):
            import subprocess
            if action == "set":
                sys_vol = round(value / 100.0 * 65535)
                subprocess.run([path, "setsysvolume", str(sys_vol)], check=False)
            elif action == "up":
                change = round(value / 100.0 * 65535)
                subprocess.run([path, "changesysvolume", str(change)], check=False)
            elif action == "down":
                change = round(value / 100.0 * 65535)
                subprocess.run([path, "changesysvolume", str(-change)], check=False)
            elif action == "mute":
                subprocess.run([path, "mutesysvolume", "1"], check=False)
            elif action == "unmute":
                subprocess.run([path, "mutesysvolume", "0"], check=False)
            print("Volume adjusted via nircmd (system-wide)")
            return 0

    print("Error: nircmd not found. Install from https://www.nirsoft.net/utils/nircmd.html")
    return 1

def main():
    if not check_spotify_running():
        print("Spotify is not running")
        sys.exit(0)

    action = None
    value = 10

    for i, arg in enumerate(sys.argv[1:], 1):
        if arg.startswith("--"):
            action = arg[2:]
        elif arg.isdigit() and action is not None:
            value = int(arg)

    if action not in ["set", "up", "down", "mute", "unmute"]:
        print("Usage: volume_control.py [--set|--up|--down|--mute|--unmute] [value]")
        print("  --set 75     → set volume to 75%")
        print("  --up 10      → increase by 10%")
        print("  --down 10    → decrease by 10%")
        print("  --mute       → mute Spotify only")
        print("  --unmute     → unmute Spotify only")
        sys.exit(1)

    if action in ["set", "up", "down"] and not (len(sys.argv) > 2 and sys.argv[2].isdigit()):
        if action == "set":
            print(f"Error: --set requires a value (0-100)")
        else:
            print(f"Error: --{action} requires a value")
        sys.exit(1)

    # Try pycaw first (Spotify-specific)
    result = control_volume_pycaw(action, value if action in ["set", "up", "down"] else 0)

    if result == 2:
        # pycaw failed, try nircmd
        result = control_volume_nircmd(action, value if action in ["set", "up", "down"] else 0)

    sys.exit(result)

if __name__ == "__main__":
    main()

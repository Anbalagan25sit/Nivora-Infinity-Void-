#!/usr/bin/env python3
"""
Spotify Control Script for Windows
No API or OAuth required - uses Windows-specific methods
"""

import argparse
import json
import os
import subprocess
import sys
import time
import ctypes
import ctypes.wintypes
from ctypes.wintypes import RECT, POINT
from urllib.parse import quote_plus
from pathlib import Path

# Windows API constants
user32 = ctypes.windll.user32
VK_CONTROL = 0x11
VK_S = 0x53
VK_R = 0x52
VK_MEDIA_PLAY_PAUSE = 0xB3
VK_MEDIA_NEXT_TRACK = 0xB0
VK_MEDIA_PREV_TRACK = 0xB1
VK_RETURN = 0x0D
VK_ESCAPE = 0x1B
VK_TAB = 0x09
KEYEVENTF_KEYUP = 0x0002

# State file location
STATE_FILE = Path.home() / ".spotify_state.json"
LAST_TRACK_FILE = Path.home() / ".spotify_last_track.txt"


def load_state():
    """Load state from JSON file"""
    if STATE_FILE.exists():
        try:
            with open(STATE_FILE, 'r') as f:
                return json.load(f)
        except:
            return {}
    return {}


def save_state(state):
    """Save state to JSON file"""
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2)


def _open_uri(uri):
    """
    Open a URI on Windows safely, handling special characters.
    Uses os.startfile which calls ShellExecute and properly handles URI schemes.
    """
    try:
        # Method 1: Use os.startfile (Windows only) - safest for URIs
        os.startfile(uri)
    except AttributeError:
        # Fallback: use subprocess with proper quoting
        subprocess.run(['cmd', '/c', 'start', '', f'"{uri}"'], shell=True, check=True)
    except Exception as e:
        raise RuntimeError(f"Failed to open URI: {e}")


def _try_click_close_button():
    """Attempt to click the close button on an ad overlay."""
    try:
        hwnd, title = get_spotify_window_handle()
        if not hwnd:
            return
        rect = RECT()
        if not user32.GetWindowRect(hwnd, ctypes.byref(rect)):
            return
        x = rect.right - 20
        y = rect.top + 50
        old_pt = POINT()
        user32.GetCursorPos(ctypes.byref(old_pt))
        user32.SetCursorPos(x, y)
        time.sleep(0.1)
        user32.mouse_event(0x0002, x, y, 0, 0, 0)  # MOUSEEVENTF_LEFTDOWN
        time.sleep(0.05)
        user32.mouse_event(0x0004, x, y, 0, 0, 0)  # MOUSEEVENTF_LEFTUP
        time.sleep(0.3)
        user32.SetCursorPos(old_pt.x, old_pt.y)
    except Exception as e:
        print(f"[WARN] Click close button failed: {e}")


def _auto_play_first_result():
    """
    After opening a search, wait for results and use key sequences to play first result.
    Tries multiple strategies to handle different Spotify UI states and ad overlays.
    """
    # Wait for Spotify to load results and any ad to appear
    time.sleep(8)

    hwnd, title = get_spotify_window_handle()
    if not hwnd:
        print('[WARN] Could not find Spotify window for auto-play')
        return
    was_minimized = user32.IsIconic(hwnd) != 0
    user32.SetForegroundWindow(hwnd)
    time.sleep(1.5)

    # Step 1: Try to dismiss ad popups with ESC
    print('[INFO] Dismissing potential ad popups...')
    for i in range(5):
        user32.keybd_event(VK_ESCAPE, 0, 0, 0)
        time.sleep(0.1)
        user32.keybd_event(VK_ESCAPE, 0, KEYEVENTF_KEYUP, 0)
        time.sleep(0.6)

    # Step 2: Try clicking the close button (X) if ad persists
    print('[INFO] Attempting to click close button on ad...')
    _try_click_close_button()

    time.sleep(1)

    # Re-ensure focus on Spotify
    current_hwnd = user32.GetForegroundWindow()
    if current_hwnd != hwnd:
        user32.SetForegroundWindow(hwnd)
        time.sleep(0.5)

    # Step 3: Try multiple navigation strategies
    strategies = [
        ('Just Enter', _strategy_just_enter),
        ('Tab x2 + Enter', lambda hwnd: _strategy_tab_enter(hwnd, times=2)),
        ('Tab x3 + Enter', lambda hwnd: _strategy_tab_enter(hwnd, times=3)),
        ('Tab x5 + Enter', lambda hwnd: _strategy_tab_enter(hwnd, times=5)),
        ('ArrowDown + Enter', _strategy_arrow_down),
        ('Tab x5, ArrowDown, Enter', _strategy_tab_arrow_enter),
        ('Ctrl+L, Tab, Enter', _strategy_ctrl_l_tab_enter),
    ]

    for name, strategy_func in strategies:
        print(f'[INFO] Trying strategy: {name}')
        if strategy_func(hwnd):
            print(f'[OK] Success with strategy: {name}')
            break
        else:
            print(f'[INFO] Strategy {name} failed, trying next...')
            time.sleep(0.7)
    else:
        print('[WARN] All autoplay strategies failed - song may not have started')

    if was_minimized:
        user32.ShowWindow(hwnd, 9)


def _try_click_close_button():
    """Attempt to click the close button on an ad overlay at top-right."""
    hwnd, title = get_spotify_window_handle()
    if not hwnd:
        return
    # Get window rect
    rect = RECT()
    if not user32.GetWindowRect(hwnd, ctypes.byref(rect)):
        return
    # Calculate click position: top-right of client area, offset to avoid title bar close
    # Typical ad close button is near top-right, inside the client area
    x = rect.right - 20  # 20 pixels from right edge
    y = rect.top + 50    # 50 pixels from top (below title bar)
    # Save cursor
    old_pt = POINT()
    user32.GetCursorPos(ctypes.byref(old_pt))
    # Move and click
    user32.SetCursorPos(x, y)
    time.sleep(0.1)
    user32.mouse_event(0x0002, x, y, 0, 0, 0)  # MOUSEEVENTF_LEFTDOWN
    time.sleep(0.05)
    user32.mouse_event(0x0004, x, y, 0, 0, 0)  # MOUSEEVENTF_LEFTUP
    time.sleep(0.3)
    # Restore cursor
    user32.SetCursorPos(old_pt.x, old_pt.y)

def _strategy_tab_enter(hwnd, times=2):
    for _ in range(times):
        user32.keybd_event(VK_TAB, 0, 0, 0)
        time.sleep(0.1)
        user32.keybd_event(VK_TAB, 0, KEYEVENTF_KEYUP, 0)
        time.sleep(0.25)
    user32.keybd_event(VK_RETURN, 0, 0, 0)
    time.sleep(0.1)
    user32.keybd_event(VK_RETURN, 0, KEYEVENTF_KEYUP, 0)
    time.sleep(1.5)
    return _check_playback_started(hwnd)

def _strategy_arrow_down(hwnd):
    VK_DOWN = 0x28
    user32.keybd_event(VK_DOWN, 0, 0, 0)
    time.sleep(0.1)
    user32.keybd_event(VK_DOWN, 0, KEYEVENTF_KEYUP, 0)
    time.sleep(0.2)
    user32.keybd_event(VK_RETURN, 0, 0, 0)
    time.sleep(0.1)
    user32.keybd_event(VK_RETURN, 0, KEYEVENTF_KEYUP, 0)
    time.sleep(1.5)
    return _check_playback_started(hwnd)

def _strategy_ctrl_l_tab_enter(hwnd):
    user32.keybd_event(VK_CONTROL, 0, 0, 0)
    time.sleep(0.05)
    user32.keybd_event(0x4C, 0, 0, 0)  # L key
    time.sleep(0.05)
    user32.keybd_event(0x4C, 0, KEYEVENTF_KEYUP, 0)
    user32.keybd_event(VK_CONTROL, 0, KEYEVENTF_KEYUP, 0)
    time.sleep(0.5)
    return _strategy_tab_enter(hwnd, times=1)

def _strategy_just_enter(hwnd):
    """Just press Enter - maybe first result is already focused"""
    user32.keybd_event(VK_RETURN, 0, 0, 0)
    time.sleep(0.1)
    user32.keybd_event(VK_RETURN, 0, KEYEVENTF_KEYUP, 0)
    time.sleep(1.5)
    return _check_playback_started(hwnd)

def _strategy_tab_arrow_enter(hwnd, tab_times=5):
    """Tab several times, then ArrowDown, then Enter"""
    for _ in range(tab_times):
        user32.keybd_event(VK_TAB, 0, 0, 0)
        time.sleep(0.1)
        user32.keybd_event(VK_TAB, 0, KEYEVENTF_KEYUP, 0)
        time.sleep(0.2)
    VK_DOWN = 0x28
    user32.keybd_event(VK_DOWN, 0, 0, 0)
    time.sleep(0.1)
    user32.keybd_event(VK_DOWN, 0, KEYEVENTF_KEYUP, 0)
    time.sleep(0.2)
    user32.keybd_event(VK_RETURN, 0, 0, 0)
    time.sleep(0.1)
    user32.keybd_event(VK_RETURN, 0, KEYEVENTF_KEYUP, 0)
    time.sleep(1.5)
    return _check_playback_started(hwnd)

def _check_playback_started(hwnd):
    time.sleep(2)
    track = get_current_track()
    if track and track.get('status') == 'playing':
        print(f'[INFO] Verified playback: {track.get("artist")} - {track.get("song")}')
        return True
    return False



def is_spotify_running():
    """Check if Spotify process is running"""
    try:
        result = subprocess.run(
            ['tasklist', '/FI', 'IMAGENAME eq Spotify.exe'],
            capture_output=True, text=True
        )
        return "Spotify.exe" in result.stdout
    except:
        return False


def get_spotify_window_handle():
    """Get Spotify window handle (HWND)"""
    # Try different possible window titles
    titles = ["Spotify Premium", "Spotify", "Spotify Free"]
    for title in titles:
        hwnd = user32.FindWindowW(None, title)
        if hwnd:
            return hwnd, title
    return None, None


def bring_spotify_to_foreground():
    """Bring Spotify window to foreground and return whether it was minimized"""
    hwnd, title = get_spotify_window_handle()
    if not hwnd:
        return None, False

    # Check if window is minimized
    was_minimized = user32.IsIconic(hwnd) != 0

    # Bring to foreground
    user32.SetForegroundWindow(hwnd)
    time.sleep(0.2)  # Wait for window to activate

    return hwnd, was_minimized


def restore_window_if_needed(hwnd, was_minimized):
    """Restore window if it was minimized before"""
    if was_minimized and hwnd:
        user32.ShowWindow(hwnd, 9)  # SW_RESTORE


def cmd_search(args):
    """Search for a song on Spotify and open it"""
    # Direct URI play if provided
    if args.uri:
        print(f"Opening Spotify URI: {args.uri}")
        _open_uri(args.uri)
        # Direct URIs (track, album, artist) auto-play, no need for Enter key
        return 0

    # Build query for search
    query_parts = []
    if args.song:
        query_parts.append(args.song)
    if args.artist:
        query_parts.append(args.artist)

    if not query_parts:
        print("Error: Must provide either --uri, or at least --song/--artist")
        return 1

    query = " ".join(query_parts)
    encoded_query = quote_plus(query)

    # Method 1: Spotify URI deep link
    search_uri = f'spotify:search:{query.replace(" ", "+")}'
    print(f"Attempting Method 1: {search_uri}")

    # Try to open with Spotify protocol
    try:
        _open_uri(search_uri)
    except Exception as e:
        print(f"Method 1 failed: {e}, falling back to Method 2...")
        # Method 2: Web URL
        web_url = f'https://open.spotify.com/search/{encoded_query}'
        print(f"Opening web URL: {web_url}")
        _open_uri(web_url)

    # Auto-play first result if requested (only for search results)
    if args.autoplay:
        print("[INFO] Auto-play enabled, pressing Enter to play first result...")
        _auto_play_first_result()

    # Print reference URLs
    print("\nReference URLs:")
    print(f"  Spotify URI: {search_uri}")
    print(f"  Web URL: https://open.spotify.com/search/{encoded_query}")

    return 0


def get_current_track():
    """Get currently playing track info from Spotify window title"""
    if not is_spotify_running():
        print("[ERROR] Spotify is not running")
        return None

    # PowerShell method to get window title
    ps_script = """
    $sp = Get-Process Spotify -ErrorAction SilentlyContinue
    if ($sp) {
        $sp.MainWindowTitle
    }
    """

    try:
        result = subprocess.run(
            ['powershell', '-Command', ps_script],
            capture_output=True, text=True
        )
        title = result.stdout.strip()

        if not title or title == "Spotify" or title == "Spotify Premium" or title == "Spotify Free":
            return {
                "status": "paused",
                "song": None,
                "artist": None
            }

        if " - " in title:
            artist, song = title.split(" - ", 1)
            return {
                "status": "playing",
                "song": song.strip(),
                "artist": artist.strip()
            }
        else:
            return {
                "status": "unknown",
                "song": title,
                "artist": None
            }
    except Exception as e:
        print(f"Error getting track info: {e}")
        return None


def cmd_now_playing(args):
    """Display current track info"""
    track = get_current_track()

    if not track:
        return 1

    if track["status"] == "paused":
        print("[PAUSED]  Spotify is paused or nothing is playing")
    elif track["status"] == "playing":
        print("[NOW PLAYING] Now Playing:")
        print(f"  Song   : {track['song']}")
        print(f"  Artist : {track['artist']}")
        print(f"  Status : Playing")

        # Save last track
        with open(LAST_TRACK_FILE, 'w') as f:
            f.write(f"{track['artist']} - {track['song']}")
    else:
        print(f"[NOW PLAYING] Window Title: {track['song']}")

    return 0


def cmd_watch(args):
    """Watch mode - continuously display track info"""
    print("[NOW PLAYING] Spotify Watch Mode (Ctrl+C to stop)")
    print("-" * 50)

    last_track = None

    try:
        while True:
            track = get_current_track()

            if track and track["status"] == "playing":
                current = f"{track['artist']} - {track['song']}"

                if current != last_track:
                    if last_track:
                        print(f"\n[SYNC] Track changed!")
                    print(f"\n[NOW PLAYING] Now Playing:")
                    print(f"  Song   : {track['song']}")
                    print(f"  Artist : {track['artist']}")

                    # Save last track
                    with open(LAST_TRACK_FILE, 'w') as f:
                        f.write(current)

                    last_track = current

            time.sleep(args.interval)

    except KeyboardInterrupt:
        print("\n\n[BYE] Watch mode stopped")
        return 0


def send_media_key(vk_code):
    """Send media key to Spotify globally"""
    # Press key down
    ctypes.windll.user32.keybd_event(vk_code, 0, 0, 0)
    time.sleep(0.05)
    # Release key
    ctypes.windll.user32.keybd_event(vk_code, 0, 2, 0)


def send_ctrl_key(letter):
    """Send Ctrl+Letter key combination to Spotify"""
    hwnd, was_minimized = bring_spotify_to_foreground()

    if not hwnd:
        print("[ERROR] Spotify is not running")
        return False

    # Get virtual key code
    VK_CODE = {
        's': 0x53,
        'r': 0x52,
    }[letter.lower()]

    # Send Ctrl down
    ctypes.windll.user32.keybd_event(VK_CONTROL, 0, 0, 0)
    time.sleep(0.05)

    # Send the letter key
    ctypes.windll.user32.keybd_event(VK_CODE, 0, 0, 0)
    time.sleep(0.05)
    ctypes.windll.user32.keybd_event(VK_CODE, 0, 2, 0)  # Key up

    # Send Ctrl up
    ctypes.windll.user32.keybd_event(VK_CONTROL, 0, 2, 0)
    time.sleep(0.05)

    # Restore window if it was minimized
    if was_minimized:
        ctypes.windll.user32.ShowWindow(hwnd, 9)  # SW_RESTORE

    return True


def cmd_shuffle(args):
    """Toggle Spotify shuffle mode"""
    if not is_spotify_running():
        print("[ERROR] Spotify is not running")
        return 1

    print("[SYNC] Toggling shuffle...")

    if send_ctrl_key('s'):
        print("[OK] Shuffle toggled")
    else:
        print("[ERROR] Failed to toggle shuffle")
        return 1

    return 0


def cmd_repeat(args):
    """Cycle Spotify repeat modes"""
    if not is_spotify_running():
        print("[ERROR] Spotify is not running")
        return 1

    # Load previous state
    state = load_state()
    current_mode = state.get("repeat", "off")

    # Cycle modes: off -> context -> track -> off
    modes = ["off", "context", "track"]
    current_index = modes.index(current_mode) if current_mode in modes else 0
    new_index = (current_index + 1) % len(modes)
    new_mode = modes[new_index]

    print(f"[SYNC] Changing repeat: {current_mode} -> {new_mode}")

    # Send Ctrl+R
    if send_ctrl_key('r'):
        # Save new state
        state["repeat"] = new_mode
        save_state(state)

        mode_names = {
            "off": "Off",
            "context": "Repeat All",
            "track": "Repeat One"
        }
        print(f"[OK] Repeat mode: {mode_names.get(new_mode, new_mode)}")
    else:
        print("[ERROR] Failed to change repeat mode")
        return 1

    return 0


def cmd_volume(args):
    """Control Spotify volume"""
    if not is_spotify_running():
        print("[ERROR] Spotify is not running")
        return 1

    # Normalize mute/unmute to a single mute variable
    if args.unmute:
        mute_state = False
    elif args.mute:
        mute_state = True
    else:
        mute_state = None

    # Method 1: Using pycaw (if available)
    if args.method == "pycaw":
        try:
            from comtypes import CLSCTX_ALL
            from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

            print("[VOLUME] Controlling volume via pycaw...")

            sessions = AudioUtilities.GetAllSessions()
            for session in sessions:
                if session.Process and session.Process.name() == "Spotify.exe":
                    volume = session.SimpleAudioVolume

                    if args.set is not None:
                        volume.SetMasterVolume(args.set / 100.0, None)
                        print(f"[OK] Volume set to {args.set}%")
                    elif args.up:
                        current = volume.GetMasterVolume()
                        new_volume = min(1.0, current + (args.up / 100.0))
                        volume.SetMasterVolume(new_volume, None)
                        print(f"[OK] Volume increased to {int(new_volume * 100)}%")
                    elif args.down:
                        current = volume.GetMasterVolume()
                        new_volume = max(0.0, current - (args.down / 100.0))
                        volume.SetMasterVolume(new_volume, None)
                        print(f"[OK] Volume decreased to {int(new_volume * 100)}%")
                    elif mute_state is not None:
                        volume.SetMute(mute_state, None)
                        status = "muted" if mute_state else "unmuted"
                        print(f"[OK] Volume {status}")
                    elif args.toggle:
                        current = volume.GetMute()
                        volume.SetMute(not current, None)
                        status = "muted" if not current else "unmuted"
                        print(f"[OK] Volume toggled: {status}")

                    return 0

            print("[ERROR] Could not find Spotify audio session")
            return 1

        except ImportError:
            print("[WARN]  pycaw not installed, falling back to nircmd...")
            args.method = "nircmd"

    # Method 2: Using nircmd
    if args.method == "nircmd":
        # Check if nircmd is available
        try:
            subprocess.run(['nircmd', '--help'], capture_output=True)
        except:
            print("[ERROR] nircmd not found. Install from https://www.nirsoft.net/utils/nircmd.html")
            return 1

        if args.set is not None:
            volume_value = int(args.set * 65535 / 100)
            subprocess.run(['nircmd', 'setsysvolume', str(volume_value)])
            print(f"[OK] Volume set to {args.set}%")
        elif args.up:
            subprocess.run(['nircmd', 'changesysvolume', str(int(args.up * 65535 / 100))])
            print(f"[OK] Volume increased by {args.up}%")
        elif args.down:
            subprocess.run(['nircmd', 'changesysvolume', str(int(-args.down * 65535 / 100))])
            print(f"[OK] Volume decreased by {args.down}%")
        elif mute_state is not None:
            mute_val = 1 if mute_state else 0
            subprocess.run(['nircmd', 'mutesysvolume', str(mute_val)])
            status = "muted" if mute_state else "unmuted"
            print(f"[OK] Volume {status}")
        elif args.toggle:
            subprocess.run(['nircmd', 'mutesysvolume', '2'])
            print("[OK] Volume toggled")
        else:
            print("[ERROR] No volume action specified")
            return 1

        return 0

    print("[ERROR] No available volume control method")
    return 1


def cmd_stop(args):
    """Stop Spotify (pause, quit, or kill)"""
    if not is_spotify_running():
        print("[ERROR] Spotify is not running")
        return 0

    if args.mode == "pause" or args.mode == "toggle":
        print("[PAUSED]  Pausing Spotify...")
        send_media_key(VK_MEDIA_PLAY_PAUSE)

        # Verify paused
        time.sleep(0.5)
        track = get_current_track()
        if track and track["status"] == "paused":
            print("[OK] Spotify paused")
        else:
            print("[WARN]  Spotify may still be playing")

    elif args.mode == "quit":
        print("[EXIT] Quitting Spotify...")
        subprocess.run(['taskkill', '/IM', 'Spotify.exe', '/F'], capture_output=True)

        # Also kill helper processes
        for proc in ["SpotifyCrashService.exe", "SpotifyWebHelper.exe"]:
            subprocess.run(['taskkill', '/IM', proc, '/F'], capture_output=True)

        time.sleep(1)
        if not is_spotify_running():
            print("[OK] Spotify has been closed")
        else:
            print("[WARN]  Some Spotify processes may still be running")

    elif args.mode == "kill-all":
        print("[KILL] Killing all Spotify processes...")
        for proc in ["Spotify.exe", "SpotifyCrashService.exe", "SpotifyWebHelper.exe"]:
            subprocess.run(['taskkill', '/IM', proc, '/F'], capture_output=True)
        print("[OK] All Spotify processes terminated")

    else:
        print(f"[ERROR] Unknown mode: {args.mode}")
        return 1

    return 0


def cmd_playback(args):
    """Control playback: play, pause, next, previous"""
    if not is_spotify_running():
        print("[ERROR] Spotify is not running")
        return 1

    action = args.action.lower()

    if action in ('play', 'pause'):
        # Check current state to avoid toggling unnecessarily
        track = get_current_track()
        current_status = track.get("status") if track else None

        if action == 'play':
            if current_status == 'playing':
                print("[INFO] Already playing")
                return 0
            # Send play/pause key (will resume if paused)
            send_media_key(VK_MEDIA_PLAY_PAUSE)
            print("[OK] Resumed playback")
        else:  # pause
            if current_status == 'paused':
                print("[INFO] Already paused")
                return 0
            send_media_key(VK_MEDIA_PLAY_PAUSE)
            print("[OK] Paused playback")

    elif action == 'next':
        send_media_key(VK_MEDIA_NEXT_TRACK)
        print("[OK] Skipped to next track")
    elif action == 'previous':
        send_media_key(VK_MEDIA_PREV_TRACK)
        print("[OK] Went to previous track")
    else:
        print(f"[ERROR] Unknown action: {action}")
        return 1

    return 0


def main():
    parser = argparse.ArgumentParser(
        description="Spotify Control Script for Windows (No API Required)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Search and open a song
  spotify.py search --song "Blinding Lights" --artist "The Weeknd"

  # Open a specific track
  spotify.py search --uri spotify:track:0VjIjW4GlUZAMY2vXMi3b

  # Show current track
  spotify.py now-playing

  # Watch for track changes
  spotify.py watch

  # Toggle shuffle
  spotify.py shuffle

  # Cycle repeat mode
  spotify.py repeat

  # Control volume
  spotify.py volume --set 50
  spotify.py volume --up 10
  spotify.py volume --down 5
  spotify.py volume --mute true
  spotify.py volume --toggle

  # Stop Spotify
  spotify.py stop --pause
  spotify.py stop --quit
  spotify.py stop --kill-all
        """
    )

    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # Search command
    search_parser = subparsers.add_parser('search', help='Search for a song and open Spotify')
    search_parser.add_argument('--song', help='Song name')
    search_parser.add_argument('--artist', help='Artist name')
    search_parser.add_argument('--uri', help='Direct Spotify URI to play')
    search_parser.add_argument('--autoplay', action='store_true', help='Auto-play first result (for tool integration)')

    # Now playing command
    subparsers.add_parser('now-playing', help='Show currently playing track')

    # Watch command
    watch_parser = subparsers.add_parser('watch', help='Watch mode - continuously show track info')
    watch_parser.add_argument('--interval', type=int, default=5, help='Refresh interval in seconds (default: 5)')

    # Shuffle command
    subparsers.add_parser('shuffle', help='Toggle shuffle mode')

    # Repeat command
    subparsers.add_parser('repeat', help='Cycle repeat mode (Off -> Repeat All -> Repeat One)')

    # Volume command
    volume_parser = subparsers.add_parser('volume', help='Control Spotify volume')
    volume_parser.add_argument('--set', type=int, choices=range(0, 101), metavar='0-100', help='Set volume to percentage')
    volume_parser.add_argument('--up', type=int, default=5, help='Increase volume by percentage (default: 5)')
    volume_parser.add_argument('--down', type=int, default=5, help='Decrease volume by percentage (default: 5)')
    volume_parser.add_argument('--mute', action='store_true', help='Mute volume')
    volume_parser.add_argument('--unmute', action='store_true', help='Unmute volume')
    volume_parser.add_argument('--toggle', action='store_true', help='Toggle mute')
    volume_parser.add_argument('--method', choices=['pycaw', 'nircmd'], default='pycaw', help='Volume control method (default: pycaw)')

    # Stop command
    stop_parser = subparsers.add_parser('stop', help='Stop Spotify')
    stop_parser.add_argument('--mode', choices=['pause', 'quit', 'kill-all', 'toggle'], default='pause',
                            help='Stop mode: pause (default), quit, kill-all, or toggle')

    # Playback command (for next/previous/play/pause)
    playback_parser = subparsers.add_parser('playback', help='Control playback (next, previous, play, pause)')
    playback_parser.add_argument('action', choices=['play', 'pause', 'next', 'previous'],
                                help='Playback action: play, pause, next, previous')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    # Route to appropriate command
    commands = {
        'search': cmd_search,
        'now-playing': cmd_now_playing,
        'watch': cmd_watch,
        'shuffle': cmd_shuffle,
        'repeat': cmd_repeat,
        'volume': cmd_volume,
        'stop': cmd_stop,
        'playback': cmd_playback,
    }

    return commands[args.command](args)


if __name__ == '__main__':
    sys.exit(main())

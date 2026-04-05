# Spotify Control Script for Windows

A comprehensive Python script to control Spotify on Windows **without using any Spotify API or OAuth**. Uses Windows-specific methods like window title reading, keyboard shortcuts, and audio session control.

## Features

- **Search & Open**: Search for songs or open specific tracks via URI
- **Now Playing**: Display current track info from Spotify window title
- **Watch Mode**: Continuously monitor track changes
- **Shuffle Control**: Toggle shuffle with Ctrl+S
- **Repeat Modes**: Cycle through Off → Repeat All → Repeat One
- **Volume Control**: Set/adjust/mute Spotify volume independently
- **Playback Control**: Pause, quit, or kill-all Spotify processes

## Requirements

- Windows 10/11
- Python 3.7+
- Spotify Desktop App installed (for most features)

### Optional Dependencies

For **volume control** using `--method pycaw` (default):
```bash
pip install pycaw comtypes
```

For **volume control** using `--method nircmd`:
- Download [nircmd](https://www.nirsoft.net/utils/nircmd.html) and add to PATH

## Installation

1. Save the script as `spotify_control.py`
2. (Optional) Install dependencies:
   ```bash
   pip install pycaw comtypes
   ```
3. (Optional) Download nircmd for alternative volume control

## Usage

### Search and Open Songs

```bash
# Search by song and artist
python spotify_control.py search --song "Blinding Lights" --artist "The Weeknd"

# Open a specific track by URI
python spotify_control.py search --uri spotify:track:0VjIjW4GlUZAMYd2vXMi3b
```

**How it works:**
- First tries: `spotify:search:query` (URI scheme, opens Spotify directly)
- Falls back to: `https://open.spotify.com/search/query` (opens browser)
- Properly encodes special characters (&, ', (, ), #, etc.)

### Now Playing

```bash
python spotify_control.py now-playing
```

**Output:**
```
🎵 Now Playing:
  Song   : Blinding Lights
  Artist : The Weeknd
  Status : Playing
```

Or when paused:
```
⏸️  Spotify is paused or nothing is playing
```

### Watch Mode

```bash
# Watch for changes with 5-second interval (default)
python spotify_control.py watch

# Custom interval
python spotify_control.py watch --interval 3
```

Press `Ctrl+C` to stop. Shows a message when track changes. Saves last track to `~/.spotify_last_track.txt`.

### Shuffle Control

```bash
python spotify_control.py shuffle
```

Sends `Ctrl+S` to Spotify to toggle shuffle mode.

### Repeat Modes

```bash
python spotify_control.py repeat
```

Cycles through: **Off → Repeat All → Repeat One → Off...**

State is saved in `~/.spotify_state.json` so the script remembers the last mode (although the actual state depends on Spotify).

### Volume Control

```bash
# Set volume to specific percentage
python spotify_control.py volume --set 75

# Increase/decrease volume
python spotify_control.py volume --up 10    # Increase by 10%
python spotify_control.py volume --down 5   # Decrease by 5%

# Mute controls
python spotify_control.py volume --mute true    # Mute
python spotify_control.py volume --unmute       # Unmute
python spotify_control.py volume --toggle       # Toggle mute

# Choose method (pycaw or nircmd)
python spotify_control.py volume --set 50 --method pycaw
python spotify_control.py volume --set 50 --method nircmd
```

**Note:** Volume control works **only for Spotify**, independent of system volume.

### Stop Spotify

```bash
# Just pause playback (default)
python spotify_control.py stop --pause

# Quit Spotify completely
python spotify_control.py stop --quit

# Kill all Spotify processes
python spotify_control.py stop --kill-all

# Toggle play/pause
python spotify_control.py stop --toggle
```

## How It Works (No API)

### Getting Track Info
- Reads Spotify's main window title using PowerShell `Get-Process`
- While playing, title format is: `Artist - Song Name`
- When paused/minimized, title is just `Spotify` or `Spotify Premium`

### Keyboard Shortcuts
- **Shuffle**: `Ctrl+S`
- **Repeat**: `Ctrl+R`
- **Play/Pause**: Media key `VK_MEDIA_PLAY_PAUSE`

All sent using `ctypes` and Windows API `keybd_event()`.

### Volume Control
- Uses `pycaw` library to access Windows Audio Session API
- Finds Spotify's audio session by process name
- Adjusts volume via `ISimpleAudioVolume.SetMasterVolume()`

### Process Management
- Uses `taskkill` command or `Stop-Process` PowerShell cmdlet
- Kills specific processes: `Spotify.exe`, `SpotifyCrashService.exe`, `SpotifyWebHelper.exe`

## Files Created

- `~/.spotify_state.json` - Saves repeat mode state
- `~/.spotify_last_track.txt` - Saves last played track (for reference)

## Troubleshooting

### "Spotify is not running"
Make sure the Spotify desktop app is open and logged in.

### Volume control fails
- Install pycaw: `pip install pycaw comtypes`
- Or use nircmd: download from nirsoft.net and add to PATH

### Keyboard shortcuts not working
Ensure Spotify window is focused. The script automatically brings Spotify to foreground before sending shortcuts.

### Search opens browser instead of Spotify
Make sure Spotify desktop app is installed and the `spotify:` URI protocol handler is registered (usually happens during installation).

## Technical Notes

- All methods work on Windows only (uses Windows APIs)
- No Spotify API credentials needed (100% local)
- Works with Spotify Free and Premium
- Does NOT work with Spotify Web Player (requires a desktop app)
- Command-line friendly (can be aliased or added to PATH)

## License

MIT License - Feel free to use and modify as needed.

# Spotify Control Integration with Robin Agent

## Overview

Successfully integrated a comprehensive, no-API Spotify control system into the Robin agent. The integration uses the newly created `spotify_control.py` script (based on Windows APIs) instead of relying on the Spotify Web API or pyautogui hacks.

## Components

### 1. `spotify_control.py` (Main Script)
**Location**: Same directory as `tools.py`

**Features**:
- Search and open songs/artists via URI deep links
- Get currently playing track (reads window title)
- Watch mode (continuous monitoring)
- Playback control: play, pause, next, previous
- Shuffle toggle (Ctrl+S)
- Repeat mode cycling (Off → Repeat All → Repeat One)
- Volume control (set, up, down, mute, unmute) via pycaw or nircmd
- Stop modes: pause, quit, kill-all

**Commands**:
```bash
python spotify_control.py search --song "Blinding Lights" --artist "The Weeknd"
python spotify_control.py search --uri spotify:track:...
python spotify_control.py now-playing
python spotify_control.py watch
python spotify_control.py playback play|pause|next|previous
python spotify_control.py shuffle
python spotify_control.py repeat
python spotify_control.py volume --set 75
python spotify_control.py stop --pause|quit|kill-all
```

### 2. `tools.py` (Robin Tool Wrappers)

**Updated Tools** (now use `spotify_control.py`):
- `spotify_play_media(query, media_type)` - Play search results
- `spotify_control_playback(action)` - Control playback (pause/resume/next/previous)
- `spotify_what_is_playing()` - Get current track
- `spotify_mute_application(mute)` - Mute/unmute Spotify only

**New Tools Added**:
- `spotify_toggle_shuffle()` - Toggle shuffle mode
- `spotify_cycle_repeat()` - Cycle repeat mode
- `spotify_volume(set, up, down)` - Control volume

**Constant Added**:
```python
SPOTIFY_CONTROL_SCRIPT = os.path.join(os.path.dirname(__file__), 'spotify_control.py')
```

### 3. `prompts.py` (Robin's Instructions)

Updated the "Media routing" section to include all new tools and correct usage:

```
Media routing:
- Spotify play a song/artist/album/playlist -> Use `spotify_play_media(query, media_type)`
- Spotify pause/resume/next/previous -> Use `spotify_control_playback(action)`
- Check what's playing -> Use `spotify_what_is_playing()`
- Mute/unmute Spotify -> Use `spotify_mute_application(mute)`
- Control Spotify volume -> Use `spotify_volume(set=75)` or `spotify_volume(up=10)`
- Toggle shuffle -> Use `spotify_toggle_shuffle()`
- Cycle repeat modes -> Use `spotify_cycle_repeat()`
- Stop/quit Spotify -> Use `spotify_control` with commands: 'stop', 'quit', 'kill-all'
```

## Technical Details

### How It Works
- `tools.py` spawns subprocesses calling `spotify_control.py`
- All Spotify control happens locally via Windows APIs (no Spotify API)
- Uses:
  - `ctypes` + Windows API (`user32.dll`) for keyboard shortcuts
  - `PowerShell` to read window titles
  - `pycaw` (optional) or `nircmd` (optional) for volume control
  - `os.startfile` for URI launching

### Compatibility
- Windows 10/11 only
- Requires Spotify Desktop App (not Web Player)
- Works with Spotify Free and Premium

### Dependencies
- **Required**: None (pure Python + Windows APIs)
- **Optional for volume control**:
  - `pip install pycaw comtypes` (default method)
  - Or download `nircmd` from NirSoft

## Testing

All tools have been tested:
- ✓ Import validation
- ✓ Help output
- ✓ Special character encoding (works with &, (, ), #)
- ✓ Direct URI play
- ✓ State file operations
- ✓ Tool registration

## Usage Examples with Robin

When user says:
- "Play Blinding Lights by The Weeknd" → Robin calls `spotify_play_media('Blinding Lights', 'track')`
- "Pause the music" → `spotify_control_playback('pause')`
- "What's playing?" → `spotify_what_is_playing()`
- "Turn it up" → `spotify_volume(up=10)`
- "Shuffle this playlist" → `spotify_toggle_shuffle()`
- "Repeat one" → `spotify_cycle_repeat()`
- "Mute Spotify" → `spotify_mute_application(True)`

## Files Modified/Created

| File | Action | Lines Changed |
|------|--------|---------------|
| `spotify_control.py` | Created | 650+ lines |
| `tools.py` | Updated | Added 6 new tools, modified 4 existing |
| `prompts.py` | Updated | Media routing section |
| `README_SpotifyControl.md` | Created | Full documentation |
| `requirements.txt` | Created | Optional deps |
| `spotify.bat` | Created | Batch wrapper |

## Advantages Over Previous Implementation

- **No pyautogui hacks**: No simulated tab/enter presses
- **No winsdk dependency**: SMTC not required for now-playing
- **More reliable**: Uses direct Windows APIs
- **Full feature set**: Shuffle, repeat, volume, stop modes all exposed
- **State persistence**: Repeat mode saved to JSON
- **Watch mode**: Can monitor track changes
- **Better error handling**: Clear error messages when Spotify isn't running

## Future Enhancements

- Add ability to play specific track by URI directly via `spotify_play_media`
- Add tool to get Spotify status (running/not running)
- Add tool to launch Spotify if not running
- Consider replacing `spotify_play` and `spotify_control` (API-based) with no-API alternatives

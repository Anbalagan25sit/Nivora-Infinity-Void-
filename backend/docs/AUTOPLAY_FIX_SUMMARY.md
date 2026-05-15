# Spotify Autoplay Fix - Summary

## Problem
When Robin calls `spotify_play_media()` to play a song:
1. Spotify opens with search results but **doesn't start playing**
2. Tab+Enter key sequence didn't work because **ad popups blocked input**

## Solution Implemented

### 1. Multi-Strategy Autoplay System
**File**: `spotify_control.py`

Added robust `_auto_play_first_result()` function that tries **7 different strategies** in order:

1. **Just Enter** - maybe result already focused
2. **Tab x2 + Enter** - original approach
3. **Tab x3 + Enter** - more tabs
4. **Tab x5 + Enter** - even more tabs
5. **ArrowDown + Enter** - alternative navigation
6. **Tab x5, ArrowDown, Enter** - combined approach
7. **Ctrl+L, Tab, Enter** - refocus search then navigate

Each strategy checks if playback started by reading window title. First success stops the loop.

### 2. Ad Dismissal
**New Method**: `_try_click_close_button()`
- Waits for Spotify window to be ready
- Calculates position of X button (top-right of window)
- Simulates mouse click to close ad
- Restores mouse cursor to original position

Also: Sends **ESC** 5 times before clicking (many ads respond to ESC).

### 3. Timing Improvements
- Initial wait increased to **8 seconds** (allows ad to appear and be dismissible)
- Delays between key presses tuned (0.1-0.25s)
- After each strategy, wait 1.5s before checking playback status

### 4. Code Structure
**New Constants**:
- `VK_ESCAPE = 0x1B`
- `VK_TAB = 0x09` (already present)

**New Functions**:
- `_try_click_close_button()` - clicks X to close ad
- `_strategy_just_enter(hwnd)` - simple Enter press
- `_strategy_tab_arrow_enter(hwnd)` - tabs then arrow down then Enter

**Updated Functions**:
- `_auto_play_first_result()` - now comprehensive with ad handling

### 5. Integration Points
- `spotify_control.py` `search` command now accepts `--autoplay` flag
- `tools.py` `spotify_play_media()` tool calls search with `--autoplay`
- Robin agent automatically benefits from autoplay when playing songs

## Testing Output Example (Spotify running)

```
[INFO] Auto-play enabled, pressing Enter to play first result...
[INFO] Dismissing potential ad popups...
[INFO] Attempting to click close button on ad...
[INFO] Trying strategy: Just Enter
[INFO] Strategy Just Enter failed, trying next...
[INFO] Trying strategy: Tab x2 + Enter
[OK] Success with strategy: Tab x2 + Enter
[INFO] Verified playback: The Weeknd - Powerhouse
```

## Why This Works

1. **Redundancy**: If one key sequence fails due to UI state, another might work
2. **Ad Handling**: ESC + mouse click covers most ad types
3. **Verification**: We check if playback actually started, so we don't stop too early
4. **Graceful Degradation**: If Spotify not running, prints clear error
5. **Non-Destructive**: Mouse cursor restored; window minimized state preserved

## Manual Testing Checklist

- [ ] Spotify Premium (no ads) - likely works with first strategy
- [ ] Spotify Free with overlay ad - ESC should close it
- [ ] Spotify Free with non-dismissible ad - may need wait longer
- [ ] Different screen resolutions - click coordinates may need adjustment

## If Autoplay Still Fails

1. Check if Spotify window is actually in focus after the script runs
2. Verify ad close button appears at expected coordinates (top-right, ~50px down)
3. Consider increasing initial wait from 8s to 10-12s for slower connections
4. If using a custom Spotify theme, coordinates may differ

## Files Modified

| File | Lines Added | Purpose |
|------|-------------|---------|
| `spotify_control.py` | ~120 | Multi-strategy autoplay + mouse click |
| `tools.py` | ~10 | Add `--autoplay` to spotify_play_media call |
| `prompts.py` | ~20 | Clarified tool usage, no-tool-announcement rule |

## Next Steps (Optional)

- [ ] Add configuration for click coordinates (in case UI differs)
- [ ] Add strategy that uses ArrowRight/ArrowLeft? (for grid navigation)
- [ ] Use image recognition to find close button precisely (cv2)
- [ ] Add fallback to send Alt+F4 to close ad window if separate

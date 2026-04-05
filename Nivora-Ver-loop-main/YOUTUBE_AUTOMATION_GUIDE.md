# YouTube Automation - Quick Start Guide

## Overview

Nivora can now **automatically search, find, and play YouTube videos and live streams** using natural language queries and vision-guided browser automation.

## Features

✅ **Natural Language Search** - No need for exact video titles
✅ **Live Stream Detection** - Automatically finds and plays live streams
✅ **Recent/Latest Videos** - Understands temporal queries
✅ **Vision-Guided Clicking** - Uses AWS Nova Pro to identify and click videos
✅ **Automatic Playback** - Opens browser and starts video without manual intervention
✅ **Playback Control** - Pause, play, fullscreen, mute with voice commands

---

## Usage Examples

### Play Live Streams

**User:** *"Play recently repo tamil gaming live"*

**What happens:**
1. Nivora searches YouTube for "recently repo tamil gaming live"
2. Uses vision AI to identify live streams (looks for red LIVE badge)
3. Automatically clicks the best matching live stream
4. Video starts playing in your default browser

**User:** *"Find tamil gaming live streams"*

Returns a list of all currently live gaming streams.

---

### Play Recent Videos

**User:** *"Play latest MrBeast video"*

**What happens:**
1. Searches YouTube for "latest MrBeast video"
2. Vision AI identifies the most recent upload
3. Automatically starts playback

---

### Play Specific Content

**User:** *"Play lofi hip hop radio live stream"*
**User:** *"Play Pewdiepie's newest upload"*
**User:** *"Play the new Sidemen video"*

All work with natural language - no need to know exact titles!

---

## Available Tools

### 1. `youtube_search_and_play`

**Main tool for playing YouTube content**

```python
youtube_search_and_play(
    query="recently repo tamil gaming live",
    prefer_live=True  # Prioritize live streams
)
```

**Query Examples:**
- "recently repo tamil gaming live"
- "latest Pewdiepie video"
- "lofi hip hop radio live"
- "MrBeast newest upload"
- "Sidemen newest video"

**How it works:**
1. Opens YouTube search
2. Waits 3 seconds for page load
3. Captures screen screenshot
4. Uses AWS Nova Pro vision to find best match
5. Clicks on video thumbnail
6. Verifies playback started

---

### 2. `youtube_find_live_streams`

**Find all active live streams for a topic**

```python
youtube_find_live_streams(
    channel_or_topic="tamil gaming"
)
```

Returns a formatted list of:
- Video titles
- Channel names
- Current viewer counts
- Position in search results

---

### 3. `youtube_play_by_url`

**Play a specific video by URL**

```python
youtube_play_by_url(
    url="https://www.youtube.com/watch?v=..."
)
```

---

### 4. `youtube_control_playback`

**Control video playback with keyboard shortcuts**

```python
youtube_control_playback(action="fullscreen")
```

**Available actions:**
- `"play"` / `"pause"` - Toggle playback (spacebar)
- `"fullscreen"` - Toggle fullscreen (F key)
- `"mute"` - Toggle mute (M key)
- `"skip_ad"` - Skip advertisement (Tab + Enter)

---

## Technical Details

### Vision AI Integration

The system uses **AWS Nova Pro vision model** to:
- Identify video thumbnails on YouTube
- Read video titles and channel names
- Detect LIVE badges
- Find clickable coordinates
- Verify playback status

### Browser Automation

- Opens videos in your **default browser** (Chrome, Firefox, Edge, etc.)
- Uses `pyautogui` for precise clicking
- Waits for page loads to ensure accuracy
- Verifies video is playing before reporting success

### Live Stream Detection

Automatically adds YouTube's live filter (`&sp=EgJAAQ%253D%253D`) when:
- Query contains "live" or "stream"
- `prefer_live=True` parameter is set
- System detects live-related keywords

### Recent Video Prioritization

YouTube naturally prioritizes recent uploads when query contains:
- "recent"
- "latest"
- "newest"
- "new"
- "today"

---

## Configuration

### Required
- AWS Bedrock access (for Nova Pro vision)
- Default browser installed
- Internet connection

### Optional
- Larger screen resolution = better vision accuracy
- Faster internet = quicker page loads

---

## Examples in Conversation

### Example 1: Live Gaming Stream

**User:** "Nivora, play recently repo tamil gaming live"

**Nivora:** "Now playing: 'BGMI Live - Road to Conqueror' by Repo Gaming 🔴 LIVE
Channel: Repo Gaming
Confidence: high"

---

### Example 2: Latest Upload

**User:** "Nivora, what's MrBeast's latest video?"

**Nivora:** *[Searches and plays]*
"Now playing: 'I Survived 50 Hours In Antarctica' by MrBeast
Confidence: high"

---

### Example 3: Find Multiple Streams

**User:** "Nivora, find live gaming streams"

**Nivora:** "Found 5 live stream(s) for 'gaming':

1. BGMI LIVE - Ranked Push | Road to Conqueror
   Channel: Scout OP
   Viewers: 45K

2. Valorant India Live - Esports Tournament
   Channel: Skyesports
   Viewers: 12K

3. GTA V RP Live Stream
   Channel: CarryMinati Gaming
   Viewers: 8.5K

..."

---

### Example 4: Control Playback

**User:** "Nivora, make it fullscreen"

**Nivora:** *[Presses F key]*
"Toggled fullscreen"

**User:** "Nivora, pause the video"

**Nivora:** *[Presses K key]*
"Toggled play/pause"

---

## Troubleshooting

### Video not found
- Try making query more specific
- Check if channel/video name is correct
- Try adding "official" or channel name

### Wrong video playing
- Add more details to query (channel name, upload date)
- Use `youtube_find_live_streams` first to see options
- Use `youtube_play_by_url` with exact URL

### Vision AI errors
- Ensure AWS Bedrock is configured
- Check internet connection
- Try again after page fully loads

### Playback not starting
- Video page opens but may need manual click
- Some videos have age restrictions
- Ad blockers may interfere

---

## Integration with Agent

The YouTube automation tools are already added to `tools.py` and available to Nivora.

**To use in prompts:**

Add to Nivora's instructions:
```
YOUTUBE AUTOMATION:
You can search and play YouTube videos and live streams using natural language.

Tools available:
- youtube_search_and_play(query, prefer_live) - Main tool for playing videos
- youtube_find_live_streams(channel_or_topic) - List active live streams
- youtube_control_playback(action) - Control video playback

Examples:
- User: "play recently repo tamil gaming live"
  -> Call youtube_search_and_play("recently repo tamil gaming live", prefer_live=True)

- User: "find gaming live streams"
  -> Call youtube_find_live_streams("gaming")

- User: "make it fullscreen"
  -> Call youtube_control_playback("fullscreen")
```

---

## Future Enhancements

🔮 **Potential additions:**
- Playlist creation/management
- Subscribe to channels
- Like/comment on videos
- Queue multiple videos
- YouTube Music integration
- Download videos (if legal)
- Timestamp navigation
- Quality selection

---

## Testing

To test the YouTube automation:

```bash
# Test the module directly
python youtube_automation.py

# Test with Nivora
python multi_agent_livekit.py
# Then say: "play lofi hip hop radio live"
```

---

## Success! 🎉

Your Nivora assistant can now:
✅ Search YouTube intelligently
✅ Play videos and live streams automatically
✅ Find specific channels and content
✅ Control playback with voice
✅ Handle complex natural language queries

Try saying: **"Play recently repo tamil gaming live"** and watch it work!

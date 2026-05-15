# 🎵 Spotify Automation - Complete Guide

## 🎉 Overview

Nivora now has **full Spotify automation** using Spotipy! Control everything with your voice:
- ✅ Play songs, albums, artists, playlists
- ✅ Search Spotify library
- ✅ Add to queue
- ✅ Like/unlike songs
- ✅ Create and manage playlists
- ✅ Control playback (pause, skip, shuffle, repeat)
- ✅ Set volume
- ✅ Play by mood (chill, workout, party, etc.)

**And Nivora now has a sweet female voice (Priya)!** 🎤

---

## 🚀 Quick Setup (5 Steps)

### Step 1: Get Spotify Credentials

1. Go to [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
2. Log in with your Spotify account
3. Click **"Create App"**
4. Fill in:
   - **App name**: "Nivora Voice Assistant"
   - **App description**: "Voice-controlled Spotify automation"
   - **Redirect URI**: `http://localhost:8888/callback`
5. Check the box for Developer Terms
6. Click **"Save"**
7. You'll see your **Client ID** and **Client Secret**

### Step 2: Add Credentials to .env

Open your `.env` file and add:
```env
SPOTIFY_CLIENT_ID=your_client_id_here
SPOTIFY_CLIENT_SECRET=your_client_secret_here
```

### Step 3: Get Refresh Token

**IMPORTANT:** Spotify requires HTTPS redirect URIs, but `http://localhost` may not work in the dashboard.

We provide **TWO methods** to get your refresh token:

---

#### **Method 1: Automated Server (RECOMMENDED)** ⭐

This runs a local web server that catches the callback automatically.

```bash
python get_spotify_token_server.py
```

**What it does:**
1. Starts local server on port 8888
2. Opens browser for authorization
3. Catches callback automatically
4. Saves token to .env file

**Just click "Agree" when prompted!**

---

#### **Method 2: Manual Code Entry (Fallback)**

If Method 1 doesn't work, use this:

```bash
python get_spotify_token_manual.py
```

**What it does:**
1. Opens browser for authorization
2. You copy the redirect URL (even if it shows error)
3. Paste it back in terminal
4. Gets your refresh token

---

### Step 3b: For Spotify Dashboard Setup

**If adding redirect URI in Spotify Dashboard:**

Since `http://localhost:8888/callback` shows as "not secure", you have two options:

**Option A: Use the scripts above** (they handle this automatically)

**Option B: Alternative redirect URIs:**
- Try: `http://127.0.0.1:8888/callback` (IP instead of localhost)
- Or use: `https://nivora-callback.com/callback` (if you have a domain)

**For most users:** Just use the provided scripts - they work without dashboard changes!

### Step 4: Verify Setup

Test that Spotify API works:
```bash
python -c "from spotify_api import is_configured; print('✓ Configured' if is_configured() else '✗ Not configured')"
```

Expected output: `✓ Configured`

### Step 5: Start Nivora

```bash
python agent.py start
```

**Test it:**
Say: *"Play Blinding Lights by The Weeknd"*

---

## 🎤 Voice Commands

### Playing Music

**Songs:**
```
"Play Blinding Lights"
"Play Shape of You by Ed Sheeran"
"Play Bohemian Rhapsody"
```

**Albums:**
```
"Play the album Midnights"
"Play After Hours by The Weeknd"
"Play 1989"
```

**Artists:**
```
"Play Taylor Swift"
"Play Drake"
"Play The Weeknd"
```

**Playlists:**
```
"Play Today's Top Hits"
"Play Chill Vibes playlist"
"Play my workout playlist"
```

**By Mood:**
```
"Play chill music"
"Play workout music"
"Play party music"
"Play focus music"
"Play romantic music"
```

### Playback Control

```
"Pause" / "Pause Spotify"
"Resume" / "Play"
"Next song" / "Skip"
"Previous song" / "Go back"
"Shuffle on" / "Turn on shuffle"
"Shuffle off" / "Turn off shuffle"
"Repeat this song"
"Repeat playlist"
"Turn off repeat"
"Set volume to 50"
"Max volume" / "Volume 100"
```

### Queue Management

```
"Add Starboy to queue"
"Add Levitating to the queue"
"Queue up As It Was"
```

### Like/Save Songs

```
"Like this song"
"Save this song"
"Unlike this song"
"Remove from liked songs"
```

### Information

```
"What's playing?"
"What song is this?"
"Show playback details"
"Get current song info"
```

### Search

```
"Search for Taylor Swift songs"
"Search Spotify for Coldplay"
"Find playlists about chill"
"Search for workout music"
```

### Playlists

```
"Create a playlist called My Favorites"
"Add this song to My Favorites"
"Show my playlists"
"List my playlists"
```

---

## 🛠️ Available Tools

### 1. **Playing Music**

| Tool | Description | Example |
|------|-------------|---------|
| `spotify_play_track` | Play a song | *"Play Starboy"* |
| `spotify_play_album` | Play an album | *"Play Midnights"* |
| `spotify_play_artist` | Play an artist | *"Play Drake"* |
| `spotify_play_playlist` | Play a playlist | *"Play Chill Vibes"* |
| `spotify_play_by_mood` | Play by mood | *"Play workout music"* |

### 2. **Playback Control**

| Tool | Description | Example |
|------|-------------|---------|
| `spotify_pause` | Pause playback | *"Pause"* |
| `spotify_resume` | Resume playback | *"Resume"* |
| `spotify_next` | Next track | *"Next song"* |
| `spotify_previous` | Previous track | *"Previous"* |
| `spotify_set_volume` | Set volume 0-100 | *"Volume 50"* |
| `spotify_shuffle` | Toggle shuffle | *"Shuffle on"* |
| `spotify_repeat` | Set repeat mode | *"Repeat this song"* |

### 3. **Queue & Favorites**

| Tool | Description | Example |
|------|-------------|---------|
| `spotify_add_to_queue` | Add song to queue | *"Queue up Starboy"* |
| `spotify_like_current_song` | Like current song | *"Like this song"* |
| `spotify_unlike_current_song` | Unlike song | *"Unlike this"* |

### 4. **Information**

| Tool | Description | Example |
|------|-------------|---------|
| `spotify_now_playing` | Get current song | *"What's playing?"* |
| `spotify_current_playback_details` | Detailed info | *"Show details"* |

### 5. **Search**

| Tool | Description | Example |
|------|-------------|---------|
| `spotify_search` | Search Spotify | *"Search for Coldplay"* |

### 6. **Playlists**

| Tool | Description | Example |
|------|-------------|---------|
| `spotify_create_playlist` | Create playlist | *"Create playlist My Mix"* |
| `spotify_add_current_to_playlist` | Add to playlist | *"Add to My Favorites"* |
| `spotify_list_my_playlists` | List playlists | *"Show playlists"* |

---

## 📊 Mood-Based Playback

Nivora can play music based on your mood or activity:

| Mood | What It Plays |
|------|---------------|
| **happy** | Upbeat, cheerful music |
| **sad** | Relaxing, melancholic music |
| **chill** | Lo-fi, chill beats |
| **party** | Dance, party hits |
| **workout** | High-energy gym music |
| **focus** | Concentration, study music |
| **romantic** | Love songs |
| **sleep** | Relaxation, sleep sounds |
| **motivation** | Pump-up, motivational tracks |

**Usage:**
```
"Play chill music"
"Play workout music"
"Play focus music"
```

---

## 🎯 Example Workflows

### Workflow 1: Start Your Day
```
You: "Good morning Nivora, play some happy music"
Nivora: [Plays upbeat playlist]

You: "What's playing?"
Nivora: "Playing 'Good 4 U' by Olivia Rodrigo from the album Sour."

You: "Like this song"
Nivora: "Added 'Good 4 U' to your Liked Songs."
```

### Workflow 2: Workout Session
```
You: "Play workout music"
Nivora: [Plays workout playlist]

You: "Add Eye of the Tiger to queue"
Nivora: "Added to queue: Eye of the Tiger by Survivor."

You: "Turn on shuffle"
Nivora: "Shuffle enabled."
```

### Workflow 3: Discover New Music
```
You: "Search Spotify for Billie Eilish"
Nivora: [Lists top tracks, albums, and playlists]

You: "Play the album Happier Than Ever"
Nivora: "Playing album: Happier Than Ever by Billie Eilish."
```

### Workflow 4: Playlist Management
```
You: "Create a playlist called Road Trip 2024"
Nivora: "Created public playlist 'Road Trip 2024'."

You: "Add this song to Road Trip 2024"
Nivora: "Added 'Blinding Lights' to playlist 'Road Trip 2024'."

You: "Show my playlists"
Nivora: [Lists all your playlists]
```

---

## 🐛 Troubleshooting

### "Spotify API is not configured"

**Solution:**
1. Check `.env` has all three values:
   - `SPOTIFY_CLIENT_ID`
   - `SPOTIFY_CLIENT_SECRET`
   - `SPOTIFY_REFRESH_TOKEN`
2. Run verification:
   ```bash
   python -c "from spotify_api import is_configured; print(is_configured())"
   ```

### "Failed to play. Is Spotify open and a device active?"

**Solution:**
1. Open Spotify app (desktop or web)
2. Play ANY song once to activate device
3. Try command again

### "Playback failed"

**Common causes:**
- Spotify app is closed
- No active device
- Free Spotify account (some features require Premium)

**Solution:**
1. Open Spotify
2. Click play on any song
3. Try again

### "Search failed" or "No results found"

**Solution:**
- Check internet connection
- Verify search query spelling
- Try broader search terms

### Token expired

**Solution:**
Refresh tokens last a long time, but if expired:
```bash
python get_spotify_token.py
```
Update `SPOTIFY_REFRESH_TOKEN` in `.env`

---

## 🔐 Spotify Scopes Explained

The app requests these permissions:

| Scope | What It Allows |
|-------|----------------|
| `user-modify-playback-state` | Control playback (play, pause, skip) |
| `user-read-playback-state` | Read what's currently playing |
| `user-read-currently-playing` | Get current track info |
| `playlist-modify-public` | Create/edit public playlists |
| `playlist-modify-private` | Create/edit private playlists |
| `user-library-read` | Read your saved songs |
| `user-library-modify` | Like/unlike songs |
| `user-read-email` | Get your email (for user ID) |

**These are safe** - Nivora only controls Spotify, doesn't access sensitive data.

---

## 🎨 Technical Details

### Architecture

```
Voice Input → Nivora Agent → Spotify Tool Selection
                    ↓
              spotify_tools_advanced.py
                    ↓
              spotify_api.py (spotipy wrapper)
                    ↓
         Spotify Web API (OAuth 2.0)
                    ↓
              Your Spotify Account
```

### How It Works

1. **Voice command** received by Nivora
2. **LLM decides** which Spotify tool to use
3. **Tool called** with parameters
4. **spotify_api.py** makes API request
5. **Spotipy library** handles OAuth
6. **Spotify API** executes action
7. **Result returned** to user

### Token Refresh

- Access tokens expire after 1 hour
- Refresh token **never expires** (unless revoked)
- `spotify_api.py` automatically refreshes tokens
- You only need to run `get_spotify_token.py` once

---

## 📝 Files Structure

```
spotify_tools_advanced.py    # All Spotify tools (NEW)
spotify_api.py               # Spotify API wrapper (using spotipy)
get_spotify_token.py         # Token generator script
tools.py                     # Updated with Spotify tools
prompts.py                   # Updated with Spotify instructions
agent.py                     # Updated voice to female (priya)
```

---

## 🎤 Voice Change Summary

**Old:** Male voice (shubh)
**New:** Female voice (priya) - Sweet and clear!

Changed in `agent.py`:
```python
tts=sarvam.TTS(
    model="bulbul:v3",
    speaker="priya",  # ← Changed to female
    target_language_code="en-IN",
    ...
)
```

---

## ✅ Setup Checklist

```
□ Spotify Developer App created
□ Client ID and Secret added to .env
□ Ran get_spotify_token.py
□ Refresh token added to .env
□ Verified configuration (python -c "...")
□ Spotify app open (desktop/web)
□ Played a song to activate device
□ Started Nivora agent
□ Tested voice command
□ Nivora responds in female voice (priya)
```

---

## 🎉 Summary

**What You Got:**

1. ✅ **20+ Spotify tools** for complete control
2. ✅ **Voice-activated** - Just ask naturally
3. ✅ **Spotipy-powered** - Reliable Spotify Web API
4. ✅ **Female voice** - Sweet "priya" voice
5. ✅ **Mood-based playback** - 9 preset moods
6. ✅ **Queue management** - Add songs on the fly
7. ✅ **Playlist control** - Create and manage
8. ✅ **Like/save** - Build your library
9. ✅ **Search** - Find anything on Spotify
10. ✅ **Full playback control** - Play, pause, skip, shuffle, repeat, volume

**Ready to use!** 🚀

---

## 🆘 Getting Help

1. **Check this guide** first
2. **Verify setup** with checklist
3. **Test individual tools** in Python:
   ```python
   from spotify_tools_advanced import spotify_play_track
   # Test it
   ```
4. **Check logs** for errors
5. **Restart Spotify** app
6. **Re-run token script** if auth issues

---

**Enjoy your voice-controlled Spotify experience with Nivora! 🎵🎤**

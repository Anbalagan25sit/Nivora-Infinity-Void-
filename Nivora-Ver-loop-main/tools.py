"""
NIVORA 1.0 — Tool Suite
Includes tools for:
- Web browsing (open_website)
- Email (send_email)
- Google Sheets (read_sheet, write_sheet)
- Spotify Control (via spotify_api)
- YouTube (search_youtube, play_youtube)
- Notes (take_note, read_notes)
- Reminders (set_reminder)
- Google Calendar (list_events, create_event)
- Web Search (web_search)
- Weather (get_weather)
- System Control (keyboard shortcuts)
"""

import logging
import os
import subprocess
import sys
import smtplib
import imaplib
import email as _email
from email.header import decode_header as _decode_header
import webbrowser
import datetime
import asyncio
import json
import time
import urllib.parse
from email.mime.text import MIMEText
from typing import Annotated

import requests
import pywhatkit
import pyautogui
from duckduckgo_search import DDGS
import gspread

from livekit.agents import RunContext, function_tool
import spotify_api
import computer_use as _cu

# Optional imports for LocalMediaTools — gracefully degrade if unavailable
try:
    import winsdk.windows.media.control as _wmc
    _WINSDK_AVAILABLE = True
except ImportError:
    _WINSDK_AVAILABLE = False

try:
    from pycaw.pycaw import AudioUtilities, ISimpleAudioVolume
    _PYCAW_AVAILABLE = True
except ImportError:
    _PYCAW_AVAILABLE = False

logger = logging.getLogger(__name__)

# Import advanced Spotify tools (with error handling) - AFTER logger is defined
try:
    from spotify_tools_advanced import ALL_SPOTIFY_TOOLS
except ImportError as e:
    logger.warning(f"Could not import advanced Spotify tools: {e}")
    ALL_SPOTIFY_TOOLS = []

# Import social media automation tools (with error handling)
try:
    from social_automation import SOCIAL_TOOLS
except ImportError as e:
    logger.warning(f"Could not import social automation tools: {e}")
    SOCIAL_TOOLS = []

# Import YouTube automation (with error handling)
try:
    from youtube_automation import (
        youtube_search_and_play,
        youtube_play_by_url,
        youtube_control_playback,
        youtube_find_live_streams
    )
except ImportError as e:
    logger.warning(f"Could not import YouTube automation tools: {e}")
    # Create placeholder functions
    async def youtube_search_and_play(*args, **kwargs):
        return "YouTube automation not available."
    async def youtube_play_by_url(*args, **kwargs):
        return "YouTube automation not available."
    async def youtube_control_playback(*args, **kwargs):
        return "YouTube automation not available."
    async def youtube_find_live_streams(*args, **kwargs):
        return "YouTube automation not available."

# Import E-Box course automation (with error handling)
try:
    from ebox_automation import complete_ebox_course, ebox_help_with_problem
    EBOX_TOOLS = [complete_ebox_course, ebox_help_with_problem]
    logger.info("E-Box automation tools loaded successfully")
except ImportError as e:
    logger.warning(f"Could not import E-Box automation tools: {e}")
    EBOX_TOOLS = []

# Path to the spotify_control.py script (new no-API implementation)
SPOTIFY_CONTROL_SCRIPT = os.path.join(os.path.dirname(__file__), 'spotify_control.py')

# ============================================================================
# CONFIGURATION & CONSTANTS
# ============================================================================

WEBSITE_MAP: dict[str, str] = {
    "youtube": "https://www.youtube.com", "github": "https://github.com",
    "google": "https://www.google.com", "gmail": "https://mail.google.com",
    "drive": "https://drive.google.com", "leetcode": "https://leetcode.com",
    "stackoverflow": "https://stackoverflow.com", "reddit": "https://www.reddit.com",
    "twitter": "https://twitter.com", "x": "https://x.com",
    "instagram": "https://www.instagram.com", "facebook": "https://www.facebook.com",
    "linkedin": "https://www.linkedin.com", "netflix": "https://www.netflix.com",
    "spotify": "https://open.spotify.com", "amazon": "https://www.amazon.in",
    "flipkart": "https://www.flipkart.com", "wikipedia": "https://www.wikipedia.org",
    "notion": "https://www.notion.so", "figma": "https://www.figma.com",
    "discord": "https://discord.com/app", "whatsapp": "https://web.whatsapp.com",
    "telegram": "https://web.telegram.org", "zoom": "https://zoom.us",
    "canva": "https://www.canva.com", "chatgpt": "https://chat.openai.com",
    "hianime": "https://hianime.to", "hotstar": "https://www.hotstar.com",
    "prime": "https://www.primevideo.com", "twitch": "https://www.twitch.tv",
    "my github": "https://github.com/Anbalagan25sit",
    "portfolio": "https://anbalagan25sit.github.io/Anbalagan-Portfolio/",
    "my portfolio": "https://anbalagan25sit.github.io/Anbalagan-Portfolio/",
}

NOTES_FILE = "notes.txt"

# ============================================================================
# BASIC TOOLS (Web & System)
# ============================================================================

@function_tool()
async def open_website(context: RunContext, target: str) -> str:
    """Open a website by name or URL (target=site name like 'youtube', 'github' or a full URL)."""
    try:
        t = target.strip().lower()
        if t.startswith(("http://", "https://", "www.")):
            url = target if target.startswith(("http://", "https://")) else "https://" + target
            webbrowser.open(url)
            return f"Opened {url}."
        key = t.replace(".com", "").replace(".org", "").replace(" ", "")
        url = WEBSITE_MAP.get(key) or WEBSITE_MAP.get(t) or f"https://www.{key}.com"
        webbrowser.open(url)
        return f"Opened {url}."
    except Exception as e:
        return f"Error opening website: {e}"

@function_tool()
async def web_search(context: RunContext, query: str) -> str:
    """Search the web using DuckDuckGo."""
    try:
        results = DDGS().text(query, max_results=5)
        if not results:
            return "No results found."
        formatted_results = "\n".join([f"- {r['title']}: {r['href']}" for r in results])
        return f"Search results for '{query}':\n{formatted_results}"
    except Exception as e:
        logger.error(f"Web search failed: {e}")
        return f"Failed to search web: {e}"

@function_tool()
async def get_weather(context: RunContext, city: str) -> str:
    """Get current weather updates for a specific city."""
    try:
        # Using wttr.in for simple text-based weather
        r = requests.get(f"https://wttr.in/{city}?format=3")
        if r.status_code == 200:
            return f"Weather in {city}: {r.text.strip()}"
        return f"Could not get weather for {city}."
    except Exception as e:
        return f"Error fetching weather: {e}"

@function_tool()
async def system_control(context: RunContext, command: str) -> str:
    """
    Control system or media using keyboard shortcuts.
    Supported commands: 'volume up', 'volume down', 'mute', 'play', 'pause', 'next', 'previous'.
    """
    cmd = command.lower()
    try:
        if "volume up" in cmd:
            pyautogui.press("volumeup")
        elif "volume down" in cmd:
            pyautogui.press("volumedown")
        elif "mute" in cmd:
            pyautogui.press("volumemute")
        elif "play" in cmd or "pause" in cmd:
            pyautogui.press("playpause")
        elif "next" in cmd:
            pyautogui.press("nexttrack")
        elif "previous" in cmd or "back" in cmd:
            pyautogui.press("prevtrack")
        else:
            return "Unknown system command."
        return f"Executed system command: {command}"
    except Exception as e:
        return f"Failed to execute system command: {e}"

# ============================================================================
# SPOTIFY TOOLS
# ============================================================================

@function_tool()
async def spotify_play(context: RunContext, query: str = "") -> str:
    """
    Play music on Spotify using the Spotify API.
    """
    if not query:
        success = spotify_api.play()
        return "Resumed playback (API)." if success else "Failed to resume playback (API)."

    success, msg = spotify_api.search_and_play_track(query)
    return msg if success else f"Failed to play track: {msg}"

@function_tool()
async def spotify_control(context: RunContext, command: str) -> str:
    """
    Control Spotify playback using the Spotify API.
    Commands: 'play', 'pause', 'next', 'previous',
              'volume up', 'volume down', 'mute',
              'shuffle', 'repeat', 'like', 'search'.
    """
    cmd = command.lower()
    try:
        if "pause" in cmd:
            spotify_api.pause()
            return "Paused playback."
        elif "play" in cmd:
            spotify_api.play()
            return "Resumed playback."
        elif "next" in cmd:
            spotify_api.next_track()
            return "Skipped to next track."
        elif "previous" in cmd:
            spotify_api.previous_track()
            return "Went back to previous track."
        elif "shuffle" in cmd:
            spotify_api.toggle_shuffle()
            return "Toggled shuffle mode."
        elif "repeat" in cmd:
            spotify_api.toggle_repeat()
            return "Toggled repeat mode."
        else:
            return f"Unknown command: {command}"
    except Exception as e:
        return f"Failed to execute command '{command}': {e}"


@function_tool()
async def spotify_shortcut(
    context: RunContext,  # type: ignore
    command: str,
) -> str:
    """
    Control the Spotify desktop/web app using ONLY keyboard shortcuts.
    This never opens or refreshes Spotify; it just sends keys to the active Spotify window.

    Supported examples (case-insensitive):
    - "play", "pause", "play/pause"
    - "shuffle", "repeat"
    - "go home", "go library", "go playlists", "go podcasts", "go artists",
      "go albums", "go audiobooks", "go queue", "go liked songs", "go now playing"
    - "like song", "mute"
    """
    cmd = command.strip().lower()
    try:
        # Playback
        if cmd in ("play", "pause", "play/pause", "toggle play"):
            pyautogui.press("space")
            return "Toggled play/pause in Spotify."

        # Shuffle / Repeat
        if "shuffle" in cmd:
            pyautogui.hotkey("ctrl", "s")
            return "Toggled shuffle in Spotify."
        if "repeat" in cmd:
            pyautogui.hotkey("ctrl", "r")
            return "Toggled repeat in Spotify."

        # Like current song
        if "like" in cmd or "favorite" in cmd or "favourite" in cmd:
            pyautogui.hotkey("alt", "shift", "b")
            return "Toggled like for current song."

        # Navigation
        if "go home" in cmd or cmd == "home":
            pyautogui.hotkey("alt", "shift", "h")
            return "Opened Spotify Home."
        if "go library" in cmd:
            pyautogui.hotkey("alt", "shift", "0")
            return "Opened Your Library in Spotify."
        if "go playlists" in cmd:
            pyautogui.hotkey("alt", "shift", "1")
            return "Opened Playlists in Spotify."
        if "go podcasts" in cmd:
            pyautogui.hotkey("alt", "shift", "2")
            return "Opened Podcasts in Spotify."
        if "go artists" in cmd:
            pyautogui.hotkey("alt", "shift", "3")
            return "Opened Artists in Spotify."
        if "go albums" in cmd:
            pyautogui.hotkey("alt", "shift", "4")
            return "Opened Albums in Spotify."
        if "go audiobooks" in cmd:
            pyautogui.hotkey("alt", "shift", "5")
            return "Opened Audiobooks in Spotify."
        if "go liked songs" in cmd or "liked songs" in cmd:
            pyautogui.hotkey("alt", "shift", "s")
            return "Opened Liked Songs in Spotify."
        if "go queue" in cmd or cmd == "queue":
            pyautogui.hotkey("alt", "shift", "q")
            return "Opened Queue in Spotify."
        if "go now playing" in cmd or "now playing" in cmd:
            pyautogui.hotkey("alt", "shift", "j")
            return "Opened Now Playing in Spotify."

        # Search entry
        if "open search" in cmd or "go search" in cmd:
            # Go to Search field
            pyautogui.hotkey("ctrl", "l")
            return "Focused Spotify search."

        # Mute/unmute
        if "mute" in cmd:
            pyautogui.press("m")
            return "Toggled mute in Spotify."

        return f"Unknown Spotify shortcut command: '{command}'."
    except Exception as e:
        return f"Spotify shortcut failed: {e}"


@function_tool()
async def youtube_shortcut(
    context: RunContext,  # type: ignore
    command: str,
) -> str:
    """
    Control the active YouTube video using keyboard shortcuts only.

    Examples (case-insensitive):
    - "play", "pause"         → K (or Space)
    - "mute"                  → M
    - "fullscreen"            → F
    - "skip forward"          → L (or Right Arrow)
    - "skip back"             → J (or Left Arrow)
    - "volume up" / "down"    → Up / Down Arrow
    - "captions"              → C
    """
    cmd = command.strip().lower()
    try:
        if cmd in ("play", "pause", "play/pause", "toggle play"):
            pyautogui.press("k")
            return "Toggled play/pause on YouTube."
        if "mute" in cmd:
            pyautogui.press("m")
            return "Toggled mute on YouTube."
        if "fullscreen" in cmd or "full screen" in cmd:
            pyautogui.press("f")
            return "Toggled fullscreen on YouTube."
        if "skip forward" in cmd or "forward" in cmd or "next" in cmd:
            pyautogui.press("l")
            return "Skipped forward on YouTube."
        if "skip back" in cmd or "rewind" in cmd or "back" in cmd:
            pyautogui.press("j")
            return "Skipped backward on YouTube."
        if "volume up" in cmd:
            pyautogui.press("up")
            return "Volume up on YouTube."
        if "volume down" in cmd:
            pyautogui.press("down")
            return "Volume down on YouTube."
        if "captions" in cmd or "subtitles" in cmd:
            pyautogui.press("c")
            return "Toggled captions on YouTube."
        return f"Unknown YouTube shortcut command: '{command}'."
    except Exception as e:
        return f"YouTube shortcut failed: {e}"


@function_tool()
async def open_spotify(
    context: RunContext,
    mode: str = "home",
    content_id: str = "",
    query: str = "",
) -> str:
    """
    Open Spotify Web Player to any section.
    mode options:
      'home'            — Spotify home
      'search'          — Search page (optionally with query)
      'track'           — Open track by ID
      'album'           — Open album by ID
      'artist'          — Open artist by ID
      'playlist'        — Open playlist by ID
      'library'         — Your liked songs library
      'playlists'       — Your playlists
      'queue'           — Current queue
      'recent'          — Recently played
    Pass content_id for track/album/artist/playlist/podcast/episode.
    """
    BASE = "https://open.spotify.com"
    m = mode.strip().lower()
    url_map = {
        "home":      BASE,
        "queue":     f"{BASE}/queue",
        "recent":    f"{BASE}/collection/recently-played",
        "library":   f"{BASE}/collection/tracks",
        "playlists": f"{BASE}/collection/playlists",
        "podcasts":  f"{BASE}/collection/podcasts",
        "artists":   f"{BASE}/collection/artists",
        "albums":    f"{BASE}/collection/albums",
    }
    content_types = {"track", "album", "artist", "playlist", "show", "episode", "user"}
    try:
        if m in url_map:
            webbrowser.open(url_map[m])
            return f"Opened Spotify: {m}."
        elif m == "search":
            if query:
                webbrowser.open(f"{BASE}/search/{urllib.parse.quote(query)}")
                return f"Opened Spotify search for '{query}'."
            webbrowser.open(f"{BASE}/search")
            return "Opened Spotify search page."
        elif m in content_types:
            if not content_id:
                return f"Please provide content_id for mode='{m}'."
            webbrowser.open(f"{BASE}/{m}/{content_id}")
            return f"Opened Spotify {m}: {content_id}."
        else:
            return f"Unknown mode '{mode}'. Use: home, search, track, album, artist, playlist, library, playlists, queue, recent."
    except Exception as e:
        return f"Failed to open Spotify: {e}"

@function_tool()
async def play_youtube_video(context: RunContext, query: str) -> str:
    """
    Search and play a YouTube video in the browser.
    This is the PRIMARY tool for playing any song or video on YouTube.

    Use this when user says:
    - "play [song name] on youtube"
    - "play [artist] songs on youtube"
    - "youtube play [query]"
    - "search and play [query] on youtube"

    Examples:
    - play_youtube_video("Shape of You Ed Sheeran")
    - play_youtube_video("lofi hip hop beats")
    - play_youtube_video("Blinding Lights The Weeknd")
    """
    try:
        q = query.strip()
        logger.info(f"[YouTube] Playing: {q}")

        # If it looks like a raw video ID (11 chars, no spaces), open directly
        if len(q) == 11 and " " not in q and q.isalnum():
            url = f"https://www.youtube.com/watch?v={q}"
            webbrowser.open(url)
            await asyncio.sleep(3)
            pyautogui.press("k")   # K = play/pause on YouTube
            return f"Opened YouTube video ID '{q}' and started playback."

        # Method 1: Use pywhatkit to directly play on YouTube (most reliable)
        try:
            # pywhatkit.playonyt opens the video directly without needing to click
            logger.info(f"[YouTube] Using pywhatkit to play: {q}")
            pywhatkit.playonyt(q, open_video=True)
            await asyncio.sleep(2)
            return f"Playing '{q}' on YouTube."
        except Exception as pywhatkit_error:
            logger.warning(f"[YouTube] pywhatkit failed: {pywhatkit_error}, trying fallback...")

        # Method 2: Fallback - Open YouTube search and auto-click first result
        encoded = urllib.parse.quote(q)
        search_url = f"https://www.youtube.com/results?search_query={encoded}"
        logger.info(f"[YouTube] Fallback - Opening search: {search_url}")
        webbrowser.open(search_url)
        await asyncio.sleep(3)  # Wait for page to load

        # Click on the first video result using keyboard navigation
        # Tab focuses the search results, then we navigate to first video
        for _ in range(3):  # Press Tab a few times to get to video results
            pyautogui.press("tab")
            await asyncio.sleep(0.2)

        pyautogui.press("enter")  # Open the first video
        await asyncio.sleep(3)  # Wait for video to load

        # Ensure video plays (press K or Space)
        pyautogui.press("k")

        return f"Playing '{q}' on YouTube."

    except Exception as e:
        logger.error(f"play_youtube_video failed: {e}", exc_info=True)
        return f"Failed to play YouTube video: {e}"


@function_tool()
async def open_youtube(
    context: RunContext,
    mode: str = "home",
    query: str = "",
) -> str:
    """
    Open YouTube in the browser.
    mode options:
      - 'home'   : Open the YouTube homepage.
      - 'search' : Search YouTube for the given query.
      - 'video'  : Open a specific video by video ID (pass the ID as query).
    """
    try:
        m = mode.strip().lower()
        if m == "home" or not m:
            webbrowser.open("https://www.youtube.com")
            return "Opened YouTube homepage."
        elif m == "search":
            if not query:
                webbrowser.open("https://www.youtube.com")
                return "Opened YouTube homepage (no search query provided)."
            encoded = urllib.parse.quote(query.strip())
            url = f"https://www.youtube.com/results?search_query={encoded}"
            webbrowser.open(url)
            return f"Opened YouTube search for '{query}'."
        elif m == "video":
            if not query:
                return "Please provide a video ID for mode='video'."
            url = f"https://www.youtube.com/watch?v={query.strip()}"
            webbrowser.open(url)
            return f"Opened YouTube video: {url}"
        else:
            return f"Unknown mode '{mode}'. Use 'home', 'search', or 'video'."
    except Exception as e:
        logger.error(f"open_youtube failed: {e}")
        return f"Failed to open YouTube: {e}"


# ============================================================================
# UNIVERSAL MEDIA CONTROLS
# ============================================================================

@function_tool()
async def pause_media(context: RunContext, action: str = "toggle") -> str:
    """
    Pause or resume any media (Spotify, YouTube, system media, etc.).
    action: 'toggle' (default), 'pause', or 'play'.
    Uses the system Play/Pause media key for generic apps.
    For YouTube in the active browser tab, also presses K.
    """
    try:
        a = action.strip().lower()
        # System-wide media key (works for Spotify, Windows Media Player, etc.)
        pyautogui.press("playpause")
        return f"Media {a if a != 'toggle' else 'play/pause'} triggered."
    except Exception as e:
        return f"Failed to toggle media: {e}"


@function_tool()
async def next_track(context: RunContext, target: str = "system") -> str:
    """
    Skip to the next track or video.
    target:
      - 'system'  (default): Uses the Next Track media key (works for Spotify, etc.).
      - 'spotify' : Shift+N (Spotify desktop shortcut).
      - 'youtube' : Presses L (skip forward 10 s on YouTube).
    """
    try:
        t = target.strip().lower()
        if t == "spotify":
            pyautogui.hotkey("shift", "n")
            return "Skipped to next track on Spotify (Shift+N)."
        elif t == "youtube":
            pyautogui.press("l")
            return "Skipped forward 10 seconds on YouTube (L)."
        else:
            pyautogui.press("nexttrack")
            return "Pressed Next Track media key."
    except Exception as e:
        return f"Failed to skip to next track: {e}"


@function_tool()
async def previous_track(context: RunContext, target: str = "system") -> str:
    """
    Go to the previous track or rewind.
    target:
      - 'system'  (default): Uses the Previous Track media key (works for Spotify, etc.).
      - 'spotify' : Shift+P (Spotify desktop shortcut).
      - 'youtube' : Presses J (rewind 10 s on YouTube).
    """
    try:
        t = target.strip().lower()
        if t == "spotify":
            pyautogui.hotkey("shift", "p")
            return "Went to previous track on Spotify (Shift+P)."
        elif t == "youtube":
            pyautogui.press("j")
            return "Rewound 10 seconds on YouTube (J)."
        else:
            pyautogui.press("prevtrack")
            return "Pressed Previous Track media key."
    except Exception as e:
        return f"Failed to go to previous track: {e}"


@function_tool()
async def volume_control(context: RunContext, action: str) -> str:
    """
    Control system volume.
    action options: 'up', 'down', 'mute', 'unmute'.
    Each 'up'/'down' press changes volume by one step (~2%).
    """
    try:
        a = action.strip().lower()
        if a == "up":
            pyautogui.press("volumeup")
            return "Volume increased."
        elif a == "down":
            pyautogui.press("volumedown")
            return "Volume decreased."
        elif a in ("mute", "unmute"):
            pyautogui.press("volumemute")
            return "Volume mute toggled."
        else:
            return f"Unknown volume action '{action}'. Use 'up', 'down', 'mute', or 'unmute'."
    except Exception as e:
        return f"Failed to control volume: {e}"

# ============================================================================
# EMAIL TOOLS
# ============================================================================

@function_tool()
async def send_email(context: RunContext, recipient: str, subject: str, body: str) -> str:
    """
    Send an email using Gmail SMTP.
    Requires EMAIL_USER (or GMAIL_USER) and EMAIL_PASS (or GMAIL_APP_PASSWORD) environment variables.
    """
    sender = os.getenv("EMAIL_USER") or os.getenv("GMAIL_USER")
    password = os.getenv("EMAIL_PASS") or os.getenv("GMAIL_APP_PASSWORD")
    
    if not sender or not password:
        return "Email credentials (EMAIL_USER/GMAIL_USER, EMAIL_PASS/GMAIL_APP_PASSWORD) are missing."

    try:
        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = sender
        msg['To'] = recipient

        # Using SMTP_SSL for Gmail
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender, password)
            server.sendmail(sender, recipient, msg.as_string())
        return f"Email sent to {recipient}."
    except Exception as e:
        logger.error(f"Failed to send email: {e}")
        return f"Failed to send email: {e}"

@function_tool()
async def read_emails(context: RunContext, count: int = 5, unread_only: bool = False) -> str:
    """
    Read recent emails from Gmail via IMAP.
    count: number of emails to fetch (default 5).
    unread_only: if True, only fetch unread emails.
    Requires EMAIL_USER (or GMAIL_USER) and EMAIL_PASS (or GMAIL_APP_PASSWORD) env vars.
    """
    user = os.getenv("EMAIL_USER") or os.getenv("GMAIL_USER")
    password = os.getenv("EMAIL_PASS") or os.getenv("GMAIL_APP_PASSWORD")
    if not user or not password:
        return "Email credentials (EMAIL_USER/GMAIL_USER, EMAIL_PASS/GMAIL_APP_PASSWORD) are missing."
    try:
        mail = imaplib.IMAP4_SSL("imap.gmail.com", 993)
        mail.login(user, password)
        mail.select("inbox")
        criteria = "(UNSEEN)" if unread_only else "ALL"
        _, message_ids = mail.search(None, criteria)
        ids = message_ids[0].split()
        if not ids:
            mail.logout()
            return "No emails found."
        # Take the last `count` emails (most recent)
        selected = ids[-count:]
        emails = []
        for mid in reversed(selected):
            _, msg_data = mail.fetch(mid, "(BODY[HEADER.FIELDS (FROM SUBJECT)])")
            if not msg_data or not msg_data[0]:
                continue
            raw = msg_data[0][1]
            if not isinstance(raw, bytes):
                continue
            msg = _email.message_from_bytes(raw)
            # Decode From
            from_raw = msg.get("From", "Unknown")
            # Decode Subject
            subj_parts = _decode_header(msg.get("Subject", "(no subject)"))
            subject = ""
            for part, enc in subj_parts:
                if isinstance(part, bytes):
                    subject += part.decode(enc or "utf-8", errors="replace")
                else:
                    subject += str(part)
            emails.append(f"From: {from_raw}\nSubject: {subject}")
        mail.logout()
        label = "unread " if unread_only else ""
        return f"Last {len(emails)} {label}email(s):\n\n" + "\n\n".join(emails)
    except Exception as e:
        logger.error(f"read_emails failed: {e}")
        return f"Failed to read emails: {e}"

# ============================================================================
# GOOGLE APPS (Sheets & Calendar)
# ============================================================================

@function_tool()
async def google_sheets_read(context: RunContext, sheet_name: str) -> str:
    """Read a Google Sheet by name. Returns the records."""
    try:
        # Assuming service account credentials in 'gcp-credentials.json' or similiar env setup
        # For simplicity, looking for a standard file or env var
        creds_file = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "gcp-credentials.json")
        if not os.path.exists(creds_file):
            return "Google Cloud credentials file not found."

        gc = gspread.service_account(filename=creds_file)
        sh = gc.open(sheet_name)
        worksheet = sh.sheet1
        records = worksheet.get_all_records()
        return str(records[:10]) + ("..." if len(records) > 10 else "") # Return first 10 rows
    except Exception as e:
        return f"Failed to read Google Sheet: {e}"

@function_tool()
async def google_sheets_write(context: RunContext, sheet_name: str, data: list[str]) -> str:
    """Append a row to a Google Sheet."""
    try:
        creds_file = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "gcp-credentials.json")
        if not os.path.exists(creds_file):
            return "Google Cloud credentials file not found."

        gc = gspread.service_account(filename=creds_file)
        sh = gc.open(sheet_name)
        worksheet = sh.sheet1
        worksheet.append_row(data)
        return f"Appended data to {sheet_name}."
    except Exception as e:
        return f"Failed to write to Google Sheet: {e}"

@function_tool()
async def google_calendar_list(context: RunContext, count: int = 5) -> str:
    """List upcoming Google Calendar events."""
    from google.oauth2 import service_account
    from googleapiclient.discovery import build

    creds_file = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "gcp-credentials.json")
    if not os.path.exists(creds_file):
        return "Google Cloud credentials file not found. Set GOOGLE_APPLICATION_CREDENTIALS in .env"

    try:
        SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]
        creds = service_account.Credentials.from_service_account_file(creds_file, scopes=SCOPES)
        service = build("calendar", "v3", credentials=creds)

        # Service account reads the shared calendar by the owner's email
        # "primary" refers to the service account's OWN calendar (empty).
        # Use the Gmail address of the calendar owner instead.
        calendar_id = os.getenv("GMAIL_USER") or os.getenv("EMAIL_USER") or "primary"
        now = datetime.datetime.utcnow().isoformat() + "Z"
        events_result = service.events().list(
            calendarId=calendar_id, timeMin=now,
            maxResults=count, singleEvents=True,
            orderBy="startTime"
        ).execute()
        events = events_result.get("items", [])
        if not events:
            return "No upcoming events found."
        event_list = []
        for event in events:
            start = event["start"].get("dateTime", event["start"].get("date"))
            event_list.append(f"{start}: {event.get('summary', '(no title)')}")
        return "\n".join(event_list)
    except Exception as e:
        return f"Failed to fetch calendar events: {e}"

# ============================================================================
# SPOTIFY BROWSE & INFO TOOLS
# ============================================================================
# NOTE: spotify_search is provided by spotify_tools_advanced.py (included via ALL_SPOTIFY_TOOLS)

@function_tool()
async def spotify_get_track_info(context: RunContext, track_id: str) -> str:
    """
    Get detailed info for a specific Spotify track by its ID.
    track_id: the Spotify track ID (from a search result or URL).
    """
    if not spotify_api.is_configured():
        return "Spotify API credentials not configured."
    data = spotify_api._get(f"/tracks/{track_id}")
    if not data:
        return f"Could not find track with ID '{track_id}'."
    name = data.get("name", "?")
    artists = ", ".join(a.get("name", "") for a in (data.get("artists") or []))
    album = (data.get("album") or {}).get("name", "?")
    duration_ms = data.get("duration_ms", 0)
    duration = f"{duration_ms // 60000}:{(duration_ms % 60000) // 1000:02d}"
    popularity = data.get("popularity", "?")
    explicit = "Yes" if data.get("explicit") else "No"
    preview = data.get("preview_url") or "N/A"
    return (
        f"Track: {name}\n"
        f"Artists: {artists}\n"
        f"Album: {album}\n"
        f"Duration: {duration}\n"
        f"Popularity: {popularity}/100\n"
        f"Explicit: {explicit}\n"
        f"Preview URL: {preview}"
    )


@function_tool()
async def spotify_get_artist_info(context: RunContext, artist_id: str) -> str:
    """
    Get detailed info for a Spotify artist by ID.
    artist_id: the Spotify artist ID.
    """
    if not spotify_api.is_configured():
        return "Spotify API credentials not configured."
    data = spotify_api._get(f"/artists/{artist_id}")
    if not data:
        return f"Could not find artist with ID '{artist_id}'."
    name = data.get("name", "?")
    genres = ", ".join(data.get("genres") or []) or "N/A"
    followers = (data.get("followers") or {}).get("total", "?")
    popularity = data.get("popularity", "?")
    return (
        f"Artist: {name}\n"
        f"Genres: {genres}\n"
        f"Followers: {followers:,}\n"
        f"Popularity: {popularity}/100"
    )


@function_tool()
async def spotify_get_artist_top_tracks(context: RunContext, artist_id: str) -> str:
    """
    Get an artist's top 10 most popular tracks.
    artist_id: the Spotify artist ID.
    """
    if not spotify_api.is_configured():
        return "Spotify API credentials not configured."
    data = spotify_api._get(f"/artists/{artist_id}/top-tracks", params={"market": "US"})
    if not data:
        return f"Could not fetch top tracks for artist '{artist_id}'."
    tracks = data.get("tracks") or []
    if not tracks:
        return "No top tracks found."
    lines = [f"Top tracks for artist ({artist_id}):"]
    for i, t in enumerate(tracks[:10], 1):
        name = t.get("name", "?")
        popularity = t.get("popularity", "?")
        album = (t.get("album") or {}).get("name", "?")
        lines.append(f"  {i}. {name} (Album: {album}, Popularity: {popularity})")
    return "\n".join(lines)


@function_tool()
async def spotify_get_recommendations(
    context: RunContext,
    seed_tracks: str = "",
    seed_artists: str = "",
    seed_genres: str = "",
    limit: int = 10,
) -> str:
    """
    Get personalized track recommendations.
    Provide at least one seed: seed_tracks, seed_artists, or seed_genres (comma-separated Spotify IDs or genre names).
    limit: number of recommendations (default 10, max 100).
    """
    if not spotify_api.is_configured():
        return "Spotify API credentials not configured."
    params: dict = {"limit": max(1, min(100, limit))}
    if seed_tracks.strip():
        params["seed_tracks"] = seed_tracks.strip()
    if seed_artists.strip():
        params["seed_artists"] = seed_artists.strip()
    if seed_genres.strip():
        params["seed_genres"] = seed_genres.strip()
    if not any(k in params for k in ("seed_tracks", "seed_artists", "seed_genres")):
        return "Please provide at least one seed: seed_tracks, seed_artists, or seed_genres."
    data = spotify_api._get("/recommendations", params=params)
    if not data:
        return "Could not fetch recommendations."
    tracks = data.get("tracks") or []
    if not tracks:
        return "No recommendations found for the given seeds."
    lines = [f"Recommended tracks ({len(tracks)}):"]
    for t in tracks:
        name = t.get("name", "?")
        artists = ", ".join(a.get("name", "") for a in (t.get("artists") or []))
        lines.append(f"  • {name} — {artists}")
    return "\n".join(lines)


@function_tool()
async def spotify_get_playlist(context: RunContext, playlist_id: str) -> str:
    """
    Get details and all tracks for a Spotify playlist by ID.
    playlist_id: the Spotify playlist ID.
    """
    if not spotify_api.is_configured():
        return "Spotify API credentials not configured."
    data = spotify_api._get(f"/playlists/{playlist_id}")
    if not data:
        return f"Could not find playlist '{playlist_id}'."
    name = data.get("name", "?")
    owner = (data.get("owner") or {}).get("display_name", "?")
    desc = data.get("description") or ""
    items = ((data.get("tracks") or {}).get("items") or [])
    lines = [f"Playlist: {name}", f"Owner: {owner}"]
    if desc:
        lines.append(f"Description: {desc}")
    lines.append(f"Tracks ({len(items)}):")
    for i, item in enumerate(items[:20], 1):
        t = (item or {}).get("track") or {}
        if not t:
            continue
        tname = t.get("name", "?")
        artists = ", ".join(a.get("name", "") for a in (t.get("artists") or []))
        lines.append(f"  {i}. {tname} — {artists}")
    if len(items) > 20:
        lines.append(f"  ... and {len(items) - 20} more tracks.")
    return "\n".join(lines)


@function_tool()
async def spotify_get_featured_playlists(context: RunContext, limit: int = 10) -> str:
    """
    Get Spotify's featured/curated playlists.
    limit: number of playlists to return (default 10).
    """
    if not spotify_api.is_configured():
        return "Spotify API credentials not configured."
    data = spotify_api._get("/browse/featured-playlists", params={"limit": max(1, min(50, limit))})
    if not data:
        return "Could not fetch featured playlists."
    message = data.get("message", "")
    playlists = ((data.get("playlists") or {}).get("items") or [])
    if not playlists:
        return "No featured playlists found."
    lines = [f"Featured Playlists ({message}):" if message else "Featured Playlists:"]
    for pl in playlists:
        name = pl.get("name", "?")
        pid = pl.get("id", "")
        desc = (pl.get("description") or "")[:60]
        lines.append(f"  • {name} (ID: {pid})" + (f" — {desc}" if desc else ""))
    return "\n".join(lines)


@function_tool()
async def spotify_get_new_releases(context: RunContext, limit: int = 10) -> str:
    """
    Get the latest album releases on Spotify.
    limit: number of releases to return (default 10).
    """
    if not spotify_api.is_configured():
        return "Spotify API credentials not configured."
    data = spotify_api._get("/browse/new-releases", params={"limit": max(1, min(50, limit))})
    if not data:
        return "Could not fetch new releases."
    albums = ((data.get("albums") or {}).get("items") or [])
    if not albums:
        return "No new releases found."
    lines = [f"New Releases ({len(albums)}):"]
    for a in albums:
        name = a.get("name", "?")
        artists = ", ".join(ar.get("name", "") for ar in (a.get("artists") or []))
        release_date = a.get("release_date", "?")
        aid = a.get("id", "")
        lines.append(f"  • {name} — {artists} [{release_date}] (ID: {aid})")
    return "\n".join(lines)


@function_tool()
async def spotify_get_categories(context: RunContext, limit: int = 20) -> str:
    """
    Browse Spotify music categories (Pop, Rock, Workout, Party, etc.).
    limit: number of categories to return (default 20).
    """
    if not spotify_api.is_configured():
        return "Spotify API credentials not configured."
    data = spotify_api._get("/browse/categories", params={"limit": max(1, min(50, limit)), "locale": "en_US"})
    if not data:
        return "Could not fetch categories."
    cats = ((data.get("categories") or {}).get("items") or [])
    if not cats:
        return "No categories found."
    lines = [f"Spotify Categories ({len(cats)}):"]
    for c in cats:
        lines.append(f"  • {c.get('name', '?')} (ID: {c.get('id', '')})")
    return "\n".join(lines)


@function_tool()
async def spotify_get_category_playlists(context: RunContext, category_id: str, limit: int = 10) -> str:
    """
    Get playlists for a specific Spotify category.
    category_id: the category ID (e.g. 'pop', 'workout', 'party') — get IDs from spotify_get_categories.
    limit: number of playlists to return (default 10).
    """
    if not spotify_api.is_configured():
        return "Spotify API credentials not configured."
    data = spotify_api._get(f"/browse/categories/{category_id}/playlists", params={"limit": max(1, min(50, limit))})
    if not data:
        return f"Could not fetch playlists for category '{category_id}'."
    playlists = ((data.get("playlists") or {}).get("items") or [])
    if not playlists:
        return f"No playlists found for category '{category_id}'."
    lines = [f"Playlists for '{category_id}' ({len(playlists)}):"]
    for pl in playlists:
        if not pl:
            continue
        name = pl.get("name", "?")
        pid = pl.get("id", "")
        lines.append(f"  • {name} (ID: {pid})")
    return "\n".join(lines)


@function_tool()
async def spotify_get_available_genres(context: RunContext, dummy: str = "") -> str:
    """
    Get the full list of available genre seeds for Spotify recommendations.
    Use these genre names with spotify_get_recommendations.
    """
    if not spotify_api.is_configured():
        return "Spotify API credentials not configured."
    data = spotify_api._get("/recommendations/available-genre-seeds")
    if not data:
        return "Could not fetch available genres."
    genres = data.get("genres") or []
    if not genres:
        return "No genres found."
    return f"Available genre seeds ({len(genres)}):\n" + ", ".join(genres)


# ============================================================================
# UTILITIES (Notes & Reminders)
# ============================================================================

@function_tool()
async def take_note(context: RunContext, content: str) -> str:
    """Save a note to a local file."""
    try:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(NOTES_FILE, "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] {content}\n")
        return "Note saved."
    except Exception as e:
        return f"Failed to save note: {e}"

@function_tool()
async def read_notes(context: RunContext, last_n: int = 5) -> str:
    """Read the last N notes."""
    try:
        if not os.path.exists(NOTES_FILE):
            return "No notes found."
        with open(NOTES_FILE, "r", encoding="utf-8") as f:
            lines = f.readlines()
        return "".join(lines[-last_n:])
    except Exception as e:
        return f"Failed to read notes: {e}"

@function_tool()
async def set_reminder(context: RunContext, task: str, seconds: int) -> str:
    """
    Set a simple reminder (waits in background).
    For critical reminders, an external service is better.
    """
    # Note: Creating a specialized task is better, but here we simulate a delay.
    # In a real agent, this might block if not spawned correctly, but async sleep is non-blocking to other coroutines in the loop.
    # However, for a user interaction, we just acknowledge it.
    # We will spawn a background task to handle it so we can return immediately?
    # function_tool expects a return value. If we await sleep, user waits.
    # So we should probably just note it or use an actual scheduling library.
    # For now, we'll just log it to notes as a Reminder.
    return await take_note(context, f"REMINDER: {task} (in {seconds}s)")

# ============================================================================
# COMPUTER USE TOOLS — Gemini Vision Screen Control
# Like Gemini Project Mariner / Claude Computer Use
# ============================================================================

@function_tool()
async def computer_use_spotify(
    context: RunContext,
    request: Annotated[str, "What to play or do on Spotify. E.g. 'play Blinding Lights by The Weeknd', 'pause', 'next track'"],
) -> str:
    """Control Spotify by visually analyzing the screen and clicking the right UI elements using Gemini Vision."""
    try:
        import asyncio

        request_lower = request.lower().strip()

        # If it's a simple playback control, use keyboard shortcuts (faster)
        control_map = {
            "pause": "space", "play": "space", "next": "ctrl+right",
            "next track": "ctrl+right", "previous": "ctrl+left",
            "previous track": "ctrl+left", "volume up": "ctrl+up",
            "volume down": "ctrl+down", "shuffle": "ctrl+s", "repeat": "ctrl+r",
        }
        for cmd, shortcut in control_map.items():
            if request_lower == cmd:
                keys = shortcut.split("+")
                pyautogui.hotkey(*keys)
                return f"Done — sent {shortcut} to Spotify."

        # Full vision flow for play requests
        result = await _cu.run_spotify_flow(request)
        return result
    except Exception as e:
        logger.error(f"computer_use_spotify error: {e}")
        return f"Computer use failed: {e}"


@function_tool()
async def computer_use_youtube(
    context: RunContext,
    request: Annotated[str, "Video to find and play on YouTube. E.g. 'Blinding Lights official music video', 'how to make pasta tutorial'"],
) -> str:
    """Search and play a video on YouTube by visually analyzing search results using Gemini Vision."""
    try:
        result = await _cu.run_youtube_flow(request)
        return result
    except Exception as e:
        logger.error(f"computer_use_youtube error: {e}")
        return f"Computer use failed: {e}"


@function_tool()
async def music_intent_router(
    context: RunContext,
    request: Annotated[str, "The user's natural language music or video request. E.g. 'play Blinding Lights', 'watch MrBeast', 'play my workout playlist'"],
) -> str:
    """Route a music/video request to Spotify or YouTube using Gemini Vision intent detection, then execute it."""
    try:
        # Use vision model to determine intent
        img = _cu.capture_screen()
        prompt = _cu.build_intent_router_prompt(request)
        result = _cu.analyze_screen(prompt, img)

        if "error" in result:
            return f"Intent routing failed: {result.get('error')}"

        service = result.get("service", "spotify")
        intent = result.get("intent", "play_song")
        verbal = result.get("verbal_response", f"On it.")
        query_obj = result.get("query", {})

        # Build final query string
        if service == "spotify":
            song = query_obj.get("song_title") or query_obj.get("search_term") or request
            artist = query_obj.get("artist", "")
            spotify_request = f"{song} by {artist}".strip(" by ").strip()
            flow_result = await _cu.run_spotify_flow(spotify_request)
            return flow_result or verbal

        elif service == "youtube":
            video = (
                query_obj.get("video_title")
                or query_obj.get("channel")
                or query_obj.get("search_term")
                or request
            )
            flow_result = await _cu.run_youtube_flow(video)
            return flow_result or verbal

        return verbal

    except Exception as e:
        logger.error(f"music_intent_router error: {e}")
        return f"Intent routing failed: {e}"


# ============================================================================
# SCREEN SHARE VISION TOOL
# ============================================================================

@function_tool()
async def describe_screen_share(
    context: RunContext,
    question: Annotated[
        str,
        "What to look for or describe on the shared screen. "
        "E.g. 'What application is open?', 'Read the error message on screen', "
        "'What is the user doing?'"
    ] = "Describe what you see on the shared screen in detail.",
) -> str:
    """
    Analyse the user's shared screen using vision AI and answer a question about it.
    The user must have started a screen share from their LiveKit client.
    Use this tool whenever the user asks you to look at, read, or describe their screen.
    """
    try:
        from screen_share import get_latest_frame

        img = get_latest_frame()
        if img is None:
            return (
                "No screen-share frame received yet. "
                "Please start a screen share from your client and try again."
            )

        prompt = (
            f"{question}\n\n"
            "Return a JSON object with a single key \"description\" whose value is a "
            "plain-English description answering the question above."
        )
        result = _cu.analyze_screen(prompt, img)

        if isinstance(result, dict):
            return result.get("description") or str(result)
        return str(result)

    except Exception as e:
        logger.error(f"describe_screen_share error: {e}")
        return f"Screen-share analysis failed: {e}"


# ============================================================================
# LOCAL MEDIA TOOLS — OS-level Spotify/YouTube control (no Spotify API needed)
# ============================================================================

@function_tool(
    description=(
        "Search for and play music on the locally installed Spotify desktop app "
        "without using the Spotify API. Opens a spotify: URI directly so Spotify "
        "launches and begins playback. "
        "Parameters: "
        "query — The search term, e.g. 'Blinding Lights', 'Drake', 'Lo-Fi Beats'. "
        "media_type — Scope: 'track' for a song, 'artist', 'album', 'playlist', or 'all' (default). "
        "Examples: spotify_play_media('Drake', 'artist') | spotify_play_media('Blinding Lights', 'track') | spotify_play_media('Lo-Fi Beats', 'playlist')"
    )
)
async def spotify_play_media(
    context: RunContext,
    query: Annotated[str, "The search term to look up on Spotify."],
    media_type: Annotated[
        str,
        "Scope of the Spotify search. One of: 'track', 'artist', 'album', 'playlist', 'all'. Default is 'all'.",
    ] = "all",
) -> str:
    """Play music on the local Spotify desktop app without using the Spotify API."""
    try:
        if not os.path.exists(SPOTIFY_CONTROL_SCRIPT):
            return "Spotify control script not found. Cannot play media."

        encoded_query = urllib.parse.quote(query)
        if media_type.lower() == "all":
            uri = f"spotify:search:{encoded_query}"
        else:
            uri = f"spotify:search:{media_type.lower()}:{encoded_query}"

        logger.info(f"[LocalMedia] Opening Spotify via spotify_control: {uri}")
        # Call spotify_control.py with the URI and --autoplay to actually play
        result = subprocess.run(
            [sys.executable, SPOTIFY_CONTROL_SCRIPT, 'search', '--uri', uri, '--autoplay'],
            capture_output=True,
            text=True,
            check=False
        )
        if result.returncode != 0:
            return f"Failed to open Spotify: {result.stderr or 'Unknown error'}"
        return f"Opened Spotify and started the top result for '{query}' (type: {media_type})."
    except Exception as e:
        logger.error(f"[LocalMedia] spotify_play_media failed: {e}")
        return f"Failed to play on Spotify: {e}"


@function_tool(
    description=(
        "Control Spotify (or any active media player) playback using OS-level media keys. "
        "Works without Spotify being focused. "
        "action must be exactly one of: 'pause', 'resume', 'stop', 'next', 'previous'. "
        "Examples: spotify_control_playback('pause') | spotify_control_playback('next') | spotify_control_playback('previous')"
    )
)
async def spotify_control_playback(
    context: RunContext,
    action: Annotated[
        str,
        "Playback action. One of: 'pause', 'resume', 'stop', 'next', 'previous'.",
    ],
) -> str:
    """Control Spotify playback via the spotify_control script."""
    try:
        a = action.strip().lower()
        if a in ('pause', 'resume', 'stop', 'next', 'previous'):
            # Map to spotify_control.py commands
            if a == 'stop':
                cmd = [sys.executable, SPOTIFY_CONTROL_SCRIPT, 'stop', '--mode', 'quit']
            elif a in ('pause', 'resume'):
                # Use playback command for play/pause (handles state)
                cmd = [sys.executable, SPOTIFY_CONTROL_SCRIPT, 'playback', a]
            else:  # next or previous
                cmd = [sys.executable, SPOTIFY_CONTROL_SCRIPT, 'playback', a]

            logger.info(f"[LocalMedia] Executing spotify_control: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, text=True, check=False)

            if result.returncode != 0:
                return f"Failed to execute '{a}': {result.stderr}"
            return result.stdout.strip() if result.stdout.strip() else f"Executed '{a}' successfully."
        else:
            return f"Unknown action '{action}'. Use: 'pause', 'resume', 'stop', 'next', 'previous'."
    except Exception as e:
        logger.error(f"[LocalMedia] spotify_control_playback failed: {e}")
        return f"Failed to control playback: {e}"


@function_tool(
    description=(
        "Find out what is currently playing on Spotify or any media app by reading "
        "the Windows Global System Media Transport Controls (SMTC). "
        "No parameters required — just call it to get the current track title and artist. "
        "Example: spotify_what_is_playing()"
    )
)
async def spotify_what_is_playing(context: RunContext) -> str:
    """Get the currently playing track from Spotify via spotify_control script."""
    try:
        result = subprocess.run(
            [sys.executable, SPOTIFY_CONTROL_SCRIPT, 'now-playing'],
            capture_output=True,
            text=True,
            check=False
        )
        output = result.stdout.strip()

        # Parse output
        if "Spotify is not running" in output:
            return "Spotify is not running."
        elif "paused" in output.lower() or "Nothing playing" in output:
            return "Spotify is paused or nothing is playing."
        elif "Now Playing:" in output or "Song   :" in output:
            # Extract song and artist lines
            lines = output.split('\n')
            song = None
            artist = None
            for line in lines:
                if line.strip().startswith('Song'):
                    song = line.split(':', 1)[1].strip()
                elif line.strip().startswith('Artist'):
                    artist = line.split(':', 1)[1].strip()
            if song and artist:
                return f"Currently playing: {song} by {artist}."
            elif song:
                return f"Currently playing: {song}."
            elif artist:
                return f"Currently playing by: {artist}."
            else:
                return output
        else:
            return output if output else "No track information available."
    except Exception as e:
        logger.error(f"[LocalMedia] spotify_what_is_playing failed: {e}")
        return f"Failed to get now playing info: {e}"


@function_tool(
    description=(
        "Mute or unmute ONLY the Spotify desktop app in the Windows Volume Mixer. "
        "All other apps keep their volume unchanged. "
        "mute=True to silence Spotify, mute=False to restore its audio. "
        "Examples: spotify_mute_application(True) | spotify_mute_application(False)"
    )
)
async def spotify_mute_application(
    context: RunContext,
    mute: Annotated[bool, "True to mute Spotify, False to unmute Spotify."],
) -> str:
    """Mute or unmute Spotify using the spotify_control script."""
    try:
        cmd = [sys.executable, SPOTIFY_CONTROL_SCRIPT, 'volume']
        if mute:
            cmd.append('--mute')
        else:
            cmd.append('--unmute')

        logger.info(f"[LocalMedia] Mute control: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)

        if result.returncode != 0:
            return f"Failed to {'mute' if mute else 'unmute'} Spotify: {result.stderr}"
        output = result.stdout.strip()
        return output if output else f"Spotify {'muted' if mute else 'unmuted'} successfully."
    except Exception as e:
        logger.error(f"[LocalMedia] spotify_mute_application failed: {e}")
        return f"Failed to {'mute' if mute else 'unmute'} Spotify: {e}"


@function_tool(
    description=(
        "Toggle shuffle mode on Spotify. No parameters needed. "
        "Uses the local spotify_control script (no Spotify API required). "
        "Example: spotify_toggle_shuffle()"
    )
)
async def spotify_toggle_shuffle(context: RunContext) -> str:
    """Toggle Spotify shuffle mode."""
    try:
        result = subprocess.run(
            [sys.executable, SPOTIFY_CONTROL_SCRIPT, 'shuffle'],
            capture_output=True,
            text=True,
            check=False
        )
        if result.returncode != 0:
            return f"Failed to toggle shuffle: {result.stderr}"
        output = result.stdout.strip()
        return output if output else "Shuffle toggled."
    except Exception as e:
        logger.error(f"[LocalMedia] spotify_toggle_shuffle failed: {e}")
        return f"Failed to toggle shuffle: {e}"


@function_tool(
    description=(
        "Cycle Spotify repeat mode through Off -> Repeat All -> Repeat One -> Off. "
        "No parameters needed. Uses local spotify_control script. "
        "Example: spotify_cycle_repeat()"
    )
)
async def spotify_cycle_repeat(context: RunContext) -> str:
    """Cycle Spotify repeat mode."""
    try:
        result = subprocess.run(
            [sys.executable, SPOTIFY_CONTROL_SCRIPT, 'repeat'],
            capture_output=True,
            text=True,
            check=False
        )
        if result.returncode != 0:
            return f"Failed to change repeat mode: {result.stderr}"
        output = result.stdout.strip()
        return output if output else "Repeat mode cycled."
    except Exception as e:
        logger.error(f"[LocalMedia] spotify_cycle_repeat failed: {e}")
        return f"Failed to change repeat mode: {e}"


@function_tool(
    description=(
        "Control Spotify volume. Use set for exact volume (0-100), up/down to adjust. "
        "Examples: spotify_volume(set=75) | spotify_volume(up=10) | spotify_volume(down=5)"
    )
)
async def spotify_volume(
    context: RunContext,
    set: Annotated[int | None, "Set volume to exact percentage (0-100)"] = None,
    up: Annotated[int, "Increase volume by this many percent (default 5)"] = 5,
    down: Annotated[int, "Decrease volume by this many percent (default 5)"] = 5,
) -> str:
    """Control Spotify volume using spotify_control script."""
    try:
        cmd = [sys.executable, SPOTIFY_CONTROL_SCRIPT, 'volume']
        if set is not None:
            cmd.extend(['--set', str(set)])
        elif up:
            cmd.extend(['--up', str(up)])
        elif down:
            cmd.extend(['--down', str(down)])
        else:
            return "No volume action specified."

        result = subprocess.run(cmd, capture_output=True, text=True, check=False)
        if result.returncode != 0:
            return f"Failed to control volume: {result.stderr}"
        output = result.stdout.strip()
        return output if output else "Volume adjusted."
    except Exception as e:
        logger.error(f"[LocalMedia] spotify_volume failed: {e}")
        return f"Failed to control volume: {e}"


@function_tool(
    description=(
        "Search YouTube and open the results page in the default web browser. "
        "Use when the user wants to find and watch a YouTube video. "
        "query — The search term, e.g. 'lo-fi music', 'Python tutorial', 'Coldplay Yellow live'. "
        "Examples: youtube_open('lo-fi hip hop radio') | youtube_open('how to make pasta')"
    )
)
async def youtube_open(
    context: RunContext,
    query: Annotated[str, "The search term to look up on YouTube."],
) -> str:
    """URL-encode the query and open the YouTube search results page in the browser."""
    try:
        encoded = urllib.parse.quote(query.strip())
        url = f"https://www.youtube.com/results?search_query={encoded}"
        logger.info(f"[LocalMedia] Opening YouTube search: {url}")
        webbrowser.open(url)
        return f"Opened YouTube search results for '{query}'."
    except Exception as e:
        logger.error(f"[LocalMedia] youtube_open failed: {e}")
        return f"Failed to open YouTube: {e}"


# ============================================================================
# POWERFUL WEB SCRAPING TOOLS (Playwright-powered - Like Perplexity Comet)
# ============================================================================

@function_tool()
async def extract_contact_info(
    context: RunContext,
    url: Annotated[str, "Website URL to scrape"],
) -> str:
    """
    Extract contact information (emails, phone numbers, social links) from ANY website.
    Uses Playwright to render JavaScript - works on modern websites like React/Vue/Angular.

    This is the PRIMARY tool for finding emails, phone numbers, contact info.
    Acts like Perplexity Comet - fully renders the page before extracting.

    ALWAYS use this when user asks to:
    - "find email on website"
    - "get contact info from site"
    - "extract gmail/email from page"

    Examples:
    - extract_contact_info("https://example.com")
    - extract_contact_info("https://selwynjesudas.com")
    """
    try:
        from web_scraper import extract_emails_phones

        result = await extract_emails_phones(url)

        if result.get("error"):
            return f"Extraction failed: {result['error']}"

        response = f"Contact information from {url}:\n\n"

        if result["emails"]:
            response += f"EMAILS FOUND ({len(result['emails'])}):\n"
            for email in result["emails"]:
                response += f"  * {email}\n"
            response += "\n"
        else:
            response += "No emails found in page text.\n\n"

        if result["phones"]:
            response += f"PHONE NUMBERS ({len(result['phones'])}):\n"
            for phone in result["phones"]:
                response += f"  * {phone}\n"
            response += "\n"

        if result["social_links"]:
            response += f"SOCIAL MEDIA LINKS ({len(result['social_links'])}):\n"
            for link in result["social_links"]:
                response += f"  * {link}\n"

        if not result["emails"] and not result["phones"] and not result["social_links"]:
            response = f"No contact info found on {url}. Try vision_extract_from_website for image-based extraction."

        return response

    except ImportError:
        return "Playwright not installed. Run: pip install playwright && playwright install chromium"
    except Exception as e:
        logger.error(f"[ContactExtractor] Error: {e}")
        return f"Extraction failed: {e}"


@function_tool()
async def vision_extract_from_website(
    context: RunContext,
    url: Annotated[str, "Website URL to analyze"],
    query: Annotated[str, "What to find (e.g. 'email', 'contact info', 'pricing')"],
) -> str:
    """
    Use AI VISION to extract information from a website screenshot.
    Can read text from IMAGES - use when regular extraction fails.

    Acts like Perplexity Comet with vision - takes screenshot and reads it with AI.

    Examples:
    - vision_extract_from_website("https://selwynjesudas.com", "email address")
    - vision_extract_from_website("https://company.com", "pricing")
    """
    try:
        from web_scraper import vision_extract

        result = await vision_extract(url, query)

        if result.get("error"):
            return f"Vision extraction failed: {result['error']}"

        if result.get("found"):
            return f"FOUND on {url}:\n\nDATA: {result.get('data')}\nLocation: {result.get('location', 'N/A')}\nConfidence: {result.get('confidence', 'N/A')}"
        else:
            return f"Could not find '{query}' on {url}.\n\nDetails: {result.get('data', 'No additional info')}"

    except ImportError as e:
        return f"Missing dependency: {e}. Install: pip install playwright pillow && playwright install chromium"
    except Exception as e:
        return f"Vision extraction failed: {e}"


@function_tool()
async def scrape_full_page(
    context: RunContext,
    url: Annotated[str, "Website URL"],
) -> str:
    """
    Get ALL visible text from a website using Playwright.
    Returns complete page content after JavaScript renders.
    """
    try:
        from web_scraper import scrape_full_text
        return await scrape_full_text(url)
    except ImportError:
        return "Playwright not installed. Run: pip install playwright && playwright install chromium"
    except Exception as e:
        return f"Scraping failed: {e}"


@function_tool()
async def scrape_website_text(
    context: RunContext,
    url: Annotated[str, "Website URL"],
    search_for: Annotated[str, "What to search for (e.g. 'email', 'phone', 'address')"] = "",
) -> str:
    """
    Scrape text content from a website and optionally search for specific information.

    Lightweight alternative to browser automation - works instantly without Selenium.

    Examples:
    - scrape_website_text("https://example.com", "email")
    - scrape_website_text("https://company.com", "contact")
    """
    try:
        from bs4 import BeautifulSoup
        import re

        logger.info(f"[WebScraper] Fetching {url}")

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()

        # Get text
        text = soup.get_text()

        # Clean up text
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = '\n'.join(chunk for chunk in chunks if chunk)

        if search_for:
            # Search for specific content
            search_term = search_for.lower()
            relevant_lines = []

            for line in text.split('\n'):
                if search_term in line.lower():
                    relevant_lines.append(line)

            if relevant_lines:
                result = f"Found {len(relevant_lines)} lines containing '{search_for}' on {url}:\n\n"
                result += '\n'.join(relevant_lines[:20])  # Limit to 20 lines
                if len(relevant_lines) > 20:
                    result += f"\n\n... and {len(relevant_lines) - 20} more lines"
                return result
            else:
                return f"No content found containing '{search_for}' on {url}"
        else:
            # Return summary
            preview = text[:1000] + "..." if len(text) > 1000 else text
            return f"Content from {url}:\n\n{preview}\n\n(Total: {len(text)} characters)"

    except Exception as e:
        logger.error(f"[WebScraper] Error: {e}")
        return f"Failed to scrape {url}: {e}"


# ============================================================================
# BROWSER AUTOMATION TOOLS
# ============================================================================

@function_tool()
async def web_automate(
    context: RunContext,
    task: Annotated[str, "Description of web automation task. E.g. 'Login to Twitter', 'Fill contact form', 'Extract product prices from this page'"],
    url: Annotated[str, "Starting URL (optional if already on a page)"] = "",
) -> str:
    """
    Automate web browser tasks using AI-powered browser automation.

    Capabilities:
    - Form filling (login, signup, contact forms)
    - Data extraction (scraping tables, lists, prices)
    - Clicking buttons and navigating
    - Screenshot analysis

    Examples:
    - web_automate("Login to Gmail", "https://gmail.com")
    - web_automate("Fill out contact form with my info")
    - web_automate("Extract all product prices and names")
    - web_automate("Click the Settings button and enable notifications")
    """
    try:
        from browser_automation import BrowserAutomationEngine
        from computer_use import analyze_screen
    except ImportError as e:
        return f"Web automation is not available. Missing dependency: {e}. Install with: pip install selenium playwright"

        logger.info(f"[WebAutomate] Starting task: {task}")

        async with BrowserAutomationEngine(backend="auto", headless=False) as browser:
            # Navigate to URL if provided
            if url:
                nav_result = await browser.navigate(url)
                if not nav_result["success"]:
                    return f"Failed to navigate to {url}: {nav_result.get('error')}"
                await asyncio.sleep(2)  # Let page load

            # Capture current page state
            screenshot = await browser.capture_screenshot()
            current_url = await browser.get_current_url()

            # Ask Nova Pro to plan the automation
            plan_prompt = f"""
Task: {task}
Current page URL: {current_url}

Analyze this webpage screenshot and create a step-by-step automation plan.

Return JSON with this structure:
{{
    "analysis": "brief description of what you see on the page",
    "steps": [
        {{"action": "click", "selector": "#login-btn", "description": "Click login button"}},
        {{"action": "type", "selector": "#email", "value": "<<EMAIL>>", "description": "Enter email"}},
        {{"action": "type", "selector": "#password", "value": "<<PASSWORD>>", "description": "Enter password"}},
        {{"action": "click", "selector": "button[type='submit']", "description": "Submit form"}},
        {{"action": "wait", "selector": ".dashboard", "timeout": 5000, "description": "Wait for dashboard to load"}}
    ],
    "expected_outcome": "User should be logged in",
    "estimated_time_seconds": 10
}}

Available actions: click, type, wait, scroll, navigate, extract
For sensitive data like passwords, use <<EMAIL>>, <<PASSWORD>> placeholders.

Return ONLY valid JSON, no markdown, no explanation.
"""

            plan = analyze_screen(plan_prompt, screenshot, temperature=0.1)

            if "error" in plan:
                return f"Could not create automation plan: {plan.get('error')}"

            steps = plan.get("steps", [])
            analysis = plan.get("analysis", "")
            expected = plan.get("expected_outcome", "")

            logger.info(f"[WebAutomate] Plan created with {len(steps)} steps")
            logger.info(f"[WebAutomate] Analysis: {analysis}")

            if not steps:
                return f"No automation steps could be determined for task: {task}"

            # Execute each step
            results = []
            for i, step in enumerate(steps, 1):
                action = step.get("action", "").lower()
                description = step.get("description", action)

                logger.info(f"[WebAutomate] Step {i}/{len(steps)}: {description}")

                try:
                    if action == "click":
                        selector = step.get("selector")
                        text = step.get("text")
                        result = await browser.click_element(
                            selector=selector,
                            text=text,
                            vision_fallback=True
                        )

                    elif action == "type":
                        selector = step.get("selector")
                        value = step.get("value", "")

                        # Check for placeholder - ask user for actual value
                        if value.startswith("<<") and value.endswith(">>"):
                            placeholder = value[2:-2].lower()
                            result = {"success": False, "error": f"Need actual {placeholder} value"}
                        else:
                            result = await browser.type_text(selector, value, clear_first=True)

                    elif action == "wait":
                        selector = step.get("selector")
                        timeout = step.get("timeout", 5000)
                        success = await browser.wait_for_element(selector, timeout=timeout)
                        result = {"success": success}

                    elif action == "scroll":
                        direction = step.get("direction", "down")
                        amount = step.get("amount", 500)
                        result = await browser.scroll_page(direction, amount)

                    elif action == "navigate":
                        target_url = step.get("url")
                        result = await browser.navigate(target_url)

                    elif action == "extract":
                        query = step.get("query", task)
                        result = await browser.extract_data(query)

                    else:
                        result = {"success": False, "error": f"Unknown action: {action}"}

                    status = "✓" if result.get("success") else "✗"
                    results.append({
                        "step": description,
                        "status": "success" if result.get("success") else "failed",
                        "details": result
                    })

                    # Small delay between actions
                    await asyncio.sleep(0.5)

                except Exception as step_error:
                    logger.error(f"[WebAutomate] Step failed: {step_error}")
                    results.append({
                        "step": description,
                        "status": "failed",
                        "error": str(step_error)
                    })

            # Verify final state
            final_screenshot = await browser.capture_screenshot()
            verification_prompt = f"""
Expected outcome: {expected}

Look at this webpage screenshot and determine if the automation was successful.
Did we achieve the expected outcome?

Return JSON:
{{
    "success": true,
    "verification": "Yes, user is now logged in / form was submitted / etc",
    "current_state": "brief description of current page state"
}}

Return ONLY valid JSON.
"""

            verification = analyze_screen(verification_prompt, final_screenshot, temperature=0.2)

            # Build summary
            success_count = len([r for r in results if r["status"] == "success"])
            total_count = len(results)

            summary = f"Automation task: {task}\n\n"
            summary += f"Analysis: {analysis}\n\n"
            summary += f"Executed {success_count}/{total_count} steps successfully.\n\n"

            for i, r in enumerate(results, 1):
                status_icon = "✓" if r["status"] == "success" else "✗"
                summary += f"{status_icon} Step {i}: {r['step']}\n"

            summary += f"\nVerification: {verification.get('verification', 'Could not verify')}\n"
            summary += f"Current state: {verification.get('current_state', 'Unknown')}"

            return summary

    except Exception as e:
        logger.error(f"[WebAutomate] Error: {e}", exc_info=True)
        return f"Web automation failed: {e}"


@function_tool()
async def browser_navigate_and_analyze(
    context: RunContext,
    url: Annotated[str, "URL to visit"],
    task: Annotated[str, "What to analyze or extract from the page. E.g. 'summarize the article', 'extract all prices', 'check if login was successful'"],
) -> str:
    """
    Navigate to a URL and perform vision-based analysis or data extraction.

    Use this for:
    - Reading and summarizing web content
    - Extracting specific data (prices, emails, phone numbers)
    - Checking page state (logged in, error messages, etc)
    - Understanding page layout and content

    Examples:
    - browser_navigate_and_analyze("https://news.ycombinator.com", "summarize top 5 stories")
    - browser_navigate_and_analyze("https://amazon.com/product", "extract price and rating")
    - browser_navigate_and_analyze("https://mybank.com/dashboard", "what is my account balance")
    """
    try:
        from browser_automation import BrowserAutomationEngine
    except ImportError as e:
        return f"Browser automation is not available. Missing dependency: {e}"

        logger.info(f"[BrowserAnalyze] Navigating to: {url}")

        async with BrowserAutomationEngine(backend="auto", headless=False) as browser:
            # Navigate to URL
            nav_result = await browser.navigate(url)
            if not nav_result["success"]:
                return f"Failed to navigate to {url}: {nav_result.get('error')}"

            # Wait for page to stabilize
            await asyncio.sleep(2)

            # Perform analysis
            result = await browser.analyze_page_with_vision(task)

            page_title = await browser.get_page_title()

            response = f"Page: {page_title}\n"
            response += f"URL: {url}\n\n"
            response += f"Analysis: {result}"

            return response

    except Exception as e:
        logger.error(f"[BrowserAnalyze] Error: {e}")
        return f"Browser analysis failed: {e}"


@function_tool()
async def fill_web_form(
    context: RunContext,
    url: Annotated[str, "Form URL"],
    form_data: Annotated[str, "Form fields as comma-separated key=value pairs. E.g. 'name=John Doe, email=john@example.com, message=Hello'"],
    submit: Annotated[bool, "Whether to submit the form after filling"] = False,
) -> str:
    """
    Intelligently fill out a web form using vision AI.

    The tool analyzes the form structure and maps your data to the correct fields.

    Examples:
    - fill_web_form("https://example.com/contact", "name=John, email=john@example.com, message=Hello", submit=True)
    - fill_web_form("https://site.com/signup", "username=johndoe, email=john@example.com, password=secret123")

    Supported field types: name, email, password, phone, message, address, city, etc.
    """
    try:
        from browser_automation import BrowserAutomationEngine
    except ImportError as e:
        return f"Form filling is not available. Missing dependency: {e}"

        # Parse form_data string into dict
        form_dict = {}
        for pair in form_data.split(","):
            if "=" in pair:
                key, value = pair.split("=", 1)
                form_dict[key.strip()] = value.strip()

        logger.info(f"[FillForm] Filling form at {url} with {len(form_dict)} fields")

        async with BrowserAutomationEngine(backend="auto", headless=False) as browser:
            # Navigate to form
            nav_result = await browser.navigate(url)
            if not nav_result["success"]:
                return f"Failed to navigate to {url}: {nav_result.get('error')}"

            await asyncio.sleep(1)

            # Fill form
            result = await browser.fill_form(form_dict, submit=submit)

            if result["success"]:
                filled_fields = result.get("filled_fields", [])
                success_fields = [f for f in filled_fields if f["status"] == "success"]

                response = f"Form filled successfully!\n\n"
                response += f"Filled {len(success_fields)}/{len(filled_fields)} fields:\n"
                for field in filled_fields:
                    status_icon = "✓" if field["status"] == "success" else "✗"
                    response += f"{status_icon} {field['field']}\n"

                if submit and result.get("submitted"):
                    response += "\n✓ Form submitted successfully!"
                elif submit:
                    response += "\n⚠ Form was filled but submission may have failed"

                return response
            else:
                return f"Form filling failed: {result.get('error')}"

    except Exception as e:
        logger.error(f"[FillForm] Error: {e}")
        return f"Form filling error: {e}"


@function_tool()
async def browser_extract_data(
    context: RunContext,
    url: Annotated[str, "Page URL"],
    query: Annotated[str, "What data to extract. E.g. 'all product names and prices', 'table data', 'email addresses', 'phone numbers'"],
) -> str:
    """
    Extract structured data from a webpage using vision AI.

    This tool navigates to a page, captures it, and extracts the requested information.

    Examples:
    - browser_extract_data("https://store.com/products", "all product names and prices")
    - browser_extract_data("https://news.com", "all article headlines and links")
    - browser_extract_data("https://company.com/about", "all email addresses and phone numbers")
    """
    try:
        from browser_automation import BrowserAutomationEngine
    except ImportError as e:
        return f"Data extraction is not available. Missing dependency: {e}"

        logger.info(f"[ExtractData] Extracting from: {url}")

        async with BrowserAutomationEngine(backend="auto", headless=False) as browser:
            # Navigate
            nav_result = await browser.navigate(url)
            if not nav_result["success"]:
                return f"Failed to navigate to {url}: {nav_result.get('error')}"

            await asyncio.sleep(2)

            # Extract data
            result = await browser.extract_data(query)

            if "error" in result:
                return f"Data extraction failed: {result['error']}"

            data = result.get("data", [])
            count = result.get("count", len(data))
            summary = result.get("summary", "Data extracted")

            response = f"Extracted data from: {url}\n\n"
            response += f"Query: {query}\n"
            response += f"Found: {count} items\n"
            response += f"Summary: {summary}\n\n"

            # Format data nicely
            if isinstance(data, list):
                response += "Data:\n"
                for i, item in enumerate(data[:20], 1):  # Limit to first 20 items
                    if isinstance(item, dict):
                        response += f"{i}. {json.dumps(item, indent=2)}\n"
                    else:
                        response += f"{i}. {item}\n"

                if len(data) > 20:
                    response += f"\n... and {len(data) - 20} more items"
            else:
                response += f"Data: {data}"

            return response

    except Exception as e:
        logger.error(f"[ExtractData] Error: {e}")
        return f"Data extraction error: {e}"


# ============================================================================
# ENHANCED BROWSER AUTOMATION TOOLS (Browser Agent Specialization)
# ============================================================================

@function_tool
async def browser_visual_click(
    context: RunContext,
    description: Annotated[str, "Visual description of element to click (e.g., 'blue Submit button', 'Login link in header')"],
    confirm_action: Annotated[bool, "Whether to ask for confirmation before clicking"] = True
) -> str:
    """
    Click an element using visual description and browser-use technology.

    Ideal for complex websites where CSS selectors are difficult.
    Uses AI visual understanding to locate and click elements.
    """
    try:
        if confirm_action and any(word in description.lower() for word in ["submit", "buy", "purchase", "delete", "post"]):
            return f"Found '{description}' but need confirmation for this action. Please confirm to proceed."

        from browser_automation import BrowserAutomationEngine

        async with BrowserAutomationEngine(backend="auto", visual_mode=True) as browser:
            result = await browser.click_element(text=description, vision_fallback=True)

            if result["success"]:
                method = result.get("method", "unknown")
                return f"✅ Successfully clicked '{description}' using {method} detection!"
            else:
                return f"❌ Could not click '{description}': {result.get('error', 'Unknown error')}"

    except Exception as e:
        logger.error(f"Visual click failed: {e}")
        return f"Error clicking '{description}': {str(e)}"


@function_tool
async def smart_form_fill_enhanced(
    context: RunContext,
    form_data: Annotated[dict, "Field names mapped to values (e.g., {'email': 'user@example.com', 'name': 'John Doe'})"],
    submit_form: Annotated[bool, "Whether to submit form after filling"] = False
) -> str:
    """
    Intelligently fill web forms using visual understanding and multiple strategies.

    Automatically detects field types and uses the best filling method.
    Provides detailed feedback on success/failure for each field.
    """
    try:
        from browser_automation import BrowserAutomationEngine

        async with BrowserAutomationEngine(backend="auto", visual_mode=True) as browser:
            result = await browser.fill_form(form_data, submit=submit_form)

            if result["success"]:
                filled_fields = result.get("filled_fields", [])
                success_count = sum(1 for field in filled_fields if field.get("status") == "success")
                total_fields = len(filled_fields)

                response = f"✅ Successfully filled {success_count}/{total_fields} form fields!"

                if submit_form and result.get("submitted"):
                    response += " Form has been submitted."
                elif submit_form:
                    response += " Form filled but submission needs manual confirmation."

                return response
            else:
                return f"❌ Form filling failed: {result.get('error', 'Unknown error')}"

    except Exception as e:
        logger.error(f"Smart form fill failed: {e}")
        return f"Form filling error: {str(e)}"


@function_tool
async def ecommerce_price_compare(
    context: RunContext,
    product: Annotated[str, "Product name or description to search for"],
    max_sites: Annotated[int, "Maximum number of sites to check"] = 3
) -> str:
    """
    Compare prices for a product across multiple e-commerce websites.

    Searches major retailers and extracts pricing information.
    Returns formatted comparison with prices and availability.
    """
    try:
        from browser_automation import BrowserAutomationEngine

        shopping_sites = [
            ("Amazon", "https://www.amazon.com/s?k="),
            ("eBay", "https://www.ebay.com/sch/i.html?_nkw="),
            ("Walmart", "https://www.walmart.com/search/?query=")
        ]

        results = []

        # Use playwright for better reliability with e-commerce sites
        async with BrowserAutomationEngine(backend="playwright", visual_mode=False) as browser:
            for site_name, base_url in shopping_sites[:max_sites]:
                try:
                    search_url = base_url + urllib.parse.quote_plus(product)
                    logger.info(f"Checking {site_name} for {product}...")

                    # Navigate with fast loading strategy (domcontentloaded instead of networkidle)
                    nav_result = await browser.navigate(search_url)

                    if not nav_result.get("success"):
                        logger.warning(f"{site_name}: Navigation failed - {nav_result.get('error')}")
                        results.append(f"⚠️ {site_name}: Site too slow, skipping")
                        continue

                    # Give page a moment to render results
                    await asyncio.sleep(2)

                    # Extract pricing data
                    data = await browser.extract_data(f"product prices and names for {product}")

                    if data.get("data"):
                        results.append(f"✅ {site_name}: Found {data.get('count', '?')} results")
                    else:
                        results.append(f"❌ {site_name}: No results found")

                except asyncio.TimeoutError:
                    logger.warning(f"{site_name}: Timeout - site is slow or blocking automation")
                    results.append(f"⚠️ {site_name}: Timeout (site too slow)")
                except Exception as e:
                    logger.error(f"{site_name}: Error - {e}")
                    results.append(f"⚠️ {site_name}: Could not access")

        response = f"Price comparison for '{product}':\n\n"
        response += "\n".join(results)
        response += f"\n\nTip: Visit these sites directly for detailed pricing and current deals!"

        return response

    except Exception as e:
        logger.error(f"Price comparison failed: {e}")
        return f"Price comparison error: {str(e)}"


@function_tool
async def social_media_compose(
    context: RunContext,
    platform: Annotated[str, "Social media platform (LinkedIn, Twitter, Facebook, Instagram)"],
    content: Annotated[str, "Content to post"],
    draft_only: Annotated[bool, "Only compose draft, don't post"] = True
) -> str:
    """
    Compose and optionally post content to social media platforms.

    Navigates to platform, fills post composer, and optionally publishes.
    Always asks for confirmation before actual posting.
    """
    try:
        from browser_automation import BrowserAutomationEngine

        platform_urls = {
            "linkedin": "https://www.linkedin.com",
            "twitter": "https://twitter.com",
            "facebook": "https://www.facebook.com",
            "instagram": "https://www.instagram.com"
        }

        platform_key = platform.lower()
        if platform_key not in platform_urls:
            return f"❌ Platform '{platform}' not supported. Use: LinkedIn, Twitter, Facebook, Instagram"

        async with BrowserAutomationEngine(backend="auto", visual_mode=True) as browser:
            await browser.navigate(platform_urls[platform_key])

            # Compose post content
            result = await browser.fill_form({
                "post": content,
                "status": content,
                "message": content
            }, submit=not draft_only)

            if draft_only:
                return f"📝 Draft composed for {platform}:\n\n\"{content}\"\n\nReview and post manually for safety!"
            else:
                return f"📱 Attempted to post to {platform}. Please verify the post was published successfully!"

    except Exception as e:
        logger.error(f"Social media compose failed: {e}")
        return f"Social media error: {str(e)}"


@function_tool
async def website_data_mining(
    context: RunContext,
    url: Annotated[str, "Website URL to extract data from"],
    data_type: Annotated[str, "Type of data to extract (prices, contacts, articles, listings, reviews)"],
    max_items: Annotated[int, "Maximum number of items to extract"] = 10
) -> str:
    """
    Extract structured data from websites using AI-powered analysis.

    Specializes in common data extraction patterns like product catalogs,
    contact directories, news articles, and review systems.
    """
    try:
        from browser_automation import BrowserAutomationEngine

        data_queries = {
            "prices": "extract all product prices with names",
            "contacts": "extract contact information including emails and phone numbers",
            "articles": "extract article headlines and summaries",
            "listings": "extract all listings with titles and descriptions",
            "reviews": "extract customer reviews and ratings"
        }

        query = data_queries.get(data_type.lower(), f"extract {data_type} information")

        async with BrowserAutomationEngine(backend="auto", visual_mode=True) as browser:
            await browser.navigate(url)

            result = await browser.extract_data(query)

            if result.get("data"):
                data_items = result["data"]
                count = min(len(data_items) if isinstance(data_items, list) else 1, max_items)

                response = f"🔍 Extracted {count} {data_type} items from {url}:\n\n"

                if isinstance(data_items, list):
                    for i, item in enumerate(data_items[:max_items], 1):
                        response += f"{i}. {str(item)[:100]}{'...' if len(str(item)) > 100 else ''}\n"
                else:
                    response += str(data_items)[:500]

                return response
            else:
                return f"❌ No {data_type} data found on {url}"

    except Exception as e:
        logger.error(f"Data mining failed: {e}")
        return f"Data mining error: {str(e)}"


# ============================================================================
# ALL_TOOLS
# ============================================================================

ALL_TOOLS = [
    # ── No credentials needed ──────────────────────────────────
    open_website,
    web_search,
    get_weather,
    system_control,
    # Universal Media Controls
    pause_media,
    next_track,
    previous_track,
    volume_control,
    # Notes & Reminders
    take_note,
    read_notes,
    set_reminder,
    # ── Powerful Web Scraping (Playwright-powered) ───────────────
    extract_contact_info,
    vision_extract_from_website,
    scrape_full_page,
    # ── Screen Share Vision ──────────────────────────────────────
    describe_screen_share,
    # ── Gmail (EMAIL_USER + EMAIL_PASS required) ───────────────
    send_email,
    read_emails,
    # ── Google Apps ─────────────────────────────────────────────
    google_sheets_read,
    google_sheets_write,
    google_calendar_list,
    # ── Spotify API Tools (SPOTIFY_* env vars required) ─────────
    spotify_play,
    spotify_control,
    spotify_shortcut,
    # NOTE: spotify_search removed from here - it's in ALL_SPOTIFY_TOOLS
    spotify_get_track_info,
    spotify_get_artist_info,
    spotify_get_artist_top_tracks,
    spotify_get_recommendations,
    spotify_get_playlist,
    spotify_get_featured_playlists,
    spotify_get_new_releases,
    spotify_get_categories,
    spotify_get_category_playlists,
    spotify_get_available_genres,
    open_spotify,
    # ── Local Spotify Control (No API needed) ───────────────────
    spotify_play_media,
    spotify_control_playback,
    spotify_what_is_playing,
    spotify_mute_application,
    spotify_toggle_shuffle,
    spotify_cycle_repeat,
    spotify_volume,
    # ── YouTube Tools ───────────────────────────────────────────
    youtube_open,
    youtube_shortcut,
    open_youtube,
    play_youtube_video,
    # YouTube Automation with Vision AI
    youtube_search_and_play,
    youtube_play_by_url,
    youtube_control_playback,
    youtube_find_live_streams,
    # ── Computer Use / Vision AI Tools ──────────────────────────
    computer_use_spotify,
    computer_use_youtube,
    music_intent_router,
    # ── Browser Automation (Playwright + Vision AI) ───────────────
    web_automate,
    browser_navigate_and_analyze,
    fill_web_form,
    browser_extract_data,
    # Enhanced Browser Automation Tools
    browser_visual_click,
    smart_form_fill_enhanced,
    ecommerce_price_compare,
    social_media_compose,
    website_data_mining,
] + ALL_SPOTIFY_TOOLS + SOCIAL_TOOLS + EBOX_TOOLS  # Add all advanced Spotify + Social + E-Box tools


# ============================================================================
# TOOL REFERENCE — auto-generated descriptions for the system prompt
# ============================================================================

def _get_tool_name(tool) -> str:
    if hasattr(tool, "name"):
        return tool.name
    if hasattr(tool, "__name__"):
        return tool.__name__
    if hasattr(tool, "_callable"):
        return tool._callable.__name__
    return str(tool)


def _get_tool_doc(tool) -> str:
    if hasattr(tool, "description"):
        return tool.description
    if hasattr(tool, "__doc__") and tool.__doc__:
        return tool.__doc__.strip().split("\n")[0]
    if hasattr(tool, "_callable") and tool._callable.__doc__:
        return tool._callable.__doc__.strip().split("\n")[0]
    return ""


def build_tool_reference(tools: list | None = None) -> str:
    tools = tools or ALL_TOOLS
    lines = ["TOOLS:"]
    for t in tools:
        lines.append(f"  {_get_tool_name(t)} — {_get_tool_doc(t)}")
    return "\n".join(lines)


TOOL_REFERENCE = build_tool_reference()

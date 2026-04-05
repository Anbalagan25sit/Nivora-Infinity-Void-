"""
======================================================================
  NIVORA TOKEN & CHAT SERVER - ULTIMATE EDITION
======================================================================
Flask server with ALL Nivora tools for web-based chat interface.
Includes comprehensive tool support for ultimate AI capabilities.

Run with: python token-server-ultimate.py
Server will start at http://localhost:5000

Endpoints:
  POST /api/livekit-token  - Get LiveKit access token (for voice)
  POST /api/chat           - Text-to-text chat with Nivora AI + ALL Tools
  POST /api/chat/clear     - Clear chat history
  GET  /health             - Health check
  GET  /tools              - List all available tools
"""

from flask import Flask, request, jsonify, Response
from flask_cors import CORS
from livekit import api
import os
import json
import sys
import webbrowser
import requests
import datetime
import subprocess
import smtplib
import imaplib
import email as _email
from email.header import decode_header as _decode_header
from email.mime.text import MIMEText
import time
import urllib.parse
import base64
import threading

try:
    import pyautogui
    PYAUTOGUI_AVAILABLE = True
except ImportError:
    PYAUTOGUI_AVAILABLE = False
    print("Warning: pyautogui not available. Some system controls disabled.")

try:
    # Try new package name first
    from ddgs import DDGS
except ImportError:
    try:
        # Fall back to old package name
        from duckduckgo_search import DDGS
    except ImportError:
        DDGS = None
        print("Warning: Neither 'ddgs' nor 'duckduckgo_search' found. Web search will not work.")

try:
    import pywhatkit
    PYWHATKIT_AVAILABLE = True
except ImportError:
    PYWHATKIT_AVAILABLE = False
    print("Warning: pywhatkit not available. YouTube auto-play limited.")

try:
    import gspread
    from google.oauth2.service_account import Credentials
    GOOGLE_SHEETS_AVAILABLE = True
except ImportError:
    GOOGLE_SHEETS_AVAILABLE = False
    print("Warning: Google Sheets integration not available.")

try:
    import spotipy
    from spotipy.oauth2 import SpotifyOAuth
    SPOTIFY_AVAILABLE = True
except ImportError:
    SPOTIFY_AVAILABLE = False
    print("Warning: Spotify integration not available.")

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))

# Import AWS config from parent directory
try:
    from aws_config import bedrock_client, bedrock_model, is_configured as aws_is_configured
    AWS_AVAILABLE = True
except ImportError:
    AWS_AVAILABLE = False
    print("Warning: aws_config not found. Text chat will be unavailable.")

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend requests

# LiveKit credentials
LIVEKIT_API_KEY = os.getenv("LIVEKIT_API_KEY", "APIgXpFTwkGbqkS")
LIVEKIT_API_SECRET = os.getenv("LIVEKIT_API_SECRET", "EhnJraYi9RjifXUeBmaQe37klSr6EI5lJQh0aWgU04ZA")
LIVEKIT_URL = os.getenv("LIVEKIT_URL", "wss://nivora-5opea2lo.livekit.cloud")

# Chat session storage
chat_sessions = {}

# ============================================================================
# WEBSITE MAPPINGS & CONSTANTS
# ============================================================================

WEBSITE_MAP = {
    # Social Media
    "youtube": "https://www.youtube.com", "github": "https://github.com",
    "google": "https://www.google.com", "gmail": "https://mail.google.com",
    "drive": "https://drive.google.com", "leetcode": "https://leetcode.com",
    "stackoverflow": "https://stackoverflow.com", "reddit": "https://www.reddit.com",
    "twitter": "https://twitter.com", "x": "https://x.com",
    "instagram": "https://www.instagram.com", "linkedin": "https://www.linkedin.com",
    "facebook": "https://www.facebook.com", "tiktok": "https://www.tiktok.com",
    # Entertainment
    "netflix": "https://www.netflix.com", "spotify": "https://open.spotify.com",
    "prime": "https://www.primevideo.com", "disney": "https://www.disneyplus.com",
    "hulu": "https://www.hulu.com", "twitch": "https://www.twitch.tv",
    # AI & Tools
    "chatgpt": "https://chat.openai.com", "claude": "https://claude.ai",
    "gemini": "https://gemini.google.com", "copilot": "https://copilot.microsoft.com",
    # Development
    "codepen": "https://codepen.io", "replit": "https://replit.com",
    "vercel": "https://vercel.com", "notion": "https://www.notion.so",
    # Shopping
    "amazon": "https://www.amazon.com", "ebay": "https://www.ebay.com",
    "flipkart": "https://www.flipkart.com", "myntra": "https://www.myntra.com",
}

# Notes storage
NOTES_FILE = "nivora_notes.json"

# ============================================================================
# ULTIMATE TOOL IMPLEMENTATIONS
# ============================================================================

# ── WEB & SEARCH TOOLS ──────────────────────────────────────────────────

def web_search(query: str) -> str:
    """Search the web using DuckDuckGo and return top 5 results."""
    if DDGS is None:
        return "Web search unavailable. Please install: pip install ddgs"

    try:
        results = DDGS().text(query, max_results=5)
        if not results:
            return "No results found."

        formatted = []
        for r in results:
            title = r.get('title', 'No title')
            url = r.get('href', '')
            body = r.get('body', '')[:150]
            formatted.append(f"• {title}\n  {url}\n  {body}...")

        return f"🔍 Search results for '{query}':\n\n" + "\n\n".join(formatted)
    except Exception as e:
        return f"Search failed: {str(e)}"

def open_website(target: str) -> str:
    """Open a website by name or URL."""
    try:
        t = target.strip().lower()

        # Direct URL
        if t.startswith(("http://", "https://", "www.")):
            url = target if target.startswith(("http://", "https://")) else "https://" + target
            webbrowser.open(url)
            return f"✅ Opened {url}"

        # Map common names to URLs
        key = t.replace(".com", "").replace(".org", "").replace(" ", "")
        url = WEBSITE_MAP.get(key) or WEBSITE_MAP.get(t) or f"https://www.{key}.com"
        webbrowser.open(url)
        return f"✅ Opened {url}"
    except Exception as e:
        return f"Error opening website: {str(e)}"

def get_weather(city: str) -> str:
    """Get current weather for a city using wttr.in."""
    try:
        r = requests.get(f"https://wttr.in/{city}?format=j1", timeout=5)
        if r.status_code == 200:
            data = r.json()
            current = data['current_condition'][0]
            temp_c = current['temp_C']
            feels_like = current['FeelsLikeC']
            desc = current['weatherDesc'][0]['value']
            humidity = current['humidity']
            wind = current['windspeedKmph']

            return f"🌡️ Weather in {city}:\n🌡️ {temp_c}°C (feels like {feels_like}°C)\n☁️ {desc}\n💧 Humidity: {humidity}%\n🌬️ Wind: {wind} km/h"
        return f"Could not get weather for {city}."
    except Exception as e:
        return f"Weather error: {str(e)}"

# ── UTILITY TOOLS ───────────────────────────────────────────────────────

def get_current_time() -> str:
    """Get the current time and date."""
    now = datetime.datetime.now()
    return f"🕐 Current time: {now.strftime('%I:%M %p')}\n📅 Date: {now.strftime('%A, %B %d, %Y')}"

def calculate(expression: str) -> str:
    """Safely evaluate a mathematical expression."""
    try:
        # Basic safety: only allow numbers and basic operators
        allowed_chars = set('0123456789+-*/()., ')
        if not all(c in allowed_chars for c in expression):
            return "Invalid expression. Only numbers and basic operators (+, -, *, /, parentheses) allowed."

        result = eval(expression, {"__builtins__": {}}, {})
        return f"🧮 {expression} = {result}"
    except Exception as e:
        return f"Calculation error: {str(e)}"

# ── NOTES & REMINDERS ───────────────────────────────────────────────────

def take_note(note: str) -> str:
    """Save a note."""
    try:
        # Load existing notes
        notes = []
        if os.path.exists(NOTES_FILE):
            with open(NOTES_FILE, 'r', encoding='utf-8') as f:
                notes = json.load(f)

        # Add new note with timestamp
        new_note = {
            "content": note,
            "timestamp": datetime.datetime.now().isoformat(),
            "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        }
        notes.append(new_note)

        # Save notes
        with open(NOTES_FILE, 'w', encoding='utf-8') as f:
            json.dump(notes, f, indent=2, ensure_ascii=False)

        return f"📝 Note saved: {note[:50]}{'...' if len(note) > 50 else ''}"
    except Exception as e:
        return f"Failed to save note: {str(e)}"

def read_notes(limit: int = 10) -> str:
    """Read recent notes."""
    try:
        if not os.path.exists(NOTES_FILE):
            return "📝 No notes found."

        with open(NOTES_FILE, 'r', encoding='utf-8') as f:
            notes = json.load(f)

        if not notes:
            return "📝 No notes found."

        # Get recent notes
        recent_notes = notes[-limit:] if len(notes) > limit else notes
        recent_notes.reverse()  # Show newest first

        result = f"📝 Your recent notes ({len(recent_notes)} of {len(notes)}):\n\n"
        for i, note in enumerate(recent_notes, 1):
            date = note.get('date', 'Unknown date')
            content = note.get('content', '')
            result += f"{i}. [{date}] {content}\n\n"

        return result.strip()
    except Exception as e:
        return f"Failed to read notes: {str(e)}"

def set_reminder(reminder: str, when: str = "in 1 hour") -> str:
    """Set a reminder (mock implementation for web)."""
    return f"⏰ Reminder set: '{reminder}' {when}\n(Note: This is a mock implementation for the web interface)"

# ── YOUTUBE TOOLS ───────────────────────────────────────────────────────

def play_youtube_video(query: str) -> str:
    """Search and play a YouTube video."""
    try:
        q = query.strip()

        if PYWHATKIT_AVAILABLE:
            try:
                # Try pywhatkit for auto-play
                pywhatkit.playonyt(q)
                return f"🎵 Playing '{q}' on YouTube (auto-play)"
            except Exception as e:
                print(f"pywhatkit failed: {e}")
                # Fall back to manual search
                pass

        # Fallback: Open YouTube search
        encoded = urllib.parse.quote(q)
        search_url = f"https://www.youtube.com/results?search_query={encoded}"
        webbrowser.open(search_url)
        return f"🎵 Opened YouTube search for '{q}' (manual play required)"

    except Exception as e:
        return f"Failed to play YouTube video: {str(e)}"

def youtube_shortcut(action: str) -> str:
    """Control YouTube with keyboard shortcuts."""
    if not PYAUTOGUI_AVAILABLE:
        return "❌ pyautogui not available. Install with: pip install pyautogui"

    try:
        action = action.lower()
        if action in ["play", "pause", "space"]:
            pyautogui.press("space")
            return "⏯️ Toggled YouTube play/pause"
        elif action in ["fullscreen", "f"]:
            pyautogui.press("f")
            return "🖥️ Toggled YouTube fullscreen"
        elif action in ["mute", "m"]:
            pyautogui.press("m")
            return "🔇 Toggled YouTube mute"
        elif action in ["next", "shift+n"]:
            pyautogui.hotkey("shift", "n")
            return "⏭️ Next YouTube video"
        elif action in ["prev", "previous", "shift+p"]:
            pyautogui.hotkey("shift", "p")
            return "⏮️ Previous YouTube video"
        else:
            return f"Unknown action: {action}. Use: play, pause, fullscreen, mute, next, previous"
    except Exception as e:
        return f"YouTube shortcut failed: {str(e)}"

def open_youtube() -> str:
    """Open YouTube in browser."""
    webbrowser.open("https://www.youtube.com")
    return "✅ Opened YouTube"

# ── SPOTIFY TOOLS ───────────────────────────────────────────────────────

def spotify_play(query: str) -> str:
    """Search and play on Spotify (web version)."""
    try:
        encoded = urllib.parse.quote(query)
        spotify_url = f"https://open.spotify.com/search/{encoded}"
        webbrowser.open(spotify_url)
        return f"🎵 Opened Spotify search for '{query}'"
    except Exception as e:
        return f"Failed to open Spotify: {str(e)}"

def open_spotify() -> str:
    """Open Spotify in browser."""
    webbrowser.open("https://open.spotify.com")
    return "✅ Opened Spotify"

def spotify_control(action: str) -> str:
    """Control Spotify with keyboard shortcuts."""
    if not PYAUTOGUI_AVAILABLE:
        return "❌ pyautogui not available. Install with: pip install pyautogui"

    try:
        action = action.lower()
        if action in ["play", "pause"]:
            pyautogui.press("space")
            return "⏯️ Toggled Spotify play/pause"
        elif action in ["next"]:
            pyautogui.hotkey("ctrl", "right")
            return "⏭️ Next track"
        elif action in ["previous", "prev"]:
            pyautogui.hotkey("ctrl", "left")
            return "⏮️ Previous track"
        elif action in ["volume_up"]:
            pyautogui.hotkey("ctrl", "up")
            return "🔊 Volume up"
        elif action in ["volume_down"]:
            pyautogui.hotkey("ctrl", "down")
            return "🔉 Volume down"
        else:
            return f"Unknown action: {action}. Use: play, pause, next, previous, volume_up, volume_down"
    except Exception as e:
        return f"Spotify control failed: {str(e)}"

# ── EMAIL TOOLS ─────────────────────────────────────────────────────────

def send_email(to: str, subject: str, body: str) -> str:
    """Send an email via Gmail SMTP."""
    try:
        email_user = os.getenv("EMAIL_USER")
        email_pass = os.getenv("EMAIL_PASS")

        if not email_user or not email_pass:
            return "❌ Email credentials not configured. Set EMAIL_USER and EMAIL_PASS in .env"

        # Create message
        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = email_user
        msg['To'] = to

        # Send via Gmail SMTP
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(email_user, email_pass)
            server.send_message(msg)

        return f"✅ Email sent to {to}: {subject}"
    except Exception as e:
        return f"Failed to send email: {str(e)}"

def read_emails(count: int = 5) -> str:
    """Read recent emails from Gmail."""
    try:
        email_user = os.getenv("EMAIL_USER")
        email_pass = os.getenv("EMAIL_PASS")

        if not email_user or not email_pass:
            return "❌ Email credentials not configured"

        # Connect to Gmail IMAP
        mail = imaplib.IMAP4_SSL('imap.gmail.com')
        mail.login(email_user, email_pass)
        mail.select('inbox')

        # Search for recent emails
        status, messages = mail.search(None, 'ALL')
        mail_ids = messages[0].split()

        if not mail_ids:
            mail.close()
            mail.logout()
            return "📧 No emails found"

        # Get recent emails
        recent_emails = mail_ids[-count:] if len(mail_ids) >= count else mail_ids

        result = f"📧 Your recent emails ({len(recent_emails)}):\n\n"

        for i, mail_id in enumerate(reversed(recent_emails), 1):
            status, msg_data = mail.fetch(mail_id, '(RFC822)')
            raw_email = msg_data[0][1]
            email_message = _email.message_from_bytes(raw_email)

            # Decode subject
            subject = email_message['Subject']
            if subject:
                decoded = _decode_header(subject)
                subject = decoded[0][0].decode() if isinstance(decoded[0][0], bytes) else decoded[0][0]

            sender = email_message['From']
            date = email_message['Date']

            result += f"{i}. From: {sender}\n   Subject: {subject}\n   Date: {date}\n\n"

        mail.close()
        mail.logout()
        return result

    except Exception as e:
        return f"Failed to read emails: {str(e)}"

# ── GOOGLE SHEETS TOOLS ─────────────────────────────────────────────────

def google_sheets_read(sheet_url: str, range_name: str = "A1:Z100") -> str:
    """Read data from Google Sheets."""
    try:
        if not GOOGLE_SHEETS_AVAILABLE:
            return "❌ Google Sheets not available. Install: pip install gspread google-auth"

        creds_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
        if not creds_path or not os.path.exists(creds_path):
            return "❌ Google credentials not found. Set GOOGLE_APPLICATION_CREDENTIALS"

        # Authenticate
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        creds = Credentials.from_service_account_file(creds_path, scopes=scope)
        gc = gspread.authorize(creds)

        # Open sheet
        sheet = gc.open_by_url(sheet_url).sheet1
        values = sheet.get(range_name)

        if not values:
            return "📊 No data found in the specified range"

        result = f"📊 Google Sheets data ({len(values)} rows):\n\n"
        for i, row in enumerate(values[:20], 1):  # Limit to 20 rows
            result += f"{i}. {' | '.join(str(cell) for cell in row)}\n"

        if len(values) > 20:
            result += f"\n... and {len(values) - 20} more rows"

        return result

    except Exception as e:
        return f"Failed to read Google Sheets: {str(e)}"

def google_sheets_write(sheet_url: str, range_name: str, data: str) -> str:
    """Write data to Google Sheets."""
    try:
        if not GOOGLE_SHEETS_AVAILABLE:
            return "❌ Google Sheets not available"

        creds_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
        if not creds_path or not os.path.exists(creds_path):
            return "❌ Google credentials not found"

        # Authenticate
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        creds = Credentials.from_service_account_file(creds_path, scopes=scope)
        gc = gspread.authorize(creds)

        # Open sheet and write data
        sheet = gc.open_by_url(sheet_url).sheet1

        # Parse data (assume comma-separated values)
        rows = [row.split(',') for row in data.split('\n') if row.strip()]
        sheet.update(range_name, rows)

        return f"✅ Data written to Google Sheets: {len(rows)} rows"

    except Exception as e:
        return f"Failed to write to Google Sheets: {str(e)}"

# ── SYSTEM CONTROL TOOLS ───────────────────────────────────────────────

def system_control(action: str) -> str:
    """Control system functions via keyboard shortcuts."""
    if not PYAUTOGUI_AVAILABLE:
        return "❌ pyautogui not available. Install with: pip install pyautogui"

    try:
        action = action.lower()

        if action in ["volume_up", "vol_up"]:
            pyautogui.press("volumeup")
            return "🔊 Volume up"
        elif action in ["volume_down", "vol_down"]:
            pyautogui.press("volumedown")
            return "🔉 Volume down"
        elif action in ["volume_mute", "mute"]:
            pyautogui.press("volumemute")
            return "🔇 Volume muted"
        elif action in ["media_play_pause", "play_pause"]:
            pyautogui.press("playpause")
            return "⏯️ Media play/pause"
        elif action in ["media_next", "next"]:
            pyautogui.press("nexttrack")
            return "⏭️ Next track"
        elif action in ["media_prev", "previous"]:
            pyautogui.press("prevtrack")
            return "⏮️ Previous track"
        elif action in ["brightness_up"]:
            pyautogui.hotkey("fn", "f2")  # Common brightness up
            return "☀️ Brightness up"
        elif action in ["brightness_down"]:
            pyautogui.hotkey("fn", "f1")  # Common brightness down
            return "🔅 Brightness down"
        else:
            return f"Unknown action: {action}. Available: volume_up, volume_down, volume_mute, play_pause, next, previous, brightness_up, brightness_down"

    except Exception as e:
        return f"System control failed: {str(e)}"

# ── SPECIAL TOOLS ───────────────────────────────────────────────────────

def show_love_feels() -> str:
    """Show how love feels by opening a special Instagram reel."""
    try:
        love_reel_url = "https://www.instagram.com/reel/DWaO8ogEzj3/?igsh=MXUyZDA2cTBpdnpzeA=="
        webbrowser.open(love_reel_url)
        return "💕 Opened Instagram reel showing how love feels... ✨"
    except Exception as e:
        return f"Failed to open love reel: {str(e)}"

def quick_screenshot() -> str:
    """Take a screenshot and save it."""
    if not PYAUTOGUI_AVAILABLE:
        return "❌ pyautogui not available. Install with: pip install pyautogui"

    try:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"screenshot_{timestamp}.png"
        screenshot = pyautogui.screenshot()
        screenshot.save(filename)
        return f"📸 Screenshot saved: {filename}"
    except Exception as e:
        return f"Failed to take screenshot: {str(e)}"

# ── NOTION TOOLS ────────────────────────────────────────────────────────

def notion_create_page(title: str, content: str) -> str:
    """Create a new page in Notion."""
    notion_token = os.getenv("NOTION_API_KEY") or os.getenv("NOTION_TOKEN")
    database_id = os.getenv("NOTION_DATABASE_ID")

    if not notion_token:
        return "❌ Notion not configured. Set NOTION_API_KEY in .env"

    if not database_id:
        return "❌ NOTION_DATABASE_ID not set in .env"

    try:
        headers = {
            "Authorization": f"Bearer {notion_token}",
            "Content-Type": "application/json",
            "Notion-Version": "2022-06-28"
        }

        data = {
            "parent": {"database_id": database_id},
            "properties": {
                "Name": {
                    "title": [{"text": {"content": title}}]
                }
            },
            "children": [{
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [{"type": "text", "text": {"content": content}}]
                }
            }]
        }

        response = requests.post(
            "https://api.notion.com/v1/pages",
            headers=headers,
            json=data,
            timeout=10
        )

        if response.status_code == 200:
            return f"✅ Created Notion page: {title}"
        else:
            return f"❌ Notion error: {response.status_code} - {response.text}"

    except Exception as e:
        return f"❌ Notion error: {str(e)}"

def notion_search(query: str) -> str:
    """Search Notion pages."""
    notion_token = os.getenv("NOTION_API_KEY") or os.getenv("NOTION_TOKEN")

    if not notion_token:
        return "❌ Notion not configured. Set NOTION_API_KEY in .env"

    try:
        headers = {
            "Authorization": f"Bearer {notion_token}",
            "Content-Type": "application/json",
            "Notion-Version": "2022-06-28"
        }

        data = {"query": query, "page_size": 5}

        response = requests.post(
            "https://api.notion.com/v1/search",
            headers=headers,
            json=data,
            timeout=10
        )

        if response.status_code == 200:
            results = response.json().get("results", [])
            if not results:
                return f"No Notion pages found for: {query}"

            pages = []
            for result in results:
                title = "Untitled"
                if result.get("properties", {}).get("Name"):
                    title_data = result["properties"]["Name"].get("title", [])
                    if title_data:
                        title = title_data[0].get("plain_text", "Untitled")

                url = result.get("url", "")
                pages.append(f"📝 {title}\n   {url}")

            return f"Found {len(pages)} Notion pages:\n\n" + "\n\n".join(pages)
        else:
            return f"❌ Notion error: {response.status_code}"

    except Exception as e:
        return f"❌ Notion error: {str(e)}"

# ============================================================================
# TOOL FUNCTION MAPPING
# ============================================================================

TOOL_FUNCTIONS = {
    # Web & Search
    "web_search": web_search,
    "open_website": open_website,
    "get_weather": get_weather,

    # Utility
    "get_current_time": get_current_time,
    "calculate": calculate,

    # Notes & Reminders
    "take_note": take_note,
    "read_notes": read_notes,
    "set_reminder": set_reminder,

    # YouTube
    "play_youtube_video": play_youtube_video,
    "youtube_shortcut": youtube_shortcut,
    "open_youtube": open_youtube,

    # Spotify
    "spotify_play": spotify_play,
    "spotify_control": spotify_control,
    "open_spotify": open_spotify,

    # Email
    "send_email": send_email,
    "read_emails": read_emails,

    # Google Sheets
    "google_sheets_read": google_sheets_read,
    "google_sheets_write": google_sheets_write,

    # System Control
    "system_control": system_control,

    # Notion
    "notion_create_page": notion_create_page,
    "notion_search": notion_search,

    # Special
    "show_love_feels": show_love_feels,
    "quick_screenshot": quick_screenshot,
}

# ============================================================================
# AWS BEDROCK TOOL SCHEMAS
# ============================================================================

TOOLS_SCHEMA = [
    # Web & Search Tools
    {
        "toolSpec": {
            "name": "web_search",
            "description": "Search the web using DuckDuckGo. Returns top 5 results with titles, URLs, and snippets.",
            "inputSchema": {
                "json": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Search query"}
                    },
                    "required": ["query"]
                }
            }
        }
    },
    {
        "toolSpec": {
            "name": "open_website",
            "description": "Open a website by name or URL in the default browser.",
            "inputSchema": {
                "json": {
                    "type": "object",
                    "properties": {
                        "target": {"type": "string", "description": "Website name (e.g., 'youtube', 'google') or full URL"}
                    },
                    "required": ["target"]
                }
            }
        }
    },
    {
        "toolSpec": {
            "name": "get_weather",
            "description": "Get current weather information for any city worldwide.",
            "inputSchema": {
                "json": {
                    "type": "object",
                    "properties": {
                        "city": {"type": "string", "description": "City name (e.g., 'London', 'New York', 'Tokyo')"}
                    },
                    "required": ["city"]
                }
            }
        }
    },

    # Utility Tools
    {
        "toolSpec": {
            "name": "get_current_time",
            "description": "Get the current time and date.",
            "inputSchema": {
                "json": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            }
        }
    },
    {
        "toolSpec": {
            "name": "calculate",
            "description": "Perform mathematical calculations safely. Supports basic arithmetic operations.",
            "inputSchema": {
                "json": {
                    "type": "object",
                    "properties": {
                        "expression": {"type": "string", "description": "Mathematical expression (e.g., '2 + 2', '(10 * 5) / 2')"}
                    },
                    "required": ["expression"]
                }
            }
        }
    },

    # Notes & Reminders
    {
        "toolSpec": {
            "name": "take_note",
            "description": "Save a note with timestamp for later reference.",
            "inputSchema": {
                "json": {
                    "type": "object",
                    "properties": {
                        "note": {"type": "string", "description": "The note content to save"}
                    },
                    "required": ["note"]
                }
            }
        }
    },
    {
        "toolSpec": {
            "name": "read_notes",
            "description": "Read recent saved notes.",
            "inputSchema": {
                "json": {
                    "type": "object",
                    "properties": {
                        "limit": {"type": "integer", "description": "Number of recent notes to show (default: 10)", "default": 10}
                    },
                    "required": []
                }
            }
        }
    },
    {
        "toolSpec": {
            "name": "set_reminder",
            "description": "Set a reminder (mock implementation for web interface).",
            "inputSchema": {
                "json": {
                    "type": "object",
                    "properties": {
                        "reminder": {"type": "string", "description": "Reminder text"},
                        "when": {"type": "string", "description": "When to remind (e.g., 'in 1 hour', 'tomorrow')", "default": "in 1 hour"}
                    },
                    "required": ["reminder"]
                }
            }
        }
    },

    # YouTube Tools
    {
        "toolSpec": {
            "name": "play_youtube_video",
            "description": "Search and play ANY song or video on YouTube. Primary tool for YouTube playback.",
            "inputSchema": {
                "json": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Song name, artist, or video search query"}
                    },
                    "required": ["query"]
                }
            }
        }
    },
    {
        "toolSpec": {
            "name": "youtube_shortcut",
            "description": "Control YouTube with keyboard shortcuts (play/pause, fullscreen, mute, next, previous).",
            "inputSchema": {
                "json": {
                    "type": "object",
                    "properties": {
                        "action": {"type": "string", "description": "Action: play, pause, fullscreen, mute, next, previous"}
                    },
                    "required": ["action"]
                }
            }
        }
    },
    {
        "toolSpec": {
            "name": "open_youtube",
            "description": "Open YouTube website in the browser.",
            "inputSchema": {
                "json": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            }
        }
    },

    # Spotify Tools
    {
        "toolSpec": {
            "name": "spotify_play",
            "description": "Search and open Spotify with a specific song or artist.",
            "inputSchema": {
                "json": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Song name, artist, or search query for Spotify"}
                    },
                    "required": ["query"]
                }
            }
        }
    },
    {
        "toolSpec": {
            "name": "spotify_control",
            "description": "Control Spotify playback with keyboard shortcuts.",
            "inputSchema": {
                "json": {
                    "type": "object",
                    "properties": {
                        "action": {"type": "string", "description": "Action: play, pause, next, previous, volume_up, volume_down"}
                    },
                    "required": ["action"]
                }
            }
        }
    },
    {
        "toolSpec": {
            "name": "open_spotify",
            "description": "Open Spotify web player in the browser.",
            "inputSchema": {
                "json": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            }
        }
    },

    # Email Tools
    {
        "toolSpec": {
            "name": "send_email",
            "description": "Send an email via Gmail SMTP. Requires EMAIL_USER and EMAIL_PASS environment variables.",
            "inputSchema": {
                "json": {
                    "type": "object",
                    "properties": {
                        "to": {"type": "string", "description": "Recipient email address"},
                        "subject": {"type": "string", "description": "Email subject"},
                        "body": {"type": "string", "description": "Email body content"}
                    },
                    "required": ["to", "subject", "body"]
                }
            }
        }
    },
    {
        "toolSpec": {
            "name": "read_emails",
            "description": "Read recent emails from Gmail inbox. Requires EMAIL_USER and EMAIL_PASS.",
            "inputSchema": {
                "json": {
                    "type": "object",
                    "properties": {
                        "count": {"type": "integer", "description": "Number of recent emails to read (default: 5)", "default": 5}
                    },
                    "required": []
                }
            }
        }
    },

    # Google Sheets Tools
    {
        "toolSpec": {
            "name": "google_sheets_read",
            "description": "Read data from Google Sheets. Requires GOOGLE_APPLICATION_CREDENTIALS.",
            "inputSchema": {
                "json": {
                    "type": "object",
                    "properties": {
                        "sheet_url": {"type": "string", "description": "Google Sheets URL"},
                        "range_name": {"type": "string", "description": "Range to read (e.g., 'A1:Z100')", "default": "A1:Z100"}
                    },
                    "required": ["sheet_url"]
                }
            }
        }
    },
    {
        "toolSpec": {
            "name": "google_sheets_write",
            "description": "Write data to Google Sheets. Requires GOOGLE_APPLICATION_CREDENTIALS.",
            "inputSchema": {
                "json": {
                    "type": "object",
                    "properties": {
                        "sheet_url": {"type": "string", "description": "Google Sheets URL"},
                        "range_name": {"type": "string", "description": "Range to write (e.g., 'A1:C3')"},
                        "data": {"type": "string", "description": "Data to write (comma-separated values, newline for rows)"}
                    },
                    "required": ["sheet_url", "range_name", "data"]
                }
            }
        }
    },

    # System Control Tools
    {
        "toolSpec": {
            "name": "system_control",
            "description": "Control system functions like volume, media playback, brightness via keyboard shortcuts.",
            "inputSchema": {
                "json": {
                    "type": "object",
                    "properties": {
                        "action": {"type": "string", "description": "Action: volume_up, volume_down, volume_mute, play_pause, next, previous, brightness_up, brightness_down"}
                    },
                    "required": ["action"]
                }
            }
        }
    },

    # Notion Tools
    {
        "toolSpec": {
            "name": "notion_create_page",
            "description": "Create a new page in Notion. Requires NOTION_API_KEY and NOTION_DATABASE_ID.",
            "inputSchema": {
                "json": {
                    "type": "object",
                    "properties": {
                        "title": {"type": "string", "description": "Page title"},
                        "content": {"type": "string", "description": "Page content"}
                    },
                    "required": ["title", "content"]
                }
            }
        }
    },
    {
        "toolSpec": {
            "name": "notion_search",
            "description": "Search for pages in Notion workspace. Requires NOTION_API_KEY.",
            "inputSchema": {
                "json": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Search query"}
                    },
                    "required": ["query"]
                }
            }
        }
    },

    # Special Tools
    {
        "toolSpec": {
            "name": "show_love_feels",
            "description": "Show how love feels by opening a special visual experience. Use when asked about love feelings.",
            "inputSchema": {
                "json": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            }
        }
    },
    {
        "toolSpec": {
            "name": "quick_screenshot",
            "description": "Take a screenshot and save it with timestamp.",
            "inputSchema": {
                "json": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            }
        }
    }
]

# ============================================================================
# NIVORA SYSTEM PROMPT - ULTIMATE EDITION
# ============================================================================

NIVORA_SYSTEM_PROMPT = """You are Nivora, an ultimate AI assistant created by Anbalagan. You have access to a comprehensive suite of tools for maximum capability.

🎯 **ULTIMATE TOOL SUITE AVAILABLE:**

**🌐 Web & Search:**
- web_search: Search the web for current information and news
- open_website: Open any website by name or URL
- get_weather: Get weather for any city worldwide

**⚙️ Utility:**
- get_current_time: Current date and time
- calculate: Mathematical calculations
- quick_screenshot: Take and save screenshots

**📝 Notes & Organization:**
- take_note: Save notes with timestamps
- read_notes: View recent saved notes
- set_reminder: Set reminders (mock for web)

**🎵 YouTube (CRITICAL - PRIMARY MUSIC PLATFORM):**
When user asks to play ANY song/video on YouTube, IMMEDIATELY call play_youtube_video:
- "play [song] on youtube" → play_youtube_video("song name")
- "youtube play [song]" → play_youtube_video("song name")
- "play [song]" (general) → play_youtube_video("song name")
- youtube_shortcut: Control playback (play/pause/fullscreen/mute/next/prev)
- open_youtube: Open YouTube homepage

**🎶 Spotify:**
- spotify_play: Search and open songs on Spotify
- spotify_control: Control playback with shortcuts
- open_spotify: Open Spotify web player

**📧 Email (requires EMAIL_USER/EMAIL_PASS):**
- send_email: Send emails via Gmail
- read_emails: Read recent Gmail messages

**📊 Google Sheets (requires GOOGLE_APPLICATION_CREDENTIALS):**
- google_sheets_read: Read spreadsheet data
- google_sheets_write: Write data to sheets

**🔧 System Control:**
- system_control: Volume, media, brightness controls

**📝 Notion (requires NOTION_API_KEY):**
- notion_create_page: Create new Notion pages
- notion_search: Search Notion workspace

**💕 Special Features:**
- show_love_feels: Special visual experience for love-related questions

**🎯 CRITICAL BEHAVIORS:**

1. **YOUTUBE PRIORITY**: For any music/video request, use play_youtube_video FIRST
2. **PROACTIVE TOOL USE**: Use tools immediately when relevant - don't ask permission
3. **MULTI-STEP TASKS**: Chain tools together for complex requests
4. **ERROR HANDLING**: If one tool fails, try alternatives
5. **LOVE QUESTIONS**: If user asks about love feelings → show_love_feels()

**📋 Example Workflows:**
- "play Shape of You" → play_youtube_video("Shape of You Ed Sheeran")
- "check weather and take a note" → get_weather() + take_note()
- "email my boss about the meeting" → send_email()
- "how does love feel?" → show_love_feels()
- "create a notion page about AI" → notion_create_page()
- "take a screenshot" → quick_screenshot()

Be helpful, proactive, and use your tools effectively to provide the best possible assistance!"""

# ============================================================================
# RESPONSE CLEANING
# ============================================================================

def _clean_response(text: str) -> str:
    """Clean up response text."""
    # Remove thinking tags if any
    while '<thinking>' in text and '</thinking>' in text:
        start = text.find('<thinking>')
        end = text.find('</thinking>') + len('</thinking>')
        text = text[:start] + text[end:]

    return text.strip()

# ============================================================================
# API ENDPOINTS
# ============================================================================

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    status = {
        "status": "healthy",
        "aws_available": AWS_AVAILABLE,
        "tools_count": len(TOOL_FUNCTIONS),
        "integrations": {
            "ddgs": DDGS is not None,
            "pywhatkit": PYWHATKIT_AVAILABLE,
            "pyautogui": PYAUTOGUI_AVAILABLE,
            "google_sheets": GOOGLE_SHEETS_AVAILABLE,
            "spotify": SPOTIFY_AVAILABLE
        }
    }
    return jsonify(status)

@app.route('/tools', methods=['GET'])
def list_tools():
    """List all available tools."""
    tools_info = []
    for name, func in TOOL_FUNCTIONS.items():
        tools_info.append({
            "name": name,
            "description": func.__doc__ or "No description available"
        })
    return jsonify({"tools": tools_info, "count": len(tools_info)})

@app.route('/api/livekit-token', methods=['POST'])
def get_livekit_token():
    """Generate LiveKit access token."""
    try:
        data = request.get_json()
        room_name = data.get('room', 'default-room')
        user_name = data.get('user', 'user')

        # Generate token
        token = api.AccessToken(LIVEKIT_API_KEY, LIVEKIT_API_SECRET) \
            .with_identity(user_name) \
            .with_name(user_name) \
            .with_grants(api.VideoGrants(
                room=room_name,
                room_join=True,
                can_publish=True,
                can_subscribe=True
            )).to_jwt()

        return jsonify({
            'token': token,
            'room': room_name,
            'url': LIVEKIT_URL
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Extension-compatible token endpoint (matches what nivora-extension expects)
@app.route('/api/token', methods=['GET'])
def get_token_for_extension():
    """Generate LiveKit token for browser extension (GET method with query params)."""
    try:
        room = request.args.get('room', 'nivora-assistant')
        participant = request.args.get('participant', 'user')

        # Generate token using the same logic as /api/livekit-token
        token = api.AccessToken(LIVEKIT_API_KEY, LIVEKIT_API_SECRET) \
            .with_identity(participant) \
            .with_name(participant) \
            .with_grants(api.VideoGrants(
                room=room,
                room_join=True,
                can_publish=True,
                can_subscribe=True
            )).to_jwt()

        return jsonify({
            'token': token,
            'room': room,
            'participant': participant
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/chat/clear', methods=['POST'])
def clear_chat():
    """Clear chat history for a session."""
    try:
        data = request.get_json()
        session_id = data.get('session_id', 'default')

        if session_id in chat_sessions:
            del chat_sessions[session_id]

        return jsonify({'success': True, 'message': 'Chat history cleared'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/chat', methods=['POST'])
def chat():
    """Main chat endpoint with tool support."""
    if not AWS_AVAILABLE or not aws_is_configured():
        return jsonify({'error': 'AWS Bedrock not configured. Check your .env file.'}), 500

    try:
        data = request.get_json()
        user_message = data.get('message', '')
        session_id = data.get('session_id', 'default')

        if not user_message:
            return jsonify({'error': 'No message provided'}), 400

        print(f"Chat request from session {session_id}: {user_message[:100]}...")

        # Get or initialize chat history
        history = chat_sessions.get(session_id, [])

        # Prepare messages for AWS Bedrock
        messages = history.copy()
        messages.append({"role": "user", "content": [{"text": user_message}]})

        tool_calls = []  # Track tool calls for frontend
        max_turns = 10  # Prevent infinite loops

        for turn in range(max_turns):
            try:
                # Call AWS Bedrock
                response = bedrock_client().converse(
                    modelId=bedrock_model(),
                    system=[{"text": NIVORA_SYSTEM_PROMPT}],
                    messages=messages,
                    toolConfig={"tools": TOOLS_SCHEMA}
                )

                output_message = response['output']['message']
                content = output_message['content']

                # Check if AI wants to use tools
                if any('toolUse' in item for item in content):
                    # Process tool calls
                    for item in content:
                        if 'toolUse' in item:
                            tool_use = item['toolUse']
                            tool_name = tool_use['name']
                            tool_input = tool_use['input']
                            tool_use_id = tool_use['toolUseId']

                            print(f"Tool call: {tool_name} with {tool_input}")

                            # Execute the tool
                            tool_func = TOOL_FUNCTIONS.get(tool_name)
                            if tool_func:
                                try:
                                    tool_result = tool_func(**tool_input)
                                    print(f"Tool result: {tool_result[:100]}...")
                                except Exception as e:
                                    tool_result = f"Tool execution error: {str(e)}"
                                    print(f"Tool error: {e}")
                            else:
                                tool_result = f"Unknown tool: {tool_name}"

                            # Record tool call for frontend
                            tool_calls.append({
                                "name": tool_name,
                                "input": tool_input,
                                "result": tool_result
                            })

                            # Add tool result back to conversation
                            messages.append({
                                "role": "user",
                                "content": [{
                                    "toolResult": {
                                        "toolUseId": tool_use_id,
                                        "content": [{"text": tool_result}]
                                    }
                                }]
                            })
                    # Continue loop to get final response
                    continue

                else:
                    # Got final text response
                    reply_text = ""
                    for item in content:
                        if "text" in item:
                            reply_text += item["text"]

                    reply_text = _clean_response(reply_text)
                    print(f"Final reply: {reply_text[:100]}...")

                    # Save to history (user message + final assistant message)
                    history.append({"role": "user", "content": [{"text": user_message}]})
                    history.append({"role": "assistant", "content": [{"text": reply_text}]})

                    # Limit history size
                    if len(history) > 40:
                        chat_sessions[session_id] = history[-40:]
                    else:
                        chat_sessions[session_id] = history

                    return jsonify({
                        'reply': reply_text,
                        'tool_calls': tool_calls,
                        'session_id': session_id
                    })

            except Exception as e:
                print(f"Bedrock error on turn {turn}: {e}")
                if turn == 0:  # If first turn fails, return error
                    return jsonify({'error': f'AI processing failed: {str(e)}'}), 500
                else:  # If later turn fails, return what we have
                    return jsonify({
                        'reply': 'I encountered an error while processing your request.',
                        'tool_calls': tool_calls,
                        'session_id': session_id
                    })

        # If we hit max turns, return partial response
        return jsonify({
            'reply': 'I processed your request but reached the maximum number of steps.',
            'tool_calls': tool_calls,
            'session_id': session_id
        })

    except Exception as e:
        print(f"Chat error: {e}")
        return jsonify({'error': str(e)}), 500

# ============================================================================
# MAIN
# ============================================================================

if __name__ == '__main__':
    print("=" * 70)
    print("  NIVORA TOKEN & CHAT SERVER - ULTIMATE EDITION")
    print("=" * 70)
    print(f"🔧 Available tools: {len(TOOL_FUNCTIONS)}")
    print(f"🤖 AWS Bedrock: {'✅' if AWS_AVAILABLE else '❌'}")
    print(f"🔍 Web search: {'✅' if DDGS else '❌'}")
    print(f"🎵 YouTube auto-play: {'✅' if PYWHATKIT_AVAILABLE else '❌'}")
    print(f"🖱️ System control: {'✅' if PYAUTOGUI_AVAILABLE else '❌'}")
    print(f"📊 Google Sheets: {'✅' if GOOGLE_SHEETS_AVAILABLE else '❌'}")
    print(f"🎶 Spotify API: {'✅' if SPOTIFY_AVAILABLE else '❌'}")
    print("=" * 70)

    # List all available tools by category
    print("\n🛠️ ULTIMATE TOOL SUITE:")
    for category, tools in [
        ("Web & Search", ["web_search", "open_website", "get_weather"]),
        ("Utility", ["get_current_time", "calculate", "quick_screenshot"]),
        ("Notes & Organization", ["take_note", "read_notes", "set_reminder"]),
        ("YouTube", ["play_youtube_video", "youtube_shortcut", "open_youtube"]),
        ("Spotify", ["spotify_play", "spotify_control", "open_spotify"]),
        ("Email", ["send_email", "read_emails"]),
        ("Google Sheets", ["google_sheets_read", "google_sheets_write"]),
        ("System Control", ["system_control"]),
        ("Notion", ["notion_create_page", "notion_search"]),
        ("Special", ["show_love_feels"])
    ]:
        available = [t for t in tools if t in TOOL_FUNCTIONS]
        if available:
            print(f"  📂 {category}: {', '.join(available)}")

    print("\n🚀 Starting server at http://localhost:8080")
    print("📡 LiveKit tokens available at /api/livekit-token")
    print("📡 Extension tokens available at /api/token")
    print("💬 Chat API available at /api/chat")
    print("🛠️ Tools list available at /tools")
    print("🏥 Health check available at /health")
    print("=" * 70)

    app.run(host='0.0.0.0', port=8080, debug=True)
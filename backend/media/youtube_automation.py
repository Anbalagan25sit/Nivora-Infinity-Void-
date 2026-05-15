"""
YouTube Automation Module for Nivora

Provides intelligent YouTube video and live stream playback:
- Search and play videos by natural language query
- Automatically detect and play live streams
- Handle "recently uploaded" and temporal queries
- Vision-guided browser interaction
- Direct playback without manual clicking

Example usage:
- "play recently repo tamil gaming live"
- "play the latest MrBeast video"
- "play lofi hip hop radio live"
- "play Pewdiepie's newest video"
"""

import logging
import asyncio
import webbrowser
import time
from typing import Annotated, Optional, Dict, Any
from urllib.parse import quote_plus

from livekit.agents import RunContext, function_tool

# Import vision and desktop control
import computer_use as _cu
import pyautogui
from desktop_control import keyboard_type, keyboard_press, mouse_click

# Import safety and audit
from audit_log import log_tool_execution

logger = logging.getLogger(__name__)


def _make_autoplay_url(watch_url: str) -> str:
    """Append &autoplay=1 to a YouTube watch URL."""
    sep = "&" if "?" in watch_url else "?"
    return f"{watch_url}{sep}autoplay=1"


async def _click_play_after_load(delay: float = 4.0) -> None:
    """
    Background task: wait for YouTube to load, then start video playback via
    Playwright CDP (browser-internal DOM call — no physical mouse needed).

    Flow:
      1. Chrome was opened with --remote-debugging-port=9222.
      2. Playwright connects to that existing Chrome instance via CDP.
      3. Finds the YouTube tab and calls video.play() via JavaScript.
      4. Disconnects (leaves Chrome running for the user).

    Falls back to pyautogui window-click if Playwright/CDP is unavailable.
    """
    await asyncio.sleep(delay)
    try:
        from playwright.async_api import async_playwright
        async with async_playwright() as pw:
            # Attach to the running Chrome instance on the debug port
            browser = await pw.chromium.connect_over_cdp("http://localhost:9222")
            # Find the YouTube page
            yt_page = None
            for ctx in browser.contexts:
                for page in ctx.pages:
                    if "youtube.com/watch" in page.url:
                        yt_page = page
                        break
                if yt_page:
                    break

            if yt_page is None:
                logger.warning("[YouTube] CDP connected but no youtube.com/watch tab found")
            else:
                # DOM-level play — no cursor, no focus required
                await yt_page.evaluate("document.querySelector('video')?.play()")
                logger.info(f"[YouTube] CDP: called video.play() on {yt_page.url}")

            await browser.close()   # closes the CDP connection, NOT the browser process
        return

    except Exception as cdp_err:
        logger.warning(f"[YouTube] CDP play failed ({cdp_err}), falling back to window click")

    # ── Fallback: pyautogui window click ────────────────────────────────────
    try:
        import pygetwindow as gw
        wins = [w for w in gw.getAllWindows() if w.title and "youtube" in w.title.lower()]
        if not wins:
            logger.warning("[YouTube] No YouTube window found for fallback click.")
            return
        win = wins[0]
        win.activate()
        await asyncio.sleep(0.4)
        cx = win.left + win.width  // 2
        cy = win.top  + win.height // 2 - 40
        pyautogui.click(cx, cy)
        logger.info(f"[YouTube] Fallback click at ({cx}, {cy}) in '{win.title}'")
    except Exception as e:
        logger.warning(f"[YouTube] Fallback click also failed: {e}")


def _open_youtube_url(url: str) -> None:
    """
    Open a YouTube URL in the user's default browser.

    Uses webbrowser.open() which is the MOST reliable method:
    - Works whether the browser is already running or not.
    - Properly uses single-instance IPC to open a new tab in the existing window.
    - subprocess.Popen with DETACHED_PROCESS broke Chrome IPC on second calls.

    Also launches Chrome with --remote-debugging-port=9222 so that
    _click_play_after_load() can attach via Playwright CDP and call video.play()
    without any physical mouse movement.
    """
    import os, subprocess

    # Try to (re-)launch Chrome with the debug port if it isn't already open.
    # If Chrome is already running it will just open a new tab.
    candidates = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"),
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
        os.path.expandvars(r"%LOCALAPPDATA%\Microsoft\Edge\Application\msedge.exe"),
    ]
    for exe in candidates:
        if os.path.isfile(exe):
            subprocess.Popen(
                [exe, "--remote-debugging-port=9222",
                 "--autoplay-policy=no-user-gesture-required", url],
            )
            logger.info(f"[YouTube] Launched browser with CDP port: {url}")
            return

    # Fallback if no Chrome/Edge found
    logger.warning("[YouTube] No Chrome/Edge found — using webbrowser.open()")
    webbrowser.open(url)


@function_tool()
async def youtube_search_and_play(
    context: RunContext,
    query: Annotated[str, "Natural language search query (e.g., 'gojo vs sukuna', 'latest MrBeast video')"],
    prefer_live: Annotated[bool, "Prefer live streams over regular videos"] = False
) -> str:
    """
    Search YouTube for a query and DIRECTLY OPEN AND PLAY the first matching video.

    ALWAYS use this tool when the user wants to play or watch something on YouTube.
    This tool fetches video IDs from YouTube search results and opens the actual watch URL.
    Do NOT use youtube_play_by_url with a search URL — use this tool for searching.

    Args:
        query: Natural language search query (e.g. 'gojo vs sukuna', 'lofi radio')
        prefer_live: If True, prioritizes live streams in results

    Returns:
        Status message with the video URL that was opened
    """
    try:
        logger.info(f"YouTube search and play: {query}, prefer_live={prefer_live}")

        import urllib.request
        import urllib.parse
        import re

        add_live_filter = prefer_live and "live" not in query.lower()
        encoded_query = urllib.parse.quote_plus(query)
        youtube_search_url = f"https://www.youtube.com/results?search_query={encoded_query}"

        if add_live_filter:
            youtube_search_url += "&sp=EgJAAQ%253D%253D"

        logger.info(f"Fetching YouTube search results: {youtube_search_url}")

        def _fetch(url):
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            return urllib.request.urlopen(req).read().decode('utf-8')

        html = await asyncio.to_thread(_fetch, youtube_search_url)
        # deduplicate while preserving order
        seen = set()
        video_ids = []
        for vid in re.findall(r"watch\?v=([\w-]{11})", html):
            if vid not in seen:
                seen.add(vid)
                video_ids.append(vid)

        if video_ids:
            video_id = video_ids[0]
            watch_url = _make_autoplay_url(f"https://www.youtube.com/watch?v={video_id}")
            _open_youtube_url(watch_url)
            asyncio.create_task(_click_play_after_load(delay=4.0))
            logger.info(f"[YouTube] Opened + scheduled auto-play click: {watch_url}")

            log_tool_execution(
                tool_name="youtube_search_and_play",
                params={"query": query, "prefer_live": prefer_live},
                user_confirmed=False,
                result="success",
                session_id=getattr(context, 'room', None) and context.room.name or "unknown"
            )
            return f"Now playing '{query}' on YouTube. Video URL: {watch_url}"
        else:
            return f"Could not find any YouTube videos for '{query}'."

    except Exception as e:
        logger.error(f"YouTube search and play failed: {e}", exc_info=True)
        return f"Failed to play YouTube video: {e}"


@function_tool()
async def youtube_play_by_url(
    context: RunContext,
    url: Annotated[str, "Full YouTube watch URL (https://www.youtube.com/watch?v=...) or a search query string"]
) -> str:
    """
    Play a specific YouTube video by its direct watch URL.
    If a search-results URL or plain search query is provided instead of a watch URL,
    this function will automatically extract and open the first matching video.

    Args:
        url: A YouTube watch URL like https://www.youtube.com/watch?v=VIDEO_ID
             OR a search-results URL (will auto-extract first video)
             OR a plain search query string (will search and play)

    Example:
        youtube_play_by_url("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
    """
    import urllib.request
    import urllib.parse
    import re

    try:
        logger.info(f"Opening YouTube URL: {url}")

        # ── Detect and fix search-results URLs ──────────────────────────────
        # If the LLM passes a /results?search_query=... URL instead of a
        # watch URL, we resolve it to the first real video ourselves.
        if "youtube.com/results" in url or (url and not url.startswith("http") and "watch?v=" not in url):
            # Either a search-results URL or a bare query string
            if url.startswith("http"):
                search_url = url
                logger.info(f"[YouTube] Received search URL — extracting first video: {search_url}")
            else:
                encoded = urllib.parse.quote_plus(url)
                search_url = f"https://www.youtube.com/results?search_query={encoded}"
                logger.info(f"[YouTube] Plain query received — searching: {search_url}")

            def _fetch(u):
                req = urllib.request.Request(u, headers={'User-Agent': 'Mozilla/5.0'})
                return urllib.request.urlopen(req).read().decode('utf-8')

            html = await asyncio.to_thread(_fetch, search_url)
            seen = set()
            video_ids = []
            for vid in re.findall(r"watch\?v=([\w-]{11})", html):
                if vid not in seen:
                    seen.add(vid)
                    video_ids.append(vid)

            if video_ids:
                url = f"https://www.youtube.com/watch?v={video_ids[0]}"
                logger.info(f"[YouTube] Resolved to first video: {url}")
            else:
                return f"Could not find any YouTube videos for the given URL/query."

        # ── Open URL + schedule background click ─────────────────────────────
        autoplay_url = _make_autoplay_url(url)
        _open_youtube_url(autoplay_url)
        asyncio.create_task(_click_play_after_load(delay=4.0))
        logger.info(f"[YouTube] Opened + scheduled auto-play click: {autoplay_url}")

        log_tool_execution(
            tool_name="youtube_play_by_url",
            params={"url": autoplay_url},
            user_confirmed=False,
            result="success",
            session_id=getattr(context, 'room', None) and context.room.name or "unknown"
        )

        return f"Opened and playing YouTube video: {autoplay_url}"

    except Exception as e:
        logger.error(f"YouTube URL playback failed: {e}", exc_info=True)
        return f"Failed to open YouTube URL: {e}"


@function_tool()
async def youtube_control_playback(
    context: RunContext,
    action: Annotated[str, "Playback action: 'play', 'pause', 'fullscreen', 'mute', 'skip_ad'"]
) -> str:
    """
    Control YouTube video playback using keyboard shortcuts.

    Args:
        action: One of: 'play', 'pause', 'fullscreen', 'mute', 'skip_ad'

    Keyboard shortcuts:
    - play/pause: Spacebar or 'k'
    - fullscreen: 'f'
    - mute: 'm'
    - skip_ad: Tab then Enter

    Example:
        youtube_control_playback("fullscreen")
    """
    try:
        logger.info(f"YouTube playback control: {action}")

        action_lower = action.lower()

        if action_lower in ["play", "pause", "playpause"]:
            # Press spacebar or K
            pyautogui.press("k")
            result_msg = "Toggled play/pause"

        elif action_lower == "fullscreen":
            pyautogui.press("f")
            result_msg = "Toggled fullscreen"

        elif action_lower == "mute":
            pyautogui.press("m")
            result_msg = "Toggled mute"

        elif action_lower == "skip_ad":
            # Use vision to find and click skip ad button
            img = _cu.capture_screen()
            ad_prompt = """
Find the "Skip Ad" or "Skip Ads" button on this YouTube page.

Look for:
1. "Skip Ad" button (usually bottom right of video player)
2. "Skip Ads" button
3. Any clickable skip button

Return JSON:
{
    "skip_button_found": true/false,
    "skip_x": <x coordinate of skip button center>,
    "skip_y": <y coordinate of skip button center>
}

IMPORTANT: Return ONLY valid JSON.
"""
            skip_response = _cu.analyze_screen(ad_prompt, img, temperature=0.1, backend="aws")
            if isinstance(skip_response, str):
                skip_response = skip_response.strip()
                if skip_response.startswith("```"):
                    skip_response = skip_response.split("\n", 1)[1]
                    skip_response = skip_response.rsplit("```", 1)[0]
                import json
                skip_response = json.loads(skip_response)

            if skip_response.get("skip_button_found", False):
                skip_x = int(skip_response.get("skip_x", 0))
                skip_y = int(skip_response.get("skip_y", 0))
                if skip_x > 0 and skip_y > 0:
                    pyautogui.click(skip_x, skip_y)
                    result_msg = "Clicked skip ad button"
                else:
                    # Fallback to keyboard
                    pyautogui.press("tab")
                    await asyncio.sleep(0.2)
                    pyautogui.press("enter")
                    result_msg = "Attempted to skip ad via keyboard"
            else:
                result_msg = "No skip ad button found - ad may be non-skippable or no ad playing"

        else:
            return f"Unknown action: {action}. Use 'play', 'pause', 'fullscreen', 'mute', or 'skip_ad'"

        log_tool_execution(
            tool_name="youtube_control_playback",
            params={"action": action},
            user_confirmed=False,
            result="success",
            session_id=getattr(context, 'room', None) and context.room.name or "unknown"
        )

        return result_msg

    except Exception as e:
        logger.error(f"YouTube playback control failed: {e}", exc_info=True)
        return f"Failed to control playback: {e}"


@function_tool()
async def youtube_find_live_streams(
    context: RunContext,
    channel_or_topic: Annotated[str, "Channel name or topic to search for live streams"]
) -> str:
    """
    Find and list active live streams on YouTube.

    Args:
        channel_or_topic: Channel name or topic (e.g., "gaming", "news", "music")

    Returns:
        List of currently live streams with titles and channels

    Example:
        youtube_find_live_streams("tamil gaming")
    """
    try:
        logger.info(f"Searching for live streams: {channel_or_topic}")

        # Build live stream search URL
        encoded_query = quote_plus(f"{channel_or_topic} live")
        # EgJAAQ%3D%3D is the URL parameter for live filter
        youtube_live_url = f"https://www.youtube.com/results?search_query={encoded_query}&sp=EgJAAQ%253D%253D"

        logger.info(f"Opening YouTube live search: {youtube_live_url}")

        webbrowser.open(youtube_live_url)
        await asyncio.sleep(3)

        # Capture and analyze
        img = _cu.capture_screen()
        if img is None:
            return "Error: Could not capture screen"

        vision_prompt = f"""
Analyze this YouTube live stream search page.

List ALL visible live streams. For each stream, extract:
- Video title
- Channel name
- View count (if visible)
- Position on screen (top to bottom)

Return a JSON array:
[
    {{
        "title": "<video title>",
        "channel": "<channel name>",
        "viewers": "<viewer count or 'unknown'>",
        "position": <1 for top result, 2 for second, etc>
    }}
]

IMPORTANT: Return ONLY valid JSON array, no markdown.
"""

        response = _cu.analyze_screen(vision_prompt, img, temperature=0.1, backend="aws")

        import json
        if isinstance(response, str):
            response_text = response.strip()
            if response_text.startswith("```"):
                response_text = response_text.split("\n", 1)[1]
                response_text = response_text.rsplit("```", 1)[0]
            response = json.loads(response_text)

        if isinstance(response, dict) and "error" in response:
            return f"Vision analysis failed: {response['error']}"

        if not response or len(response) == 0:
            return f"No live streams found for: {channel_or_topic}"

        # Format results
        result = f"Found {len(response)} live stream(s) for '{channel_or_topic}':\n\n"
        for i, stream in enumerate(response, 1):
            title = stream.get("title", "Unknown")
            channel = stream.get("channel", "Unknown")
            viewers = stream.get("viewers", "unknown")
            result += f"{i}. {title}\n"
            result += f"   Channel: {channel}\n"
            result += f"   Viewers: {viewers}\n\n"

        return result

    except Exception as e:
        logger.error(f"Live stream search failed: {e}", exc_info=True)
        return f"Failed to search for live streams: {e}"


@function_tool()
async def play_youtube_quick(
    query: Annotated[str, "The song, video, or stream to play on YouTube"],
    context: RunContext = None
) -> str:
    """
    Search YouTube and immediately play the best matching video or live stream.

    Use this for any YouTube playback request — it is fast and reliable.
    Automatically detects live-stream queries and applies the YouTube Live filter.

    Examples:
    - "gojo vs sukuna"
    - "lofi hip hop radio"
    - "tamil gaming live"
    - "latest MrBeast video"
    """
    import urllib.request
    import urllib.parse
    import re

    logger.info(f"[YouTube Quick] Playing: {query}")

    try:
        # ── Detect live-stream intent ────────────────────────────────────────
        live_keywords = {"live", "stream", "streaming", "right now", "currently", "today"}
        is_live = any(kw in query.lower() for kw in live_keywords)

        encoded = urllib.parse.quote_plus(query)
        search_url = f"https://www.youtube.com/results?search_query={encoded}"
        if is_live:
            # YouTube Live filter (EgJAAQ==)
            search_url += "&sp=EgJAAQ%253D%253D"
            logger.info(f"[YouTube Quick] Live stream mode — {search_url}")
        else:
            logger.info(f"[YouTube Quick] Regular video mode — {search_url}")

        # ── Fetch search results ─────────────────────────────────────────────
        def _fetch(url: str) -> str:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            return urllib.request.urlopen(req).read().decode("utf-8")

        html = await asyncio.to_thread(_fetch, search_url)

        # deduplicate while preserving order
        seen: set = set()
        video_ids: list = []
        for vid in re.findall(r"watch\?v=([\w-]{11})", html):
            if vid not in seen:
                seen.add(vid)
                video_ids.append(vid)

        if not video_ids:
            return f"Could not find any YouTube videos for '{query}'."

        # ── Open with debug port + schedule Playwright CDP play ─────────────
        watch_url = _make_autoplay_url(f"https://www.youtube.com/watch?v={video_ids[0]}")
        _open_youtube_url(watch_url)
        asyncio.create_task(_click_play_after_load(delay=4.0))
        logger.info(f"[YouTube Quick] Opened + scheduled CDP play: {watch_url}")

        log_tool_execution(
            tool_name="play_youtube_quick",
            params={"query": query, "is_live": is_live},
            user_confirmed=False,
            result="success",
            session_id=getattr(context, "room", None) and context.room.name or "unknown"
        )

        mode = "live stream" if is_live else "video"
        return f"Now playing '{query}' ({mode}) on YouTube. URL: {watch_url}"

    except Exception as e:
        logger.error(f"[YouTube Quick] Failed: {e}", exc_info=True)
        return f"Failed to play '{query}' on YouTube: {e}"



@function_tool()
async def infinx_send_live_chat(
    context: RunContext,
    message: Annotated[str, "The message to send to the YouTube live chat"],
    url: Annotated[str, "The YouTube Livestream URL"] = "https://www.youtube.com/watch?v=3A4NvZEG54A"
) -> str:
    """
    Send a message directly to a YouTube live stream chat using the Infinx API.
    Use this when the user says 'send message to live chat' or 'say hi to bumblebabu'.
    """
    import os
    from infinx.youtube_api import YouTubeAPI
    from urllib.parse import urlparse, parse_qs
    
    try:
        secret_path = os.path.join(os.path.dirname(__file__), "..", "infinx", "credit", "client_secret_1040128938222-d84ubjl8q6orcr82qmlno9ipcdetujtu.apps.googleusercontent.com.json")
        api = YouTubeAPI(secret_path)
        api.authenticate()
        
        # Extract video ID
        parsed = urlparse(url)
        video_id = None
        if parsed.hostname == 'youtu.be':
            video_id = parsed.path[1:]
        elif parsed.hostname in ('www.youtube.com', 'youtube.com'):
            if parsed.path == '/watch':
                video_id = parse_qs(parsed.query).get('v', [None])[0]
                
        if not video_id:
            return "Could not extract video ID from URL."
            
        chat_id = api.get_live_chat_id(video_id)
        if not chat_id:
            return "Could not find active live chat for this video."
            
        success = api.post_message(message, chat_id)
        if success:
            return f"Successfully sent '{message}' to the live chat!"
        else:
            return "Failed to send message via API."
            
    except Exception as e:
        logger.error(f"Failed to send live chat message: {e}")
        return f"Error: {e}"

@function_tool()
async def infinx_start_watcher(
    context: RunContext,
    url: Annotated[str, "The YouTube Livestream URL to watch (or simply say 'bumblebabu')"] = "https://www.youtube.com/watch?v=LTc5wWL-8vk"
) -> str:
    """
    Start the autonomous Infinx YouTube watcher in the background.
    The watcher will listen to captions, solve puzzles, and chat automatically.
    """
    import subprocess
    import sys
    import os
    
    try:
        # Resolve 'bumblebabu' to the default URL
        if "bumble" in url.lower() or "babu" in url.lower() or "bumba" in url.lower() or url == "":
            url = "https://www.youtube.com/watch?v=3A4NvZEG54A"
            logger.info("Auto-resolved 'bumblebabu' to default target URL.")
            
        script_path = os.path.join(os.path.dirname(__file__), "..", "infinx", "run_infinx.py")
        # Launch in background
        subprocess.Popen(
            [sys.executable, "-m", "infinx.run_infinx", "--url", url],
            cwd=os.path.join(os.path.dirname(__file__), "..")
        )
        return f"Successfully launched the Infinx Watcher for {url} in the background!"
    except Exception as e:
        logger.error(f"Failed to start Infinx watcher: {e}")
        return f"Error starting watcher: {e}"

# Example usage and testing
if __name__ == "__main__":
    print("YouTube Automation Module")
    print("\nSupported queries:")
    print("- 'play recently repo tamil gaming live'")
    print("- 'play latest MrBeast video'")
    print("- 'play lofi hip hop radio live'")
    print("- 'find live gaming streams'")
    print("\nModule loaded successfully!")

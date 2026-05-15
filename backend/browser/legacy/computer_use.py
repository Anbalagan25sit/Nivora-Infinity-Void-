"""
computer_use.py — Vision-powered Computer Use Engine
Like Gemini Project Mariner / Claude Computer Use.

Capabilities:
  - Screenshot the current screen
  - Send to AWS Bedrock Nova (primary) or Gemini Flash (fallback) for analysis
  - Parse coordinates and action steps from JSON response
  - Execute: click, type, keypress, open_url, open_app, wait

Used by: computer_use_spotify, computer_use_youtube, music_intent_router tools.
"""

import os
import io
import json
import time
import base64
import logging
import re
import pyautogui
from google import genai
from google.genai import types as _genai_types
from PIL import Image

logger = logging.getLogger(__name__)

# ─── Vision Backend Selector ──────────────────────────────────────────────────
# Set to "aws" to use Bedrock Nova (default), or "gemini" for Gemini Flash
VISION_BACKEND = os.getenv("COMPUTER_USE_BACKEND", "aws")

# ─── AWS Bedrock Nova Vision ──────────────────────────────────────────────────

def analyze_screen_aws(prompt: str, img: Image.Image, temperature: float = 0.1) -> dict:
    """
    Send a screenshot to AWS Bedrock Nova Pro for vision analysis.
    Uses existing bedrock_client() from aws_config.py — no extra credentials needed.
    """
    import json as _json
    try:
        from aws_config import bedrock_client, bedrock_model
    except ImportError:
        raise RuntimeError("aws_config.py not found — make sure it's in the same directory.")

    client = bedrock_client()
    model_id = bedrock_model()  # amazon.nova-pro-v1:0 by default

    # Convert image to base64
    b64 = image_to_base64(img)

    full_prompt = (
        prompt
        + "\n\nIMPORTANT: Return ONLY a valid JSON object. "
        "No markdown, no code fences, no explanation. "
        "Just raw JSON starting with { and ending with }."
    )

    # Amazon Nova multimodal message structure
    body = _json.dumps({
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "image": {
                            "format": "png",
                            "source": {"bytes": b64}
                        }
                    },
                    {"text": full_prompt}
                ]
            }
        ],
        "inferenceConfig": {
            "temperature": temperature,
            "max_new_tokens": 2048,
        }
    })

    response = client.invoke_model(
        modelId=model_id,
        body=body,
        contentType="application/json",
        accept="application/json",
    )

    result = _json.loads(response["body"].read())
    # Nova response format: output.message.content[0].text
    raw = (
        result.get("output", {})
              .get("message", {})
              .get("content", [{}])[0]
              .get("text", "")
    ).strip()

    raw = re.sub(r"^```(?:json)?\s*", "", raw)
    raw = re.sub(r"\s*```$", "", raw)
    raw = raw.strip()

    try:
        return _json.loads(raw)
    except _json.JSONDecodeError:
        logger.warning(f"AWS Nova JSON parse failed: {raw[:200]}")
        return {"error": "Failed to parse AWS Nova response", "raw": raw}


# ─── Gemini Setup (fallback) ──────────────────────────────────────────────────
_genai_configured = False
_genai_client = None


def _get_genai_client():
    """Return a cached google.genai Client."""
    global _genai_configured, _genai_client
    if not _genai_configured:
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise RuntimeError("GOOGLE_API_KEY not set in .env")
        _genai_client = genai.Client(api_key=api_key)
        _genai_configured = True
    return _genai_client

# ─── Screen Capture ───────────────────────────────────────────────────────────

def capture_screen() -> Image.Image:
    """Take a screenshot of the full screen."""
    screenshot = pyautogui.screenshot()
    return screenshot


def image_to_base64(img: Image.Image) -> str:
    """Convert PIL image to base64 string for Gemini API."""
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode("utf-8")


def image_to_gemini_part(img: Image.Image) -> dict:
    """Convert PIL image to Gemini API inline_data dict."""
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return {
        "inline_data": {
            "mime_type": "image/png",
            "data": base64.b64encode(buf.getvalue()).decode("utf-8"),
        }
    }

# ─── Gemini Vision Analyzer ───────────────────────────────────────────────────

def analyze_screen(prompt: str, img: Image.Image | None = None, temperature: float = 0.1,
                   backend: str | None = None) -> dict:
    """
    Send a screenshot to a vision model for analysis.

    Args:
        prompt: The analysis prompt.
        img: PIL image. If None, captures screen automatically.
        temperature: Lower = more deterministic JSON output.
        backend: "aws" (Nova Pro) or "gemini" (Flash). Defaults to VISION_BACKEND env var.
    """
    if img is None:
        img = capture_screen()

    chosen = (backend or VISION_BACKEND).lower()

    if chosen == "aws":
        try:
            return analyze_screen_aws(prompt, img, temperature)
        except Exception as e:
            logger.warning(f"AWS backend failed, falling back to Gemini: {e}")
            chosen = "gemini"

    # Gemini fallback
    client = _get_genai_client()
    image_part = image_to_gemini_part(img)

    full_prompt = (
        prompt
        + "\n\nIMPORTANT: You MUST return ONLY a valid JSON object. "
        "No markdown code blocks, no explanation, no ```json tags. "
        "Just raw JSON starting with { and ending with }."
    )

    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=[
            {"role": "user", "parts": [
                {"text": full_prompt},
                image_part,
            ]}
        ],
        config=_genai_types.GenerateContentConfig(
            temperature=temperature,
            max_output_tokens=2048,
        ),
    )

    raw = response.text.strip()
    raw = re.sub(r"^```(?:json)?\s*", "", raw)
    raw = re.sub(r"\s*```$", "", raw)
    raw = raw.strip()

    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        logger.warning(f"Gemini JSON parse failed: {raw[:200]}")
        return {"error": "Failed to parse vision response", "raw": raw}

# ─── Action Executor ──────────────────────────────────────────────────────────

def execute_action(action: dict) -> str:
    """
    Execute a single action from the vision model's step list.

    Supported action types:
      - click       : pyautogui.click(x, y)
      - double_click: pyautogui.doubleClick(x, y)
      - type        : pyautogui.typewrite(value, interval=0.05)
      - keypress    : pyautogui.hotkey(*keys)
      - open_url    : webbrowser.open(url)
      - open_app    : os.startfile(app) or subprocess
      - wait        : time.sleep(ms / 1000)
      - scroll      : pyautogui.scroll(amount, x, y)
    """
    import webbrowser
    import subprocess

    action_type = (action.get("action") or action.get("type") or "").lower()
    coords = action.get("coordinates") or []
    value = action.get("value") or action.get("keyboard_shortcut") or ""
    wait_ms = action.get("wait_ms", 300)
    url = action.get("url", "")
    description = action.get("description", action_type)

    try:
        if action_type in ("click", "left_click"):
            if len(coords) >= 2:
                pyautogui.click(coords[0], coords[1])
                logger.info(f"Clicked ({coords[0]}, {coords[1]}) — {description}")

        elif action_type == "double_click":
            if len(coords) >= 2:
                pyautogui.doubleClick(coords[0], coords[1])

        elif action_type in ("type", "text"):
            pyautogui.typewrite(str(value), interval=0.04)
            logger.info(f"Typed: '{value}'")

        elif action_type in ("keypress", "hotkey", "keyboard_shortcut"):
            # value like "Ctrl+Right" or "Space"
            keys = [k.lower().strip() for k in str(value).replace("+", " ").split()]
            pyautogui.hotkey(*keys)
            logger.info(f"Keypress: {value}")

        elif action_type == "open_url":
            target = url or value
            webbrowser.open(target)
            logger.info(f"Opened URL: {target}")

        elif action_type == "open_app":
            try:
                os.startfile(value)
            except Exception:
                subprocess.Popen(value, shell=True)
            logger.info(f"Opened app: {value}")

        elif action_type == "scroll":
            amount = int(value) if value else 3
            if len(coords) >= 2:
                pyautogui.scroll(amount, x=coords[0], y=coords[1])
            else:
                pyautogui.scroll(amount)

        elif action_type == "wait":
            ms = wait_ms if wait_ms else (int(value) if value else 1000)
            time.sleep(ms / 1000)

        else:
            logger.warning(f"Unknown action type: {action_type}")
            return f"Unknown action: {action_type}"

        # Wait after action
        if wait_ms and action_type != "wait":
            time.sleep(wait_ms / 1000)

        return f"OK: {description}"

    except Exception as e:
        logger.error(f"execute_action failed ({action_type}): {e}")
        return f"ERROR: {e}"


def execute_steps(steps: list) -> list[str]:
    """Execute a list of steps from vision model output. Returns result log."""
    results = []
    for step in steps:
        result = execute_action(step)
        results.append(result)
        logger.info(f"Step {step.get('step', '?')}: {result}")
    return results

# ============================================================================
# VISION PROMPTS
# All 11 prompts for Spotify + YouTube computer use
# ============================================================================

# ─── SPOTIFY ─────────────────────────────────────────────────────────────────

PROMPT_SPOTIFY_ANALYZE = """
You are looking at the Spotify application or web player.
Identify and return JSON:
{
  "spotify_state": "open | closed | loading | playing | paused | searching",
  "current_song": {
    "title": "",
    "artist": "",
    "album": "",
    "duration": "",
    "current_time": ""
  },
  "visible_elements": {
    "search_bar": {"visible": true, "coordinates": [x, y]},
    "play_button": {"visible": true, "coordinates": [x, y]},
    "pause_button": {"visible": true, "coordinates": [x, y]},
    "next_button": {"visible": true, "coordinates": [x, y]},
    "prev_button": {"visible": true, "coordinates": [x, y]},
    "volume_slider": {"visible": true, "coordinates": [x, y]},
    "search_results": []
  },
  "is_playing": false
}
Return the real coordinates based on what you see on screen.
"""


def build_spotify_play_prompt(song_name: str, artist_name: str, spotify_state: str) -> str:
    return f"""
Task: Play "{song_name}" by "{artist_name}" on Spotify.
Current Spotify state: {spotify_state}

Generate exact steps. Rules:
- If Spotify is closed, open it first (open_url https://open.spotify.com)
- Use the search bar to find the song
- Click the correct search result
- Press play

Return JSON:
{{
  "steps": [
    {{
      "step": 1,
      "action": "open_url | click | type | keypress | wait",
      "description": "",
      "target_element": "",
      "coordinates": [x, y],
      "value": "",
      "wait_ms": 500
    }}
  ],
  "search_query": "{song_name} {artist_name}",
  "verbal_confirmation": "Playing {song_name} by {artist_name} on Spotify"
}}
"""


def build_spotify_select_prompt(search_query: str) -> str:
    return f"""
I searched for "{search_query}" on Spotify. Find the best matching song result.
Look at: song title match, artist name match, whether it's a song (not podcast/album/playlist), popularity.

Return JSON:
{{
  "best_match": {{
    "title": "",
    "artist": "",
    "coordinates": [x, y],
    "confidence": 0.0,
    "match_reason": ""
  }},
  "alternative_matches": [],
  "no_results_found": false
}}
"""


def build_spotify_control_prompt(command: str) -> str:
    return f"""
User Command: "{command}"
Commands can be: play, pause, next, previous, volume up, volume down, shuffle, repeat.

Map command to Spotify UI action. Return JSON:
{{
  "command_type": "",
  "action": {{
    "type": "click | keypress",
    "element": "",
    "coordinates": [x, y],
    "keyboard_shortcut": ""
  }},
  "verbal_response": ""
}}

Spotify keyboard shortcuts reference:
play_pause=Space, next=ctrl+right, previous=ctrl+left,
volume_up=ctrl+up, volume_down=ctrl+down, shuffle=ctrl+s, repeat=ctrl+r
"""


def build_spotify_nav_prompt(request: str) -> str:
    return f"""
User wants to: "{request}"
Examples: "play my liked songs", "open playlist chill vibes", "play Midnights by Taylor Swift"

Determine Spotify navigation. Return JSON:
{{
  "destination_type": "liked_songs | playlist | album | artist | podcast",
  "navigation_steps": [],
  "search_required": true,
  "search_query": "",
  "verbal_response": ""
}}
"""

# ─── YOUTUBE ─────────────────────────────────────────────────────────────────

PROMPT_YOUTUBE_ANALYZE = """
You are looking at YouTube in a browser.
Return JSON:
{
  "youtube_state": "homepage | search_results | video_playing | video_paused | loading",
  "current_video": {
    "title": "",
    "channel": "",
    "duration": "",
    "current_time": "",
    "views": ""
  },
  "visible_elements": {
    "search_bar": {"visible": true, "coordinates": [x, y]},
    "play_pause_button": {"visible": true, "coordinates": [x, y]},
    "fullscreen_button": {"visible": true, "coordinates": [x, y]},
    "volume_button": {"visible": true, "coordinates": [x, y]},
    "skip_ad_button": {"visible": false, "coordinates": [x, y]},
    "video_progress_bar": {"visible": true, "coordinates": [x, y]}
  },
  "ad_playing": false,
  "is_playing": false
}
Return the real coordinates based on what you see on screen.
"""


def build_youtube_play_prompt(video_title: str, extra_info: str = "") -> str:
    import urllib.parse
    encoded = urllib.parse.quote(f"{video_title} {extra_info}".strip())
    return f"""
Task: Play "{video_title}" on YouTube. Extra context: "{extra_info}"

Generate steps. Return JSON:
{{
  "steps": [
    {{
      "step": 1,
      "action": "open_url | click | type | keypress | wait",
      "description": "",
      "url": "https://youtube.com",
      "target_element": "",
      "coordinates": [x, y],
      "value": "",
      "wait_ms": 500
    }}
  ],
  "search_query": "{video_title} {extra_info}".strip(),
  "direct_url": "https://www.youtube.com/results?search_query={encoded}",
  "verbal_confirmation": "Searching YouTube for {video_title}"
}}
"""


def build_youtube_select_prompt(search_query: str) -> str:
    return f"""
I searched YouTube for: "{search_query}"
Find the best video. Consider: title relevance, channel credibility (verified/official), view count, duration.

Return JSON:
{{
  "best_match": {{
    "title": "",
    "channel": "",
    "views": "",
    "duration": "",
    "coordinates": [x, y],
    "confidence": 0.0,
    "selection_reason": ""
  }},
  "top_3_results": [],
  "official_video_found": false
}}
"""


PROMPT_YOUTUBE_AD = """
Check if an ad is playing and handle it. Return JSON:
{
  "ad_detected": false,
  "ad_type": "skippable | non_skippable | banner | none",
  "skip_button_visible": false,
  "skip_button_coordinates": [x, y],
  "skip_available_in_seconds": 0,
  "action": {
    "wait_seconds": 0,
    "then_click": [x, y],
    "close_banner": [x, y]
  },
  "verbal_response": "Skipping ad..."
}
"""


def build_youtube_control_prompt(command: str) -> str:
    return f"""
User Command: "{command}"
Commands: play, pause, fullscreen, mute, volume [level], skip 10 seconds, replay, enable captions, speed [0.5x-2x]

Map to YouTube controls. Return JSON:
{{
  "command_type": "",
  "action": {{
    "type": "click | keypress",
    "element": "",
    "coordinates": [x, y],
    "keyboard_shortcut": ""
  }},
  "verbal_response": ""
}}

YouTube shortcuts: play_pause=k, fullscreen=f, mute=m, seek+5=l, seek-5=j,
seek+10=right, seek-10=left, volume_up=up, volume_down=down, captions=c
"""

# ─── INTENT ROUTER ────────────────────────────────────────────────────────────

def build_intent_router_prompt(user_request: str) -> str:
    return f"""
User said: "{user_request}"

Determine what the user wants and route to the correct service.

Examples:
- "play Blinding Lights" → spotify (music)
- "play Blinding Lights music video" → youtube (video)
- "show me how to cook pasta" → youtube (tutorial)
- "play my workout playlist" → spotify (playlist)
- "play Drake's new album" → spotify (album)
- "watch MrBeast" → youtube (channel)

Return JSON:
{{
  "intent": "play_song | play_video | play_playlist | play_album | watch_channel | search_content",
  "service": "spotify | youtube",
  "query": {{
    "song_title": "",
    "artist": "",
    "video_title": "",
    "channel": "",
    "playlist": "",
    "album": "",
    "search_term": ""
  }},
  "confidence": 0.9,
  "verbal_response": "Sure, playing on spotify/youtube",
  "fallback_service": "youtube | spotify"
}}
"""

# ─── High-Level Orchestrators ─────────────────────────────────────────────────

async def run_spotify_flow(request: str) -> str:
    """
    Full Spotify computer-use flow:
    1. Capture screen → analyze state
    2. Generate steps → execute
    3. Wait for result
    4. Return verbal confirmation
    """
    logger.info(f"[ComputerUse] Spotify flow: {request}")

    # Step 1: Analyze current screen
    img = capture_screen()
    state = analyze_screen(PROMPT_SPOTIFY_ANALYZE, img)
    spotify_state = state.get("spotify_state", "unknown")
    logger.info(f"[ComputerUse] Spotify state: {spotify_state}")

    # Step 2: Parse song/artist from request (simple heuristic)
    parts = request.lower().split(" by ", 1)
    song = parts[0].strip()
    artist = parts[1].strip() if len(parts) > 1 else ""

    # Step 3: Generate play steps
    prompt = build_spotify_play_prompt(song, artist, spotify_state)
    img2 = capture_screen()
    plan = analyze_screen(prompt, img2)

    if "error" in plan:
        return f"Vision analysis failed: {plan.get('error')}"

    steps = plan.get("steps", [])
    verbal = plan.get("verbal_confirmation", f"Playing {song} on Spotify")

    # Step 4: Execute steps
    for step in steps:
        execute_action(step)

    # Step 5: After search results load, pick best match
    import asyncio
    await asyncio.sleep(2.5)  # wait for search results
    img3 = capture_screen()
    select_prompt = build_spotify_select_prompt(f"{song} {artist}")
    selection = analyze_screen(select_prompt, img3)

    best = selection.get("best_match", {})
    coords = best.get("coordinates", [])
    if coords and len(coords) >= 2 and not selection.get("no_results_found"):
        # Double-click to play
        execute_action({"action": "double_click", "coordinates": coords,
                        "description": f"Play {best.get('title', song)}", "wait_ms": 500})

    return verbal


async def run_youtube_flow(request: str) -> str:
    """
    Full YouTube computer-use flow:
    1. Open YouTube with direct search URL (fastest path)
    2. Capture screen → find best result
    3. Click it → handle ads → confirm playing
    """
    import urllib.parse
    import webbrowser
    import asyncio

    logger.info(f"[ComputerUse] YouTube flow: {request}")

    # Fast path: open YouTube search directly
    encoded = urllib.parse.quote(request)
    search_url = f"https://www.youtube.com/results?search_query={encoded}"
    webbrowser.open(search_url)
    await asyncio.sleep(3)  # wait for page load

    # Capture and find best result
    img = capture_screen()
    select_prompt = build_youtube_select_prompt(request)
    selection = analyze_screen(select_prompt, img)

    best = selection.get("best_match", {})
    coords = best.get("coordinates", [])
    title = best.get("title", request)

    if coords and len(coords) >= 2:
        execute_action({"action": "click", "coordinates": coords,
                        "description": f"Click {title}", "wait_ms": 500})
        await asyncio.sleep(3)  # wait for video to load

        # Handle ad if present
        img2 = capture_screen()
        ad_info = analyze_screen(PROMPT_YOUTUBE_AD, img2)
        if ad_info.get("ad_detected") and ad_info.get("skip_button_visible"):
            skip_coords = ad_info.get("skip_button_coordinates", [])
            wait_s = ad_info.get("skip_available_in_seconds", 5)
            if wait_s > 0:
                await asyncio.sleep(wait_s + 0.5)
            if skip_coords:
                execute_action({"action": "click", "coordinates": skip_coords,
                                "description": "Skip ad", "wait_ms": 500})

        return f"Playing '{title}' on YouTube."
    else:
        return f"Searched YouTube for '{request}' — couldn't find a matching video to click."


# ─── Screen-Vision Play / Stop Orchestrator ───────────────────────────────────

async def run_spotify_control_flow(command: str) -> str:
    """
    Screen-vision Spotify play/stop/next/previous orchestrator.

    Flow:
      1. Capture current screen
      2. Analyze via PROMPT_SPOTIFY_ANALYZE → know is_playing + button coords
      3. Map command to the correct action (click button OR keyboard shortcut)
      4. Execute action
      5. Return verbal confirmation

    Args:
        command: natural-language control word — "play", "stop", "pause",
                 "next", "previous", "volume up", "volume down", "shuffle", "repeat"
    """
    import asyncio as _asyncio

    logger.info(f"[ComputerUse] Control flow: '{command}'")

    # ── Step 1: Capture + Analyse current screen ──────────────────────────────
    img = capture_screen()
    state = analyze_screen(PROMPT_SPOTIFY_ANALYZE, img)

    if "error" in state:
        logger.warning(f"Screen analysis failed: {state.get('error')}")
        # Fall back to keyboard shortcut only
        state = {}

    is_playing: bool = state.get("is_playing", False)
    spotify_state: str = state.get("spotify_state", "unknown")
    elements: dict = state.get("visible_elements", {})

    logger.info(f"[ComputerUse] State — is_playing={is_playing}, spotify_state={spotify_state}")

    cmd = command.lower().strip()

    # ── Step 2: Decide action ─────────────────────────────────────────────────
    action_taken = ""

    if cmd in ("play", "resume"):
        if is_playing:
            return "Spotify is already playing."
        # Try clicking visible play button first
        play_btn = elements.get("play_button", {})
        coords = play_btn.get("coordinates", []) if isinstance(play_btn, dict) else []
        if coords and len(coords) >= 2 and play_btn.get("visible", False):
            execute_action({"action": "click", "coordinates": coords,
                            "description": "Click play button", "wait_ms": 400})
            action_taken = "Clicked play button"
        else:
            # Fall back to Space bar
            execute_action({"action": "keypress", "value": "Space",
                            "description": "Press Space to play", "wait_ms": 400})
            action_taken = "Pressed Space to play"

    elif cmd in ("stop", "pause"):
        if not is_playing:
            return "Spotify is already paused / stopped."
        pause_btn = elements.get("pause_button", {})
        coords = pause_btn.get("coordinates", []) if isinstance(pause_btn, dict) else []
        if coords and len(coords) >= 2 and pause_btn.get("visible", False):
            execute_action({"action": "click", "coordinates": coords,
                            "description": "Click pause button", "wait_ms": 400})
            action_taken = "Clicked pause button"
        else:
            execute_action({"action": "keypress", "value": "Space",
                            "description": "Press Space to pause", "wait_ms": 400})
            action_taken = "Pressed Space to pause"

    elif cmd in ("next", "next song", "skip"):
        next_btn = elements.get("next_button", {})
        coords = next_btn.get("coordinates", []) if isinstance(next_btn, dict) else []
        if coords and len(coords) >= 2 and next_btn.get("visible", False):
            execute_action({"action": "click", "coordinates": coords,
                            "description": "Click next button", "wait_ms": 400})
            action_taken = "Clicked next button"
        else:
            execute_action({"action": "keypress", "value": "ctrl+right",
                            "description": "Ctrl+Right for next", "wait_ms": 400})
            action_taken = "Pressed Ctrl+Right for next track"

    elif cmd in ("previous", "prev", "back", "previous song"):
        prev_btn = elements.get("prev_button", {})
        coords = prev_btn.get("coordinates", []) if isinstance(prev_btn, dict) else []
        if coords and len(coords) >= 2 and prev_btn.get("visible", False):
            execute_action({"action": "click", "coordinates": coords,
                            "description": "Click previous button", "wait_ms": 400})
            action_taken = "Clicked previous button"
        else:
            execute_action({"action": "keypress", "value": "ctrl+left",
                            "description": "Ctrl+Left for previous", "wait_ms": 400})
            action_taken = "Pressed Ctrl+Left for previous track"

    elif cmd in ("volume up", "louder"):
        execute_action({"action": "keypress", "value": "ctrl+up",
                        "description": "Volume up", "wait_ms": 300})
        action_taken = "Volume increased"

    elif cmd in ("volume down", "quieter", "lower volume"):
        execute_action({"action": "keypress", "value": "ctrl+down",
                        "description": "Volume down", "wait_ms": 300})
        action_taken = "Volume decreased"

    elif cmd in ("shuffle", "shuffle on", "shuffle off"):
        execute_action({"action": "keypress", "value": "ctrl+s",
                        "description": "Toggle shuffle", "wait_ms": 300})
        action_taken = "Toggled shuffle"

    elif cmd in ("repeat", "repeat on", "repeat off"):
        execute_action({"action": "keypress", "value": "ctrl+r",
                        "description": "Toggle repeat", "wait_ms": 300})
        action_taken = "Toggled repeat"

    else:
        # Unknown command — ask vision model to interpret it
        logger.info(f"[ComputerUse] Unknown command '{cmd}', delegating to vision model")
        img2 = capture_screen()
        control_prompt = build_spotify_control_prompt(command)
        plan = analyze_screen(control_prompt, img2)
        if "error" not in plan:
            action_dict = plan.get("action", {})
            if action_dict:
                execute_action({
                    "action": action_dict.get("type", "keypress"),
                    "coordinates": action_dict.get("coordinates", []),
                    "value": action_dict.get("keyboard_shortcut") or action_dict.get("element", ""),
                    "description": plan.get("verbal_response", command),
                    "wait_ms": 400,
                })
            return plan.get("verbal_response", f"Executed: {command}")
        return f"Could not interpret command: '{command}'"

    # ── Step 3: Verify with a fresh screenshot ────────────────────────────────
    await _asyncio.sleep(0.6)
    img_after = capture_screen()
    state_after = analyze_screen(PROMPT_SPOTIFY_ANALYZE, img_after)
    now_playing = state_after.get("is_playing", None)
    current_song = state_after.get("current_song", {})
    song_title = current_song.get("title", "") if isinstance(current_song, dict) else ""
    song_artist = current_song.get("artist", "") if isinstance(current_song, dict) else ""

    if song_title:
        song_info = f" — {song_title}" + (f" by {song_artist}" if song_artist else "")
    else:
        song_info = ""

    if cmd in ("stop", "pause"):
        return f"Paused{song_info}. ({action_taken})"
    elif cmd in ("play", "resume"):
        return f"Playing{song_info}. ({action_taken})"
    else:
        return f"{action_taken}{song_info}."


def screen_play_stop(command: str = "play") -> str:
    """
    Synchronous convenience wrapper around run_spotify_control_flow().
    Use this for non-async callers.

    Args:
        command: "play", "stop", "pause", "next", "previous", etc.
    """
    import asyncio as _asyncio
    try:
        loop = _asyncio.get_event_loop()
        if loop.is_running():
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as pool:
                future = pool.submit(_asyncio.run, run_spotify_control_flow(command))
                return future.result()
        else:
            return loop.run_until_complete(run_spotify_control_flow(command))
    except RuntimeError:
        return _asyncio.run(run_spotify_control_flow(command))


# ─── CLI Self-Test ────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import sys
    import asyncio as _asyncio
    from pathlib import Path
    from dotenv import load_dotenv

    # Force UTF-8 console output on Windows
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    load_dotenv(Path(__file__).parent / ".env", override=True)

    SEP = "=" * 65

    def hdr(title: str):
        print(f"\n{SEP}")
        print(f"  {title}")
        print(SEP)

    hdr("computer_use.py — Screen Play/Stop Test")

    # ── Parse CLI argument ────────────────────────────────────────────────────
    # Usage:  python computer_use.py [play|stop|next|previous|analyze]
    cmd_arg = (sys.argv[1] if len(sys.argv) > 1 else "analyze").lower().strip()
    print(f"  Command : {cmd_arg}")
    print(f"  Backend : {VISION_BACKEND}")

    # ── Import checks ─────────────────────────────────────────────────────────
    try:
        import pyautogui  # noqa
        print("[OK] pyautogui available")
    except ImportError:
        print("[FAIL] pyautogui not installed — run: pip install pyautogui")
        sys.exit(1)

    # ── TEST A: analyze — screenshot + full Spotify state dump ────────────────
    if cmd_arg == "analyze":
        hdr("TEST A — Capture Screen & Analyze Spotify State")
        print("  Taking screenshot...")
        img = capture_screen()
        print(f"  Screenshot captured in memory  ({img.width}×{img.height})")
        # Save only if disk space available
        try:
            out = Path(__file__).parent / "_cu_spotify_state.png"
            img.save(str(out))
            print(f"  Screenshot saved: {out.name}")
        except OSError as _e:
            print(f"  [WARN] Could not save screenshot: {_e} — continuing without saving")

        print(f"  Sending to {VISION_BACKEND.upper()} vision model...")
        import time
        t0 = time.time()
        state = analyze_screen(PROMPT_SPOTIFY_ANALYZE, img)
        elapsed = time.time() - t0
        print(f"  Response received in {elapsed:.1f}s")

        if "error" in state:
            print(f"\n  [WARN] Vision error: {state.get('error')}")
            print(f"  Raw: {state.get('raw', '')[:400]}")
        else:
            print(f"\n  spotify_state : {state.get('spotify_state', '?')}")
            print(f"  is_playing    : {state.get('is_playing', '?')}")
            song = state.get("current_song", {})
            if isinstance(song, dict) and song.get("title"):
                print(f"  current_song  : {song.get('title')} — {song.get('artist', '')}")
            elems = state.get("visible_elements", {})
            for btn in ("play_button", "pause_button", "next_button", "prev_button"):
                info = elems.get(btn, {})
                if isinstance(info, dict):
                    visible = info.get("visible", False)
                    coords = info.get("coordinates", [])
                    print(f"  {btn:<20}: visible={visible}  coords={coords}")
        print(f"\n  Full JSON:\n  {state}")

    # ── TEST B: play / stop / next / previous ─────────────────────────────────
    elif cmd_arg in ("play", "stop", "pause", "next", "previous", "prev",
                     "volume up", "volume down", "shuffle", "repeat"):
        hdr(f"TEST B — Screen-Vision Control: '{cmd_arg}'")
        print("  Make sure Spotify is open on screen before continuing.")
        print("  Running control flow in 2 seconds...")
        import time
        time.sleep(2)

        result = _asyncio.run(run_spotify_control_flow(cmd_arg))
        print(f"\n  Result: {result}")

    # ── TEST C: full play-song flow ────────────────────────────────────────────
    elif cmd_arg == "play_song":
        query = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else "Blinding Lights The Weeknd"
        hdr(f"TEST C — Full Spotify Play Flow: '{query}'")
        print("  Make sure Spotify is open on screen.")
        import time
        time.sleep(2)
        result = _asyncio.run(run_spotify_flow(query))
        print(f"\n  Result: {result}")

    else:
        print(f"\n  Unknown test command: '{cmd_arg}'")
        print("  Usage: python computer_use.py [analyze | play | stop | next | previous | play_song <query>]")
        sys.exit(1)

    print(f"\n{SEP}")
    print("  Test complete.")
    print(SEP)

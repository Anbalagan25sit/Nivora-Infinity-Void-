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


@function_tool()
async def youtube_search_and_play(
    context: RunContext,
    query: Annotated[str, "Natural language search query (e.g., 'recently repo tamil gaming live', 'latest MrBeast video')"],
    prefer_live: Annotated[bool, "Prefer live streams over regular videos"] = False
) -> str:
    """
    Search YouTube and automatically play a video or live stream.

    This tool:
    1. Opens YouTube in the default browser
    2. Searches for the query
    3. Uses vision AI to identify the best matching result
    4. Automatically clicks and starts playback
    5. Handles live streams, recent uploads, and regular videos

    Args:
        query: Natural language search query
        prefer_live: If True, prioritizes live streams in results

    Example queries:
    - "recently repo tamil gaming live"
    - "latest Pewdiepie video"
    - "lofi hip hop radio live stream"
    - "MrBeast newest upload"

    Returns:
        Status message with video title and URL
    """
    try:
        logger.info(f"YouTube search and play: {query}, prefer_live={prefer_live}")

        # Step 1: Build search URL
        # Clean up the query - "live" often means the channel name, not a live stream filter
        search_query = query

        # Only add live filter if user EXPLICITLY wants live streams (prefer_live=True)
        # Don't add filter just because "live" is in the query - it's often part of channel/video names
        add_live_filter = prefer_live and "live" not in query.lower()  # Only filter if prefer_live is explicit

        # Detect keywords that suggest temporal filtering
        if any(word in query.lower() for word in ["recent", "latest", "new", "newest", "today"]):
            # YouTube will naturally prioritize recent uploads
            pass

        encoded_query = quote_plus(search_query)
        youtube_search_url = f"https://www.youtube.com/results?search_query={encoded_query}"

        # Only add live filter if explicitly requested AND "live" is not in the query
        # This prevents filtering out regular videos when user says "Tamil Gaming live" (channel name)
        if add_live_filter:
            youtube_search_url += "&sp=EgJAAQ%253D%253D"  # YouTube's live filter parameter

        logger.info(f"Opening YouTube search: {youtube_search_url}")

        # Step 2: Open YouTube in browser
        webbrowser.open(youtube_search_url)
        await asyncio.sleep(3)  # Wait for page to load

        # Step 3: Take screenshot and analyze with vision AI
        img = _cu.capture_screen()
        if img is None:
            return "Error: Could not capture screen after opening YouTube"

        # Step 4: Build vision prompt to find the best video
        vision_prompt = f"""
Analyze this YouTube search results page for the query: "{query}"

Identify the BEST matching video result. Priority order:
1. Videos from the EXACT channel mentioned in the query (e.g., "Tamil Gaming" channel)
2. Most recent/latest video from that channel
3. Videos with high view counts
4. Live streams ONLY if the query specifically asks for "live stream" or "currently live"

IMPORTANT: "live" in channel names like "Tamil Gaming live" or "Supersus live" does NOT mean live stream - it's just part of the name.

Return a JSON object:
{{
    "found": true/false,
    "video_title": "<title of the video>",
    "channel_name": "<channel name>",
    "is_live": true/false,
    "thumbnail_x": <x coordinate of video thumbnail>,
    "thumbnail_y": <y coordinate of video thumbnail>,
    "confidence": "high/medium/low"
}}

The thumbnail coordinates should be the CENTER of the video thumbnail (clickable area).

IMPORTANT: Return ONLY valid JSON, no markdown or other text.
"""

        logger.info("Analyzing YouTube search results with vision AI...")

        # Use AWS backend explicitly
        try:
            response = _cu.analyze_screen(vision_prompt, img, temperature=0.1, backend="aws")
        except Exception as e:
            logger.error(f"Vision analysis failed: {e}")
            return f"Vision AI error: {e}. Make sure AWS Bedrock is configured in your .env file."

        # Step 5: Parse vision response
        import json
        if isinstance(response, dict) and "error" in response:
            return f"Vision analysis failed: {response['error']}"

        if isinstance(response, str):
            # Strip markdown code fences if present
            response_text = response.strip()
            if response_text.startswith("```"):
                response_text = response_text.split("\n", 1)[1]
                response_text = response_text.rsplit("```", 1)[0]
            response = json.loads(response_text)

        if not response.get("found", False):
            return f"Could not find a matching video for: {query}"

        video_title = response.get("video_title", "Unknown")
        channel_name = response.get("channel_name", "Unknown")
        is_live = response.get("is_live", False)
        thumbnail_x = int(response.get("thumbnail_x", 0))
        thumbnail_y = int(response.get("thumbnail_y", 0))
        confidence = response.get("confidence", "unknown")

        logger.info(f"Found video: {video_title} by {channel_name} (live={is_live})")

        # Step 6: Click on the video thumbnail
        logger.info(f"Clicking video at ({thumbnail_x}, {thumbnail_y})")
        pyautogui.click(thumbnail_x, thumbnail_y)

        await asyncio.sleep(3)  # Wait for video page to load

        # Step 6.5: Handle YouTube Ads - Skip if present
        for ad_attempt in range(3):  # Try up to 3 times to skip ads
            img_ad_check = _cu.capture_screen()
            ad_check_prompt = """
Analyze this YouTube page. Check for YouTube ADS:

Look for:
1. "Skip Ad" or "Skip Ads" button (usually bottom right of video)
2. "Ad" label on the video
3. Yellow ad progress bar at bottom of video
4. "Video will play after ad" message
5. Countdown timer like "You can skip ad in 5..."

Return JSON:
{
    "has_ad": true/false,
    "skip_button_visible": true/false,
    "skip_button_x": <x coordinate of skip button center, or 0>,
    "skip_button_y": <y coordinate of skip button center, or 0>,
    "ad_type": "skippable/non-skippable/none"
}

IMPORTANT: Return ONLY valid JSON.
"""
            ad_response = _cu.analyze_screen(ad_check_prompt, img_ad_check, temperature=0.1, backend="aws")
            if isinstance(ad_response, str):
                ad_response = ad_response.strip()
                if ad_response.startswith("```"):
                    ad_response = ad_response.split("\n", 1)[1]
                    ad_response = ad_response.rsplit("```", 1)[0]
                ad_response = json.loads(ad_response)

            has_ad = ad_response.get("has_ad", False)
            skip_visible = ad_response.get("skip_button_visible", False)

            if not has_ad:
                logger.info("No ad detected, proceeding to video")
                break

            if skip_visible:
                skip_x = int(ad_response.get("skip_button_x", 0))
                skip_y = int(ad_response.get("skip_button_y", 0))
                if skip_x > 0 and skip_y > 0:
                    logger.info(f"Skipping ad at ({skip_x}, {skip_y})")
                    pyautogui.click(skip_x, skip_y)
                    await asyncio.sleep(1)
            else:
                # Non-skippable ad - wait a bit
                logger.info("Non-skippable ad detected, waiting...")
                await asyncio.sleep(5)

        # Step 7: Verify video started playing
        img_after = _cu.capture_screen()
        verify_prompt = """
Is a YouTube video currently playing on this screen?
Look for:
- YouTube video player
- Play/pause button visible
- Video title at the top
- NOT an ad playing

Return JSON:
{
    "video_playing": true/false,
    "video_title_visible": "<title if visible, else null>",
    "is_ad": false
}

IMPORTANT: Return ONLY valid JSON.
"""

        verify_response = _cu.analyze_screen(verify_prompt, img_after, temperature=0.1, backend="aws")
        if isinstance(verify_response, str):
            verify_response = verify_response.strip()
            if verify_response.startswith("```"):
                verify_response = verify_response.split("\n", 1)[1]
                verify_response = verify_response.rsplit("```", 1)[0]
            verify_response = json.loads(verify_response)

        is_playing = verify_response.get("video_playing", False)

        # Log to audit
        log_tool_execution(
            tool_name="youtube_search_and_play",
            params={"query": query, "prefer_live": prefer_live},
            user_confirmed=False,
            result="success" if is_playing else "partial",
            session_id=getattr(context, 'room', None) and context.room.name or "unknown"
        )

        # Build result message
        live_indicator = " 🔴 LIVE" if is_live else ""
        result = f"Now playing: '{video_title}' by {channel_name}{live_indicator}\n"
        result += f"Confidence: {confidence}\n"

        if not is_playing:
            result += "\nNote: Video page opened but couldn't verify playback started. You may need to click play manually."

        return result

    except Exception as e:
        logger.error(f"YouTube search and play failed: {e}", exc_info=True)
        return f"Failed to play YouTube video: {e}"


@function_tool()
async def youtube_play_by_url(
    context: RunContext,
    url: Annotated[str, "YouTube video or live stream URL"]
) -> str:
    """
    Play a specific YouTube video by URL.

    Args:
        url: Full YouTube URL (e.g., https://www.youtube.com/watch?v=...)

    Example:
        youtube_play_by_url("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
    """
    try:
        logger.info(f"Opening YouTube URL: {url}")

        webbrowser.open(url)
        await asyncio.sleep(2)

        log_tool_execution(
            tool_name="youtube_play_by_url",
            params={"url": url},
            user_confirmed=False,
            result="success",
            session_id=getattr(context, 'room', None) and context.room.name or "unknown"
        )

        return f"Opened YouTube video: {url}"

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


# Convenience function for quick playback
async def play_youtube_quick(query: str, context: RunContext) -> str:
    """
    Quick helper to search and play YouTube videos.
    Automatically detects if query is for live content.
    """
    is_live_query = any(word in query.lower() for word in ["live", "stream", "streaming"])
    return await youtube_search_and_play(context, query, prefer_live=is_live_query)


# Example usage and testing
if __name__ == "__main__":
    print("YouTube Automation Module")
    print("\nSupported queries:")
    print("- 'play recently repo tamil gaming live'")
    print("- 'play latest MrBeast video'")
    print("- 'play lofi hip hop radio live'")
    print("- 'find live gaming streams'")
    print("\nModule loaded successfully!")

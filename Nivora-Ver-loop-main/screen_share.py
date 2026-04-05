"""
screen_share.py — LiveKit screen-share frame buffer

Stores the latest video frame received from a participant's screen-share
track so that agent tools can analyse it via the existing vision pipeline
(analyze_screen_aws / analyze_screen_gemini in computer_use.py).

Usage in agent.py:
    from screen_share import set_latest_frame, get_latest_frame, start_frame_capture

Usage in tools.py:
    from screen_share import get_latest_frame
"""

from __future__ import annotations

import asyncio
import logging
from typing import Optional

from PIL import Image

logger = logging.getLogger(__name__)

# ─── Module-level frame buffer ─────────────────────────────────────────────────
_latest_frame: Optional[Image.Image] = None


def set_latest_frame(img: Image.Image) -> None:
    """Store the most recently received screen-share frame."""
    global _latest_frame
    _latest_frame = img


def get_latest_frame() -> Optional[Image.Image]:
    """Return the most recently received screen-share frame, or None."""
    return _latest_frame


async def start_frame_capture(track) -> None:  # track: livekit.rtc.RemoteVideoTrack
    """
    Async task: iterate over frames from a LiveKit video track and store
    each one in the module-level buffer.  Call this with asyncio.ensure_future().
    """
    try:
        from livekit import rtc  # local import to avoid hard dep at module level

        video_stream = rtc.VideoStream(track, format=rtc.VideoBufferType.RGBA)
        logger.info("Screen-share frame capture started.")

        async for event in video_stream:
            frame = event.frame
            try:
                img = Image.frombytes(
                    "RGBA",
                    (frame.width, frame.height),
                    bytes(frame.data),
                ).convert("RGB")
                set_latest_frame(img)
            except Exception as conv_err:
                logger.debug(f"Frame conversion error: {conv_err}")

        logger.info("Screen-share video stream ended.")
    except Exception as e:
        logger.warning(f"start_frame_capture error: {e}")

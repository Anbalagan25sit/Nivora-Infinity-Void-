"""
Cookie Manager - Saves and restores browser cookies for persistent login
"""

import json
import os
import logging
from pathlib import Path
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

# Cookie storage path
COOKIE_FILE = Path.home() / ".nivora_cookies" / "ebox_cookies.json"
COOKIE_FILE.parent.mkdir(parents=True, exist_ok=True)


async def save_cookies(page) -> bool:
    """
    Save cookies from current browser session.

    Args:
        page: Playwright page object

    Returns:
        bool: True if cookies saved successfully
    """
    try:
        # Get cookies from current page
        cookies = await page.context.cookies()

        # Save to file
        with open(COOKIE_FILE, 'w') as f:
            json.dump(cookies, f, indent=2)

        logger.info(f"✅ Saved {len(cookies)} cookies to {COOKIE_FILE}")
        return True

    except Exception as e:
        logger.error(f"Failed to save cookies: {e}")
        return False


async def load_cookies(page) -> bool:
    """
    Load previously saved cookies into browser session.

    Args:
        page: Playwright page object

    Returns:
        bool: True if cookies loaded successfully
    """
    try:
        # Check if cookie file exists
        if not COOKIE_FILE.exists():
            logger.info("No saved cookies found - first time login needed")
            return False

        # Load cookies from file
        with open(COOKIE_FILE, 'r') as f:
            cookies = json.load(f)

        if not cookies:
            logger.info("Cookie file is empty")
            return False

        # Add cookies to browser context
        await page.context.add_cookies(cookies)

        logger.info(f"✅ Loaded {len(cookies)} cookies from {COOKIE_FILE}")
        return True

    except Exception as e:
        logger.error(f"Failed to load cookies: {e}")
        return False


async def clear_cookies() -> bool:
    """
    Clear saved cookies (force re-login next time).

    Returns:
        bool: True if cookies cleared successfully
    """
    try:
        if COOKIE_FILE.exists():
            COOKIE_FILE.unlink()
            logger.info("✅ Cleared saved cookies")
            return True
        else:
            logger.info("No cookies to clear")
            return True

    except Exception as e:
        logger.error(f"Failed to clear cookies: {e}")
        return False


def has_saved_cookies() -> bool:
    """
    Check if there are saved cookies available.

    Returns:
        bool: True if saved cookies exist
    """
    return COOKIE_FILE.exists() and COOKIE_FILE.stat().st_size > 0

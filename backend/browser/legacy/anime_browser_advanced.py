"""
Advanced browser automation script for anime streaming.
Features: Auto-play, auto-fullscreen, ad handling, episode navigation.
"""

import asyncio
from playwright.async_api import async_playwright, Page
import sys
import os

# Fix Unicode encoding issues on Windows console
if sys.platform == 'win32':
    os.environ['PYTHONIOENCODING'] = 'utf-8'



 def close_popups_and_ads(page: Page):
    """
    Attempts to close common popups, ads, and overlays.
    """
    print("[*] Checking for ads and popups...")

    # Common close button selectors
    close_selectors = [
        'button[aria-label*="Close"]',
        'button[class*="close"]',
        'div[class*="close"]',
        'a[class*="close"]',
        '.modal-close',
        '.popup-close',
        '[id*="close"]',
        'button:has-text("Close")',
        'button:has-text("X")',
        'div[role="button"]:has-text("×")',
    ]

    closed_count = 0
    for selector in close_selectors:
        try:
            elements = await page.query_selector_all(selector)
            for element in elements:
                if await element.is_visible():
                    await element.click(timeout=500)
                    closed_count += 1
                    await asyncio.sleep(0.5)
        except Exception:
            pass

    if closed_count > 0:
        print(f"[+] Closed {closed_count} popup(s)/ad(s)")

    return closed_count


async def try_autoplay(page: Page):
    """
    Attempts to find and click the play button.
    """
    print("[*] Looking for play button...")

    # Common play button selectors for anime sites
    play_selectors = [
        'button[aria-label*="Play"]',
        'button[class*="play"]',
        'button[title*="Play"]',
        '.vjs-big-play-button',  # Video.js player
        '.plyr__control--overlaid',  # Plyr player
        'button:has-text("Play")',
        '[aria-label="Play"]',
        'button.ytp-large-play-button',  # YouTube player
        'iframe',  # Will try to click center of iframe
    ]

    for selector in play_selectors:
        try:
            if selector == 'iframe':
                # Try clicking center of first iframe
                iframe = await page.query_selector(selector)
                if iframe:
                    box = await iframe.bounding_box()
                    if box:
                        # Click center of iframe
                        await page.mouse.click(
                            box['x'] + box['width'] / 2,
                            box['y'] + box['height'] / 2
                        )
                        print("[+] Clicked center of video player")
                        await asyncio.sleep(1)
                        return True
            else:
                button = await page.query_selector(selector)
                if button and await button.is_visible():
                    await button.click(timeout=2000)
                    print("[+] Play button clicked!")
                    await asyncio.sleep(1)
                    return True
        except Exception as e:
            continue

    # Fallback: try clicking center of page (where video usually is)
    try:
        viewport = page.viewport_size
        if viewport:
            await page.mouse.click(viewport['width'] / 2, viewport['height'] / 2)
            print("[+] Clicked center of page to start video")
            await asyncio.sleep(1)
            return True
    except Exception:
        pass

    print("[-] Could not find play button")
    return False


async def try_fullscreen(page: Page):
    """
    Attempts to enable fullscreen mode.
    """
    print("[*] Attempting fullscreen...")

    # Try JavaScript fullscreen API
    try:
        await page.evaluate("""
            () => {
                const video = document.querySelector('video');
                if (video) {
                    if (video.requestFullscreen) {
                        video.requestFullscreen();
                    } else if (video.webkitRequestFullscreen) {
                        video.webkitRequestFullscreen();
                    } else if (video.mozRequestFullScreen) {
                        video.mozRequestFullScreen();
                    }
                    return true;
                }
                return false;
            }
        """)
        print("[+] Fullscreen enabled via video element")
        return True
    except Exception:
        pass

    # Try fullscreen button selectors
    fullscreen_selectors = [
        'button[aria-label*="Fullscreen"]',
        'button[class*="fullscreen"]',
        'button[title*="Fullscreen"]',
        '.vjs-fullscreen-control',
        '.plyr__control[data-plyr="fullscreen"]',
        'button:has-text("Fullscreen")',
    ]

    for selector in fullscreen_selectors:
        try:
            button = await page.query_selector(selector)
            if button and await button.is_visible():
                await button.click(timeout=2000)
                print("[+] Fullscreen button clicked!")
                return True
        except Exception:
            continue

    # Try pressing 'f' key (common fullscreen hotkey)
    try:
        await page.keyboard.press('f')
        print("[+] Pressed 'f' for fullscreen")
        return True
    except Exception:
        pass

    print("[-] Could not enable fullscreen")
    return False


async def try_next_episode(page: Page):
    """
    Attempts to navigate to the next episode.
    """
    print("[*] Looking for next episode button...")

    next_selectors = [
        'a:has-text("Next Episode")',
        'button:has-text("Next")',
        'a[title*="Next"]',
        'a[class*="next"]',
        '.episode-next',
        'a:has-text("Next")',
    ]

    for selector in next_selectors:
        try:
            button = await page.query_selector(selector)
            if button and await button.is_visible():
                await button.click(timeout=2000)
                print("[+] Next episode button clicked!")
                await asyncio.sleep(3)  # Wait for page to load
                return True
        except Exception:
            continue

    print("[-] Could not find next episode button")
    return False


async def monitor_video_progress(page: Page, auto_next: bool = False):
    """
    Monitors video progress and optionally auto-advances to next episode.
    """
    try:
        # Check if video is near the end (last 30 seconds)
        is_ending = await page.evaluate("""
            () => {
                const video = document.querySelector('video');
                if (video && !isNaN(video.duration) && !isNaN(video.currentTime)) {
                    const timeLeft = video.duration - video.currentTime;
                    return timeLeft < 30 && timeLeft > 0;
                }
                return false;
            }
        """)

        if is_ending and auto_next:
            print("[*] Video ending soon, attempting to go to next episode...")
            await try_next_episode(page)
            # Re-setup after navigation
            await asyncio.sleep(3)
            await close_popups_and_ads(page)
            await try_autoplay(page)
            if await should_fullscreen():
                await try_fullscreen(page)
    except Exception:
        pass


async def should_fullscreen():
    """Check if fullscreen was requested in args."""
    return '--fullscreen' in sys.argv or '-f' in sys.argv


async def should_auto_next():
    """Check if auto-next episode was requested in args."""
    return '--auto-next' in sys.argv or '-n' in sys.argv


async def open_anime_page_advanced(url: str, wait_time: int = 300):
    """
    Opens an anime page with advanced automation features.

    Args:
        url: The URL to navigate to
        wait_time: How long to keep the browser open (seconds)
    """
    print(f"[*] Starting advanced browser automation...")
    print(f"[*] Target URL: {url}")
    print(f"[*] Features: Auto-play, Ad-blocking, " +
          ("Fullscreen, " if await should_fullscreen() else "") +
          ("Auto-next episode" if await should_auto_next() else ""))

    async with async_playwright() as p:
        # Launch browser
        print("[*] Launching browser...")
        browser = await p.chromium.launch(
            headless=False,
            args=[
                '--start-maximized',
                '--disable-blink-features=AutomationControlled',
                '--disable-popup-blocking',  # We'll handle popups ourselves
            ]
        )

        # Create context with ad-blocking
        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            # Block common ad domains
            ignore_https_errors=True,
        )

        # Block ads at network level
        await context.route("**/*", lambda route: (
            route.abort() if any(ad in route.request.url for ad in [
                'doubleclick.net', 'googlesyndication.com', 'adserver',
                'ads.', '/ads/', 'banner', 'popup'
            ]) else route.continue_()
        ))

        page = await context.new_page()

        try:
            # Navigate to URL
            print(f"[*] Navigating to {url}...")
            await page.goto(url, wait_until='domcontentloaded', timeout=30000)
            print("[+] Page loaded successfully!")

            # Wait for initial content to load
            await asyncio.sleep(3)

            # Close any popups/ads
            await close_popups_and_ads(page)
            await asyncio.sleep(1)

            # Try to autoplay
            played = await try_autoplay(page)
            await asyncio.sleep(2)

            # Close any ads that appeared after clicking play
            await close_popups_and_ads(page)

            # Try fullscreen if requested
            if await should_fullscreen():
                await asyncio.sleep(1)
                await try_fullscreen(page)

            print(f"[*] Browser will stay open for {wait_time} seconds...")
            print("[*] Monitoring video progress...")
            print("[!] Press Ctrl+C to close the browser early.")

            # Monitor video progress
            auto_next = await should_auto_next()
            end_time = asyncio.get_event_loop().time() + wait_time

            while asyncio.get_event_loop().time() < end_time:
                # Check for video progress every 10 seconds
                await asyncio.sleep(10)
                await monitor_video_progress(page, auto_next)

                # Periodically close any new popups
                if asyncio.get_event_loop().time() % 30 < 10:  # Every 30 seconds
                    await close_popups_and_ads(page)

        except asyncio.CancelledError:
            print("\n[!] Browser automation cancelled by user.")
        except Exception as e:
            print(f"[!] Error occurred: {e}")
        finally:
            print("[*] Closing browser...")
            await browser.close()
            print("[+] Browser closed.")


async def main():
    """Main entry point for the script."""
    # Default URL
    default_url = "https://9anime.org.lv/death-note-episode-19/"

    # Parse arguments
    args = [arg for arg in sys.argv[1:] if not arg.startswith('-')]

    # Get URL
    if len(args) > 0:
        url = args[0]
    else:
        url = default_url

    # Get wait time
    wait_time = 300  # 5 minutes default
    if len(args) > 1:
        try:
            wait_time = int(args[1])
        except ValueError:
            print("[!] Invalid wait time, using default (300 seconds)")

    # Print help if requested
    if '--help' in sys.argv or '-h' in sys.argv:
        print("""
Advanced Anime Browser Automation
Usage: python anime_browser_advanced.py [URL] [TIME] [OPTIONS]

Arguments:
  URL                 Anime page URL (default: Death Note Episode 19)
  TIME                How long to keep browser open in seconds (default: 300)

Options:
  -f, --fullscreen    Enable auto-fullscreen
  -n, --auto-next     Auto-advance to next episode when current ends
  -h, --help          Show this help message

Examples:
  python anime_browser_advanced.py
  python anime_browser_advanced.py "https://9anime.org.lv/naruto-episode-1/" 1800
  python anime_browser_advanced.py --fullscreen --auto-next
  python anime_browser_advanced.py "https://9anime.org.lv/one-piece/" 3600 -f -n
        """)
        return

    await open_anime_page_advanced(url, wait_time)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n[!] Script terminated by user.")

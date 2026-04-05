"""
Browser automation script for navigating to anime websites.
Uses Playwright to control a Chrome/Edge browser.
"""

import asyncio
from playwright.async_api import async_playwright
import sys
import os

# Fix Unicode encoding issues on Windows console
if sys.platform == 'win32':
    os.environ['PYTHONIOENCODING'] = 'utf-8'


async def open_anime_page(url: str, wait_time: int = 300):
    """
    Opens an anime page in a browser and keeps it open.

    Args:
        url: The URL to navigate to
        wait_time: How long to keep the browser open (seconds), default 5 minutes
    """
    print(f"[*] Starting browser automation...")
    print(f"[*] Target URL: {url}")

    async with async_playwright() as p:
        # Launch browser in non-headless mode (visible window)
        print("[*] Launching browser...")
        browser = await p.chromium.launch(
            headless=False,  # Show the browser window
            args=[
                '--start-maximized',  # Start maximized
                '--disable-blink-features=AutomationControlled',  # Hide automation
            ]
        )

        # Create a new browser context with a realistic viewport
        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )

        # Create a new page
        page = await context.new_page()

        try:
            # Navigate to the URL
            print(f"[*] Navigating to {url}...")
            await page.goto(url, wait_until='domcontentloaded', timeout=30000)
            print("[+] Page loaded successfully!")

            # Wait a bit for any dynamic content to load
            await asyncio.sleep(3)

            print(f"[*] Browser will stay open for {wait_time} seconds...")
            print("[*] You can manually interact with the page now.")
            print("[!] Press Ctrl+C to close the browser early.")

            # Keep the browser open for the specified time
            await asyncio.sleep(wait_time)

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

    # Check if URL was provided as command line argument
    if len(sys.argv) > 1:
        url = sys.argv[1]
    else:
        url = default_url

    # Check if wait time was provided
    wait_time = 300  # 5 minutes default
    if len(sys.argv) > 2:
        try:
            wait_time = int(sys.argv[2])
        except ValueError:
            print("[!] Invalid wait time, using default (300 seconds)")

    await open_anime_page(url, wait_time)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n[!] Script terminated by user.")

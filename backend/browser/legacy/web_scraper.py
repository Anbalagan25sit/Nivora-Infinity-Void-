"""
Powerful Web Scraping Module - Like Perplexity Comet
Uses Playwright for JavaScript-rendered pages and Vision AI for image-based extraction.
"""

import re
import time
import logging
import asyncio
from typing import Annotated

logger = logging.getLogger(__name__)


async def extract_emails_phones(url: str) -> dict:
    """
    Extract emails and phone numbers from a website using Playwright (async).
    Handles JavaScript-rendered pages.
    """
    from playwright.async_api import async_playwright

    logger.info(f"[WebScraper] Extracting contact info from {url}")

    result = {
        "url": url,
        "emails": [],
        "phones": [],
        "social_links": [],
        "error": None
    }

    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            await page.goto(url, timeout=25000)
            await page.wait_for_load_state('networkidle', timeout=20000)

            # Scroll to load lazy content
            await page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
            await asyncio.sleep(1)
            await page.evaluate('window.scrollTo(0, 0)')
            await asyncio.sleep(0.5)

            # Get all text content
            text = await page.inner_text('body')
            html = await page.content()

            # Get mailto links
            mailto_links = await page.eval_on_selector_all(
                'a[href^="mailto:"]',
                'elements => elements.map(e => e.href.replace("mailto:", "").split("?")[0])'
            )

            # Get social media links
            social_links = await page.eval_on_selector_all(
                'a[href*="instagram"], a[href*="twitter"], a[href*="linkedin"], a[href*="github"], a[href*="facebook"]',
                'elements => elements.map(e => e.href)'
            )

            await browser.close()

        # Extract emails
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails_text = re.findall(email_pattern, text, re.IGNORECASE)
        emails_html = re.findall(email_pattern, html, re.IGNORECASE)

        all_emails = list(set(emails_text + emails_html + mailto_links))

        # Filter false positives
        bad_patterns = ['example.com', 'domain.com', 'test.com', '.png', '.jpg', '.gif', '.svg', '.css', '.js', 'webpack', 'sentry', 'wix']
        result["emails"] = [e for e in all_emails if not any(x in e.lower() for x in bad_patterns)]

        # Extract phones
        phone_pattern = r'[\+]?[(]?[0-9]{1,3}[)]?[-\s\.]?[(]?[0-9]{1,4}[)]?[-\s\.]?[0-9]{1,4}[-\s\.]?[0-9]{1,9}'
        phones = list(set(re.findall(phone_pattern, text)))
        result["phones"] = [p for p in phones if len(re.sub(r'\D', '', p)) >= 10]

        result["social_links"] = list(set(social_links))[:10]

    except Exception as e:
        result["error"] = str(e)
        logger.error(f"[WebScraper] Error: {e}")

    return result


async def vision_extract(url: str, query: str) -> dict:
    """
    Use Vision AI to extract information from a website screenshot (async).
    This can read text from images!
    """
    from playwright.async_api import async_playwright
    import computer_use as _cu
    from PIL import Image
    import io

    logger.info(f"[VisionExtract] Analyzing {url} for: {query}")

    try:
        # Take screenshot
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page(viewport={'width': 1920, 'height': 1080})
            await page.goto(url, timeout=25000)
            await page.wait_for_load_state('networkidle', timeout=20000)

            # Scroll to load content
            await page.evaluate('window.scrollTo(0, document.body.scrollHeight / 2)')
            await asyncio.sleep(1)

            screenshot_bytes = await page.screenshot(full_page=True)
            await browser.close()

        # Convert to PIL Image
        img = Image.open(io.BytesIO(screenshot_bytes))

        # Vision prompt
        prompt = f"""Analyze this website screenshot to find: "{query}"

Look EVERYWHERE including:
- Header/Navigation
- Footer (common for contact info)
- Sidebar sections
- Images with text
- Contact/About sections

Return JSON:
{{
    "found": true/false,
    "data": "exact information found",
    "location": "where on page",
    "confidence": "high/medium/low"
}}

Be thorough!"""

        result = _cu.analyze_screen(prompt, img)
        return result if isinstance(result, dict) else {"data": str(result)}

    except Exception as e:
        logger.error(f"[VisionExtract] Error: {e}")
        return {"error": str(e)}


async def scrape_full_text(url: str) -> str:
    """
    Get all visible text from a website using Playwright (async).
    """
    from playwright.async_api import async_playwright

    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            await page.goto(url, timeout=20000)
            await page.wait_for_load_state('networkidle', timeout=15000)

            title = await page.title()
            text = await page.inner_text('body')
            await browser.close()

        # Clean up
        lines = [l.strip() for l in text.split('\n') if l.strip()]
        clean_text = '\n'.join(lines)

        if len(clean_text) > 5000:
            clean_text = clean_text[:5000] + "\n...[truncated]"

        return f"Title: {title}\n\n{clean_text}"

    except Exception as e:
        return f"Error: {e}"


# Sync wrappers for non-async contexts
def extract_emails_phones_sync(url: str) -> dict:
    """Sync wrapper for extract_emails_phones"""
    from playwright.sync_api import sync_playwright

    logger.info(f"[WebScraper] Extracting contact info from {url} (sync)")

    result = {
        "url": url,
        "emails": [],
        "phones": [],
        "social_links": [],
        "error": None
    }

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(url, timeout=25000)
            page.wait_for_load_state('networkidle', timeout=20000)

            page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
            time.sleep(1)
            page.evaluate('window.scrollTo(0, 0)')
            time.sleep(0.5)

            text = page.inner_text('body')
            html = page.content()

            mailto_links = page.eval_on_selector_all(
                'a[href^="mailto:"]',
                'elements => elements.map(e => e.href.replace("mailto:", "").split("?")[0])'
            )

            social_links = page.eval_on_selector_all(
                'a[href*="instagram"], a[href*="twitter"], a[href*="linkedin"], a[href*="github"], a[href*="facebook"]',
                'elements => elements.map(e => e.href)'
            )

            browser.close()

        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails_text = re.findall(email_pattern, text, re.IGNORECASE)
        emails_html = re.findall(email_pattern, html, re.IGNORECASE)

        all_emails = list(set(emails_text + emails_html + mailto_links))

        bad_patterns = ['example.com', 'domain.com', 'test.com', '.png', '.jpg', '.gif', '.svg', '.css', '.js', 'webpack', 'sentry', 'wix']
        result["emails"] = [e for e in all_emails if not any(x in e.lower() for x in bad_patterns)]

        phone_pattern = r'[\+]?[(]?[0-9]{1,3}[)]?[-\s\.]?[(]?[0-9]{1,4}[)]?[-\s\.]?[0-9]{1,4}[-\s\.]?[0-9]{1,9}'
        phones = list(set(re.findall(phone_pattern, text)))
        result["phones"] = [p for p in phones if len(re.sub(r'\D', '', p)) >= 10]

        result["social_links"] = list(set(social_links))[:10]

    except Exception as e:
        result["error"] = str(e)
        logger.error(f"[WebScraper] Error: {e}")

    return result


# Test function
if __name__ == "__main__":
    # Test extraction
    url = "https://selwynjesudas.com"
    print(f"Testing extraction from {url}...\n")

    result = extract_emails_phones_sync(url)
    print("Emails:", result["emails"])
    print("Phones:", result["phones"])
    print("Social:", result["social_links"])
    print("Error:", result["error"])

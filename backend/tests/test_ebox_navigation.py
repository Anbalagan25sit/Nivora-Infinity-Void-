"""
Test E-Box Navigation - Debug what happens after login
"""

import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

async def test_navigation():
    """Test E-Box login and see what page we land on."""
    print("=" * 60)
    print("E-Box Navigation Debug Test")
    print("=" * 60)

    from browser_automation import BrowserAutomationEngine
    from ebox_automation import login_to_ebox, EBOX_USERNAME

    browser = BrowserAutomationEngine(headless=False)

    try:
        await browser.start()
        print("Browser started")

        # Login
        print("\n1. Logging in...")
        login_result = await login_to_ebox(browser)
        print(f"   Login result: {login_result}")

        if not login_result.get("success"):
            print("Login failed!")
            return

        # Check current URL after login
        await asyncio.sleep(2)
        current_url = await browser.get_current_url()
        print(f"\n2. Current URL after login: {current_url}")

        # Get page title
        page = browser.page
        title = await page.title()
        print(f"   Page title: {title}")

        # Take screenshot for analysis
        print("\n3. Taking screenshot...")
        screenshot = await browser.capture_screenshot()
        print(f"   Screenshot captured: {type(screenshot)}")

        # Try to find course elements on the page
        print("\n4. Looking for course elements...")

        # Check for common course-related elements
        selectors_to_try = [
            'text="Differential"',
            'text="Enrolled"',
            'a[href*="course"]',
            '.course-card',
            '[class*="course"]',
            'text="My Courses"',
            'text="Dashboard"',
        ]

        for selector in selectors_to_try:
            try:
                elements = await page.query_selector_all(selector)
                count = len(elements) if elements else 0
                if count > 0:
                    print(f"   Found {count} elements for: {selector}")
                    # Get text of first element
                    if elements:
                        text = await elements[0].text_content()
                        print(f"      First element text: {text[:100] if text else 'N/A'}...")
            except Exception as e:
                pass

        # Get all visible text on the page
        print("\n5. Getting page content...")
        try:
            body_text = await page.inner_text('body')
            # Look for course-related keywords
            keywords = ['differential', 'biology', 'course', 'enrolled', 'unit', 'topic']
            for kw in keywords:
                if kw.lower() in body_text.lower():
                    # Find context around the keyword
                    idx = body_text.lower().find(kw.lower())
                    context = body_text[max(0, idx-30):idx+50]
                    print(f"   Found '{kw}': ...{context}...")
        except Exception as e:
            print(f"   Could not get body text: {e}")

        # Keep browser open
        print("\n" + "=" * 60)
        print("Browser will stay open for 60 seconds.")
        print("Please check manually what's on the screen.")
        print("=" * 60)

        await asyncio.sleep(60)

    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()

    finally:
        await browser.close()
        print("\nBrowser closed.")


if __name__ == "__main__":
    asyncio.run(test_navigation())

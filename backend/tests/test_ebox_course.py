"""
Test E-Box Course Navigation
"""

import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

async def test_course_navigation():
    """Test navigating to a specific course."""
    print("=" * 60)
    print("E-Box Course Navigation Test")
    print("=" * 60)

    from browser_automation import BrowserAutomationEngine
    from ebox_automation import login_to_ebox, navigate_to_course

    browser = BrowserAutomationEngine(headless=False)

    try:
        await browser.start()
        print("Browser started")

        # Login
        print("\n1. Logging in...")
        login_result = await login_to_ebox(browser)

        if not login_result.get("success"):
            print(f"Login failed: {login_result}")
            return

        print("   Login successful!")

        # Try to navigate to Differential Equations course
        print("\n2. Navigating to 'Differential Equations And Complex Analysis'...")
        nav_result = await navigate_to_course(browser, "Differential Equations And Complex Analysis")

        print(f"   Result: {nav_result}")

        if nav_result.get("success"):
            print("\n   SUCCESS! Course navigation worked!")

            # Check new URL
            current_url = await browser.get_current_url()
            print(f"   New URL: {current_url}")
        else:
            print(f"\n   FAILED: {nav_result.get('error')}")
            if nav_result.get('available_courses'):
                print("   Available courses:")
                for c in nav_result.get('available_courses', []):
                    print(f"      - {c}")

        # Keep browser open
        print("\n" + "=" * 60)
        print("Browser will stay open for 30 seconds.")
        print("=" * 60)

        await asyncio.sleep(30)

    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()

    finally:
        await browser.close()
        print("\nBrowser closed.")


if __name__ == "__main__":
    asyncio.run(test_course_navigation())

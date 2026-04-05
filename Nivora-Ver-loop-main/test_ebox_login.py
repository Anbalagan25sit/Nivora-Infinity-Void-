"""
Test E-Box Login Automation
This script tests the auto-login functionality for E-Box.
"""

import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

async def test_ebox_login():
    """Test the E-Box login automation."""
    print("=" * 60)
    print("E-Box Login Automation Test")
    print("=" * 60)

    # Import browser automation
    from browser_automation import BrowserAutomationEngine
    from ebox_automation import login_to_ebox, EBOX_USERNAME, EBOX_PASSWORD, EBOX_LOGIN_URL

    print(f"\nTarget URL: {EBOX_LOGIN_URL}")
    print(f"Username: {EBOX_USERNAME}")
    print(f"Password: {'*' * len(EBOX_PASSWORD)}")

    # Create browser instance
    print("\n1. Starting browser...")
    browser = BrowserAutomationEngine(headless=False)

    try:
        # Start browser
        await browser.start()
        print("   OK - Browser started")

        # Test login
        print("\n2. Testing login automation...")
        login_result = await login_to_ebox(browser)

        if login_result.get("success"):
            print(f"   OK - Login successful!")
            print(f"   Message: {login_result.get('message', 'No message')}")
        else:
            print(f"   FAIL - Login failed: {login_result.get('error')}")
            return False

        # Keep browser open for manual verification
        print("\n" + "=" * 60)
        print("Browser will stay open for 30 seconds for manual verification.")
        print("Check if you are logged into E-Box dashboard.")
        print("=" * 60)

        await asyncio.sleep(30)

        return True

    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

    finally:
        print("\n3. Closing browser...")
        await browser.close()
        print("   OK - Browser closed")


def main():
    """Run the test."""
    result = asyncio.run(test_ebox_login())

    print("\n" + "=" * 60)
    if result:
        print("TEST PASSED - E-Box login automation works!")
    else:
        print("TEST FAILED - Check the errors above")
    print("=" * 60)

    return 0 if result else 1


if __name__ == "__main__":
    exit(main())

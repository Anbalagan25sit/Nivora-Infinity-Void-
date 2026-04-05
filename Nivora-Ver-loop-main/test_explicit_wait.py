"""
Test with explicit wait for editor to be ready
"""

import asyncio
import sys
import os
from dotenv import load_dotenv

load_dotenv()
sys.path.insert(0, os.path.dirname(__file__))

async def test_with_explicit_wait():
    from playwright.async_api import async_playwright

    print("=" * 70)
    print("E-BOX COMMAND ARGS - Wait for Editor Ready")
    print("=" * 70)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()

        try:
            # Login
            print("\n[1] Login...")
            await page.goto("https://pro.e-box.co.in/login")
            await asyncio.sleep(1)
            await page.fill('input[name="username"]', 'SIT25CS170')
            await page.fill('input[name="password"]', 'SIT25CS170')
            await page.click('button[type="submit"]')
            await asyncio.sleep(2)

            # Navigate
            print("[2] Navigate to course...")
            await page.wait_for_selector('a[href*="course"]')
            courses = await page.query_selector_all('a[href*="course"]')
            for course in courses:
                text = await course.inner_text()
                if 'differential' in text.lower():
                    await course.click()
                    break
            await asyncio.sleep(2)

            print("[3] Click topic...")
            await page.get_by_text("Solution Of Ordinary", exact=False).first.click()
            await asyncio.sleep(1)

            print("[4] Click i-Design...")
            idesign_link = await page.query_selector('a.item:has-text("i-Design")')
            if idesign_link:
                await idesign_link.click()
            await asyncio.sleep(2)

            print("[5] Click project...")
            attempt_link = await page.query_selector('a[href*="attempt"]')
            if attempt_link:
                await attempt_link.click()

            # Wait for the problem page to FULLY load
            print("\n[6] Waiting for editor to be fully ready...")
            try:
                # Wait for Submit button (indicates page is loaded)
                await page.wait_for_selector('button:has-text("Submit")', timeout=10000)
                print("    Submit button found - page loaded")
            except:
                print("    Submit button not found, continuing anyway")

            # Extra wait for any dynamic content
            await asyncio.sleep(5)

            print(f"\n[7] On problem page: {page.url}")

            # Now try to find the command arg field
            print("\n[8] Looking for command line argument field...")
            print("-" * 50)

            # Try getByRole
            textboxes = page.get_by_role('textbox')
            count = await textboxes.count()
            print(f"    getByRole found {count} textboxes")

            if count > 0:
                for i in range(count):
                    try:
                        placeholder = await textboxes.nth(i).get_attribute('placeholder')
                        print(f"      Textbox[{i}]: placeholder='{placeholder}'")
                    except:
                        print(f"      Textbox[{i}]: (no placeholder)")

                # Fill the last one
                print(f"\n    Filling textbox[{count-1}] with: 2 10")
                await textboxes.nth(count - 1).fill('2 10')
                value = await textboxes.nth(count - 1).input_value()
                print(f"    Verified: '{value}'")

                if value == '2 10':
                    print("\n    *** SUCCESS ***")

            # Also try query_selector_all to see all inputs
            print("\n[9] Using query_selector_all('input')...")
            all_inputs = await page.query_selector_all('input')
            print(f"    Found {len(all_inputs)} input elements")

            print("\n" + "=" * 70)
            print("Browser staying open for 30 seconds...")
            print("=" * 70)

            await asyncio.sleep(30)

        except Exception as e:
            print(f"\nERROR: {e}")
            import traceback
            traceback.print_exc()
            await asyncio.sleep(30)

        finally:
            await browser.close()


if __name__ == "__main__":
    asyncio.run(test_with_explicit_wait())

"""
Final Test: Command Line Arguments - Using getByRole approach
"""

import asyncio
import sys
import os
from dotenv import load_dotenv

load_dotenv()
sys.path.insert(0, os.path.dirname(__file__))

async def test_command_args_final():
    from playwright.async_api import async_playwright

    print("=" * 70)
    print("E-BOX COMMAND ARGS - FINAL TEST (getByRole approach)")
    print("=" * 70)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()

        try:
            # Quick navigation
            print("\n[1] Login...")
            await page.goto("https://pro.e-box.co.in/login")
            await asyncio.sleep(1)
            await page.fill('input[name="username"]', 'SIT25CS170')
            await page.fill('input[name="password"]', 'SIT25CS170')
            await page.click('button[type="submit"]')
            await asyncio.sleep(2)

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

            print("[4] Click i-Design section...")
            idesign_link = await page.query_selector('a.item:has-text("i-Design")')
            if idesign_link:
                await idesign_link.click()
            await asyncio.sleep(2)

            print("[5] Click project...")
            attempt_link = await page.query_selector('a[href*="attempt"]')
            if attempt_link:
                await attempt_link.click()
                await asyncio.sleep(3)

            print(f"[6] On problem page: {page.url}")

            # Wait for dynamic content
            print("\n[7] Waiting for command arg field to load...")
            await asyncio.sleep(2)

            # Test the exact approach used in ebox_automation.py
            print("\n[8] Testing getByRole('textbox') approach...")
            print("-" * 50)

            try:
                textboxes = page.get_by_role('textbox')
                count = await textboxes.count()
                print(f"    Found {count} textboxes using getByRole")

                if count > 0:
                    # Fill the last textbox (command args field is last)
                    print(f"    Filling last textbox (index {count-1}) with: 2 10")
                    await textboxes.nth(count - 1).fill('2 10')
                    await asyncio.sleep(0.5)

                    # Verify
                    value = await textboxes.nth(count - 1).input_value()
                    print(f"    Verified value: '{value}'")

                    if value == '2 10':
                        print("\n    *** SUCCESS! ***")
                        print("    Command line argument field filled correctly!")
                        print("    The ebox_automation.py approach works!")
                    else:
                        print(f"\n    FAILED: Expected '2 10' but got '{value}'")
                else:
                    print("    No textboxes found")

            except Exception as e:
                print(f"    Error: {e}")
                import traceback
                traceback.print_exc()

            print("\n" + "=" * 70)
            print("Browser staying open for 20 seconds...")
            print("=" * 70)

            await asyncio.sleep(20)

        except Exception as e:
            print(f"\nERROR: {e}")
            import traceback
            traceback.print_exc()
            await asyncio.sleep(20)

        finally:
            await browser.close()


if __name__ == "__main__":
    asyncio.run(test_command_args_final())

"""
Test Command Line Arguments Handling in E-Box
"""

import asyncio
import sys
import os
from dotenv import load_dotenv

load_dotenv()
sys.path.insert(0, os.path.dirname(__file__))

async def test_command_args():
    from playwright.async_api import async_playwright

    print("=" * 70)
    print("E-BOX COMMAND LINE ARGUMENTS TEST")
    print("=" * 70)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()

        try:
            # Quick navigation to problem page
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

            # Wait for the page to fully load - the command line argument field might load dynamically
            print("\n[6.5] Waiting for dynamic content to load...")
            await asyncio.sleep(3)

            # Now test finding and filling the command line argument field
            print("\n[7] Testing command line argument field...")
            print("-" * 50)

            # Try different input selectors
            input_selectors = [
                'input[type="text"]',
                'input:not([type="password"]):not([type="hidden"])',
                'input',
                'textarea',
            ]

            cmd_arg_filled = False
            for selector in input_selectors:
                if cmd_arg_filled:
                    break

                all_inputs = await page.query_selector_all(selector)
                print(f"\n    Selector '{selector}': Found {len(all_inputs)} fields")

                for i, inp in enumerate(all_inputs):
                    try:
                        # Try multiple ways to find related text
                        # 1. Parent element
                        parent_handle = await inp.evaluate_handle('el => el.parentElement')
                        parent_text = await parent_handle.evaluate('el => el.textContent || ""')

                        # 2. Previous sibling (label might be before the input)
                        prev_sibling_text = await inp.evaluate('el => el.previousElementSibling ? el.previousElementSibling.textContent : ""')

                        # 3. Grandparent (label might be outside parent div)
                        grandparent_text = await inp.evaluate('el => el.parentElement && el.parentElement.parentElement ? el.parentElement.parentElement.textContent : ""')

                        # 4. Check placeholder
                        placeholder = await inp.get_attribute('placeholder') or ''

                        combined_text = f"{parent_text} {prev_sibling_text} {grandparent_text} {placeholder}".lower()

                        print(f"\n      Field [{i}]:")
                        print(f"        Parent: {parent_text[:40]}...")
                        print(f"        Prev sibling: {prev_sibling_text[:40]}...")
                        print(f"        Placeholder: {placeholder}")

                        if 'command' in combined_text and 'argument' in combined_text:
                            print(f"        >>> FOUND COMMAND LINE ARGUMENT FIELD!")
                            print(f"        >>> Filling with: 2 10")
                            await inp.fill('2 10')
                            await asyncio.sleep(0.5)

                            # Verify it was filled
                            value = await inp.input_value()
                            print(f"        >>> Verified value: '{value}'")

                            if value == '2 10':
                                print(f"        >>> SUCCESS! Command args filled correctly!")
                                cmd_arg_filled = True
                            break
                    except Exception as e:
                        print(f"        Error: {e}")

            if not cmd_arg_filled:
                print("\n    WARNING: Could not fill command line argument field")
            else:
                print("\n    SUCCESS: Command line argument field handling works!")

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
    asyncio.run(test_command_args())

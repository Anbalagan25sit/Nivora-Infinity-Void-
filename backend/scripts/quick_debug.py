"""
Quick E-Box Debug - Get problem page elements
"""

import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

async def quick_debug():
    from browser_automation import BrowserAutomationEngine
    from ebox_automation import login_to_ebox, navigate_to_course

    browser = BrowserAutomationEngine(headless=False)

    try:
        await browser.start()

        # Login
        await login_to_ebox(browser)

        # Navigate to course
        await navigate_to_course(browser, "Differential Equations And Complex Analysis")
        await asyncio.sleep(2)

        page = browser.page

        # Click on first topic
        print("Clicking topic...")
        await page.get_by_text("Solution Of Ordinary", exact=False).first.click()
        await asyncio.sleep(1)

        # Click i-Design
        print("Clicking i-Design...")
        await page.get_by_text("i-Design").first.click()
        await asyncio.sleep(1)

        # Click on project
        print("Clicking project...")
        await page.get_by_text("Project", exact=False).first.click()
        await asyncio.sleep(3)

        # Now on problem page
        print("\n" + "=" * 60)
        print("ON PROBLEM PAGE - ANALYZING...")
        print("=" * 60)

        url = await browser.get_current_url()
        print(f"URL: {url}")

        # Get all text
        body = await page.inner_text('body')
        # Convert to ASCII-safe string
        body_safe = body.encode('ascii', 'replace').decode('ascii')
        print(f"\nPage text (first 2000 chars):\n{body_safe[:2000]}")

        # Find all inputs
        print("\n\nINPUT ELEMENTS:")
        inputs = await page.query_selector_all('input')
        for inp in inputs[:10]:
            try:
                inp_type = await inp.get_attribute('type')
                inp_name = await inp.get_attribute('name')
                inp_placeholder = await inp.get_attribute('placeholder')
                print(f"  - type={inp_type}, name={inp_name}, placeholder={inp_placeholder}")
            except:
                pass

        # Find all textareas
        print("\nTEXTAREA ELEMENTS:")
        textareas = await page.query_selector_all('textarea')
        print(f"  Found {len(textareas)} textareas")

        # Find buttons
        print("\nBUTTONS:")
        buttons = await page.query_selector_all('button')
        for btn in buttons[:10]:
            try:
                btn_text = await btn.text_content()
                print(f"  - {btn_text[:50] if btn_text else 'no text'}")
            except:
                pass

        # Find elements with 'code' or 'editor' in class
        print("\nCODE/EDITOR ELEMENTS:")
        html = await page.content()
        import re
        editors = re.findall(r'class="([^"]*(?:code|editor|ace|monaco)[^"]*)"', html, re.I)
        for e in list(set(editors))[:10]:
            print(f"  - {e}")

        # Check for iframe (sometimes code editors are in iframes)
        print("\nIFRAMES:")
        iframes = await page.query_selector_all('iframe')
        print(f"  Found {len(iframes)} iframes")

        # Keep browser open briefly
        print("\n\nBrowser staying open 30 seconds...")
        await asyncio.sleep(30)

    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        await asyncio.sleep(30)

    finally:
        await browser.close()


if __name__ == "__main__":
    asyncio.run(quick_debug())

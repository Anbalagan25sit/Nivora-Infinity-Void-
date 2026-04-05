"""
Debug E-Box Code Editor Structure
"""

import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

async def debug_editor():
    from browser_automation import BrowserAutomationEngine
    from ebox_automation import login_to_ebox, navigate_to_course

    browser = BrowserAutomationEngine(headless=False)

    try:
        await browser.start()
        await login_to_ebox(browser)
        await navigate_to_course(browser, "Differential Equations And Complex Analysis")
        await asyncio.sleep(2)

        page = browser.page

        # Navigate to problem page
        await page.get_by_text("Solution Of Ordinary", exact=False).first.click()
        await asyncio.sleep(1)
        await page.get_by_text("i-Design").first.click()
        await asyncio.sleep(1)
        await page.get_by_text("Project", exact=False).first.click()
        await asyncio.sleep(3)

        print("\n" + "=" * 60)
        print("EDITOR ANALYSIS")
        print("=" * 60)

        # Look for editor container
        editor_selectors = [
            '.editor_container__1K_XX',
            '[class*="editor_container"]',
            '[class*="editor_project"]',
            '.ace_editor',
            '.monaco-editor',
            '.CodeMirror',
            '[class*="code"]',
            '[contenteditable="true"]',
        ]

        for sel in editor_selectors:
            try:
                elems = await page.query_selector_all(sel)
                if elems:
                    print(f"\nFound {len(elems)} elements for: {sel}")
                    for i, elem in enumerate(elems[:3]):
                        # Get inner HTML
                        html = await elem.inner_html()
                        print(f"  [{i}] HTML preview: {html[:200]}...")
            except Exception as e:
                pass

        # Look for input areas in the editor
        print("\n\nLooking for contenteditable or input areas...")
        try:
            # Ace editor has a specific structure
            ace_content = await page.query_selector('.ace_content')
            if ace_content:
                print("  Found .ace_content!")

            ace_text_input = await page.query_selector('.ace_text-input')
            if ace_text_input:
                print("  Found .ace_text-input!")

            # Monaco editor
            monaco_input = await page.query_selector('.monaco-editor textarea')
            if monaco_input:
                print("  Found monaco textarea!")
        except:
            pass

        # Look for any ace/monaco/codemirror
        print("\n\nChecking for common code editors...")
        html = await page.content()

        if 'ace' in html.lower():
            print("  ACE editor detected in page!")
        if 'monaco' in html.lower():
            print("  Monaco editor detected in page!")
        if 'codemirror' in html.lower():
            print("  CodeMirror editor detected in page!")

        # Try to find the div that might contain the code
        print("\n\nLooking for div with specific classes...")
        divs = await page.query_selector_all('div[class*="editor"]')
        print(f"  Found {len(divs)} divs with 'editor' in class")

        # Check for Command Line Arguments input
        print("\n\nLooking for Command Line Arguments input...")
        inputs = await page.query_selector_all('input')
        for inp in inputs:
            try:
                placeholder = await inp.get_attribute('placeholder')
                class_attr = await inp.get_attribute('class')
                if placeholder:
                    print(f"  Input: placeholder='{placeholder}', class='{class_attr}'")
                elif class_attr and 'arg' in class_attr.lower():
                    print(f"  Input: class='{class_attr}'")
            except:
                pass

        # Try to interact with a code editor by clicking
        print("\n\nTrying to click on editor area...")
        try:
            editor = await page.query_selector('[class*="editor_project"]')
            if editor:
                await editor.click()
                await asyncio.sleep(0.5)
                # Try typing
                await page.keyboard.type("# Test code")
                print("  Typed into editor!")
        except Exception as e:
            print(f"  Editor interaction failed: {e}")

        print("\n\nBrowser staying open 45 seconds for manual inspection...")
        await asyncio.sleep(45)

    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        await asyncio.sleep(30)

    finally:
        await browser.close()


if __name__ == "__main__":
    asyncio.run(debug_editor())

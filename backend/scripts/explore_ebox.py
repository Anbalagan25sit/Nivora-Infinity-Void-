"""
E-Box Structure Explorer
Uses Playwright to thoroughly understand the E-Box UI structure
"""

import asyncio
import sys
import os
from dotenv import load_dotenv

load_dotenv()
sys.path.insert(0, os.path.dirname(__file__))

async def explore_ebox():
    from browser_automation import BrowserAutomationEngine
    from ebox_automation import login_to_ebox, navigate_to_course

    browser = BrowserAutomationEngine(headless=False)

    try:
        await browser.start()
        page = browser.page

        # Login
        print("=" * 70)
        print("STEP 1: LOGIN")
        print("=" * 70)
        await login_to_ebox(browser)
        await asyncio.sleep(2)

        # Navigate to course
        print("\n" + "=" * 70)
        print("STEP 2: NAVIGATE TO COURSE")
        print("=" * 70)
        await navigate_to_course(browser, "Differential Equations And Complex Analysis")
        await asyncio.sleep(3)

        # Now we're on course page - let's explore it thoroughly
        print("\n" + "=" * 70)
        print("STEP 3: EXPLORE COURSE PAGE STRUCTURE")
        print("=" * 70)

        url = await browser.get_current_url()
        print(f"URL: {url}")

        # Get the full HTML structure
        html = await page.content()

        # Look for sidebar/topics area
        print("\n--- SIDEBAR / TOPICS ---")

        # Find all clickable elements in the sidebar area
        sidebar_selectors = [
            '.sidebar',
            '[class*="sidebar"]',
            '[class*="topic"]',
            '[class*="menu"]',
            '[class*="nav"]',
            'nav',
            'aside',
        ]

        for sel in sidebar_selectors:
            try:
                elems = await page.query_selector_all(sel)
                if elems and len(elems) > 0:
                    print(f"\nFound {len(elems)} elements for '{sel}':")
                    for i, elem in enumerate(elems[:3]):
                        text = await elem.inner_text()
                        text_clean = ' '.join(text.split())[:100]
                        print(f"  [{i}]: {text_clean}...")
            except:
                pass

        # Look for topic list items
        print("\n--- TOPIC LIST ITEMS ---")

        # Get all links/buttons that might be topics
        topic_elements = await page.query_selector_all('a, button, [role="button"], [class*="item"]')
        print(f"Found {len(topic_elements)} clickable elements total")

        # Filter to find topic-like elements
        topic_names = []
        for elem in topic_elements:
            try:
                text = await elem.inner_text()
                text = text.strip()
                # Look for topic patterns
                if any(x in text.lower() for x in ['solution', 'vector', 'analytic', 'complex', 'partial', 'calculus', 'differential']):
                    href = await elem.get_attribute('href') or ''
                    cls = await elem.get_attribute('class') or ''
                    print(f"  TOPIC: '{text[:50]}' | class='{cls[:30]}' | href='{href[:30]}'")
                    topic_names.append(text)
            except:
                pass

        # Look for section tabs (i-Learn, i-Explore, etc)
        print("\n--- SECTION TABS ---")

        section_keywords = ['i-Learn', 'i-Explore', 'i-Analyse', 'i-Design', 'iLearn', 'iExplore', 'iAnalyse', 'iDesign', 'Learn', 'Explore', 'Analyse', 'Design']

        for keyword in section_keywords:
            try:
                elems = await page.query_selector_all(f'text="{keyword}"')
                if elems:
                    print(f"  Found {len(elems)} elements with text '{keyword}'")
                    for elem in elems[:2]:
                        tag = await elem.evaluate('el => el.tagName')
                        cls = await elem.get_attribute('class') or ''
                        print(f"    Tag: {tag}, Class: {cls[:40]}")
            except:
                pass

        # Try clicking on first topic
        print("\n" + "=" * 70)
        print("STEP 4: CLICK FIRST TOPIC AND EXPLORE")
        print("=" * 70)

        # Click "Solution Of Ordinary Differential"
        try:
            topic_locator = page.get_by_text("Solution Of Ordinary", exact=False).first
            await topic_locator.click()
            await asyncio.sleep(2)
            print("Clicked on 'Solution Of Ordinary Differential'")
        except Exception as e:
            print(f"Could not click topic: {e}")

        # Now look at what changed - sections should be visible
        print("\n--- AFTER CLICKING TOPIC ---")

        body_text = await page.inner_text('body')
        body_safe = body_text.encode('ascii', 'replace').decode('ascii')

        # Find section-related text
        for line in body_safe.split('\n'):
            line = line.strip()
            if line and any(x in line for x in ['Learn', 'Explore', 'Analyse', 'Design', 'Project', '%']):
                if len(line) < 100:
                    print(f"  {line}")

        # Look for section tabs after clicking topic
        print("\n--- SECTION ELEMENTS AFTER TOPIC CLICK ---")

        # Check for tab-like elements
        tab_selectors = [
            '[role="tab"]',
            '[class*="tab"]',
            '[class*="Tab"]',
            '.menu-item',
            '[class*="menu"]',
            '[class*="phase"]',
            '[class*="section"]',
        ]

        for sel in tab_selectors:
            try:
                elems = await page.query_selector_all(sel)
                if elems:
                    print(f"\n'{sel}' - {len(elems)} elements:")
                    for i, elem in enumerate(elems[:5]):
                        text = await elem.inner_text()
                        text_clean = ' '.join(text.split())[:60]
                        cls = await elem.get_attribute('class') or ''
                        print(f"    [{i}] '{text_clean}' | class: {cls[:40]}")
            except:
                pass

        # Try to find the section buttons by looking at all buttons
        print("\n--- ALL BUTTONS ON PAGE ---")
        buttons = await page.query_selector_all('button')
        for btn in buttons[:15]:
            try:
                text = await btn.inner_text()
                text_clean = ' '.join(text.split())[:50]
                cls = await btn.get_attribute('class') or ''
                if text_clean:
                    print(f"  Button: '{text_clean}' | class: {cls[:40]}")
            except:
                pass

        # Try clicking on i-Learn
        print("\n" + "=" * 70)
        print("STEP 5: TRY CLICKING i-Learn SECTION")
        print("=" * 70)

        try:
            # Try multiple ways to find i-Learn
            methods = [
                ("get_by_text exact", lambda: page.get_by_text("i-Learn", exact=True).first),
                ("get_by_text contains", lambda: page.get_by_text("i-Learn").first),
                ("locator text", lambda: page.locator('text="i-Learn"').first),
                ("locator contains", lambda: page.locator('text=/i-Learn/i').first),
                ("get_by_role tab", lambda: page.get_by_role("tab", name="i-Learn")),
            ]

            for name, locator_fn in methods:
                try:
                    locator = locator_fn()
                    count = await locator.count()
                    if count > 0:
                        print(f"  Method '{name}': FOUND (count={count})")
                        # Try to click
                        await locator.click(timeout=5000)
                        print(f"  -> CLICKED successfully!")
                        await asyncio.sleep(2)
                        break
                    else:
                        print(f"  Method '{name}': not found")
                except Exception as e:
                    print(f"  Method '{name}': error - {str(e)[:50]}")

        except Exception as e:
            print(f"Error trying to click i-Learn: {e}")

        # Check what's on page now
        print("\n--- PAGE CONTENT AFTER SECTION CLICK ---")
        body_text = await page.inner_text('body')
        body_safe = body_text.encode('ascii', 'replace').decode('ascii')

        # Look for project link
        for line in body_safe.split('\n'):
            line = line.strip()
            if 'project' in line.lower() or 'Project' in line:
                print(f"  {line[:80]}")

        # Try to click Project
        print("\n" + "=" * 70)
        print("STEP 6: TRY CLICKING PROJECT")
        print("=" * 70)

        try:
            project_locator = page.get_by_text("Project", exact=False).first
            await project_locator.click()
            await asyncio.sleep(3)
            print("Clicked on Project!")

            new_url = await browser.get_current_url()
            print(f"New URL: {new_url}")
        except Exception as e:
            print(f"Could not click Project: {e}")

        # Now explore the problem page
        print("\n" + "=" * 70)
        print("STEP 7: EXPLORE PROBLEM PAGE")
        print("=" * 70)

        # Look for code editor
        print("\n--- CODE EDITOR ELEMENTS ---")
        editor_selectors = [
            '.ace_editor',
            '.monaco-editor',
            '.CodeMirror',
            '[class*="editor"]',
            'textarea',
            '[contenteditable="true"]',
        ]

        for sel in editor_selectors:
            try:
                elems = await page.query_selector_all(sel)
                if elems:
                    print(f"  '{sel}': {len(elems)} elements")
                    for elem in elems[:2]:
                        cls = await elem.get_attribute('class') or ''
                        print(f"    class: {cls[:60]}")
            except:
                pass

        # Look for input fields (for command line args)
        print("\n--- INPUT FIELDS ---")
        inputs = await page.query_selector_all('input[type="text"], input:not([type])')
        print(f"Found {len(inputs)} text inputs")
        for inp in inputs:
            try:
                placeholder = await inp.get_attribute('placeholder') or ''
                name = await inp.get_attribute('name') or ''
                cls = await inp.get_attribute('class') or ''
                print(f"  placeholder='{placeholder}' | name='{name}' | class='{cls[:30]}'")
            except:
                pass

        # Look for Submit button
        print("\n--- SUBMIT BUTTONS ---")
        submit_texts = ['Submit', 'Run', 'Execute', 'Check', 'Verify']
        for text in submit_texts:
            try:
                btn = await page.query_selector(f'button:has-text("{text}")')
                if btn:
                    cls = await btn.get_attribute('class') or ''
                    print(f"  Found '{text}' button | class: {cls[:40]}")
            except:
                pass

        # Screenshot for manual inspection
        print("\n" + "=" * 70)
        print("EXPLORATION COMPLETE")
        print("Browser staying open for 120 seconds for manual inspection")
        print("=" * 70)

        await asyncio.sleep(120)

    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        await asyncio.sleep(60)

    finally:
        await browser.close()
        print("\nBrowser closed.")


if __name__ == "__main__":
    asyncio.run(explore_ebox())

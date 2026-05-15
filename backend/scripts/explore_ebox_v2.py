"""
E-Box Structure Explorer v2
More robust exploration with better error handling
"""

import asyncio
import sys
import os
from dotenv import load_dotenv

load_dotenv()
sys.path.insert(0, os.path.dirname(__file__))

async def explore_ebox():
    from playwright.async_api import async_playwright

    print("=" * 70)
    print("E-BOX STRUCTURE EXPLORER")
    print("=" * 70)

    async with async_playwright() as p:
        # Launch browser
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        try:
            # Step 1: Go to login page
            print("\n[1] Navigating to login page...")
            await page.goto("https://pro.e-box.co.in/login", timeout=30000)
            await asyncio.sleep(2)

            # Step 2: Login
            print("[2] Logging in...")
            await page.fill('input[name="username"]', 'SIT25CS170')
            await page.fill('input[name="password"]', 'SIT25CS170')
            await page.click('button[type="submit"]')
            await asyncio.sleep(3)

            print(f"    Current URL: {page.url}")

            # Step 3: Find and click course
            print("\n[3] Looking for courses...")
            await page.wait_for_selector('a[href*="course"]', timeout=10000)

            courses = await page.query_selector_all('a[href*="course"]')
            print(f"    Found {len(courses)} course links")

            # Find Differential Equations course
            for course in courses:
                text = await course.inner_text()
                if 'differential' in text.lower() or 'digital electronics' in text.lower():
                    print(f"    Clicking: {text[:60]}...")
                    await course.click()
                    break

            await asyncio.sleep(3)
            print(f"    Current URL: {page.url}")

            # Step 4: Explore course page structure
            print("\n[4] EXPLORING COURSE PAGE STRUCTURE")
            print("-" * 50)

            # Get all text content
            body = await page.inner_text('body')
            body_safe = body.encode('ascii', 'replace').decode('ascii')

            # Find topic names
            print("\n    TOPICS FOUND:")
            topics_found = []
            for line in body_safe.split('\n'):
                line = line.strip()
                if any(x in line for x in ['Solution Of', 'Vector Calculus', 'Analytic Functions', 'Complex Integration', 'Partial Differential', 'Fundamentals of Digital Logic', 'Boolean Function Simplification', 'Design of Combinational Circuits', 'Sequential Circuits', 'Asynchronous Sequential Logic', 'Memory Device']):
                    if len(line) < 80 and line not in topics_found:
                        topics_found.append(line)
                        print(f"      - {line}")

            # Find section names
            print("\n    SECTIONS FOUND:")
            for line in body_safe.split('\n'):
                line = line.strip()
                if any(x in line for x in ['i-Learn', 'i-Explore', 'i-Analyse', 'i-Design', 'iLearn']):
                    if len(line) < 60:
                        print(f"      - {line}")

            # Step 5: Click on first topic
            print("\n[5] CLICKING ON FIRST TOPIC...")

            # Try to find and click topic
            topic_clicked = False
            try:
                topic = page.get_by_text("Fundamentals of Digital Logic", exact=False).first
                await topic.click(timeout=5000)
                topic_clicked = True
                print("    Clicked 'Fundamentals of Digital Logic'")
            except:
                print("    Could not click by text, trying alternative...")
                # Try clicking any element containing the topic text
                elems = await page.query_selector_all('*')
                for elem in elems:
                    try:
                        text = await elem.inner_text()
                        if 'Fundamentals of Digital Logic' in text and len(text) < 100:
                            await elem.click()
                            topic_clicked = True
                            print(f"    Clicked element with text: {text[:50]}")
                            break
                    except:
                        continue

            await asyncio.sleep(2)

            # Step 6: Explore what's visible after topic click
            print("\n[6] EXPLORING PAGE AFTER TOPIC CLICK")
            print("-" * 50)

            body = await page.inner_text('body')
            body_safe = body.encode('ascii', 'replace').decode('ascii')

            # Look for section tabs
            print("\n    Looking for section tabs...")

            # Check for tab elements
            tabs = await page.query_selector_all('[role="tab"], [class*="tab"], [class*="Tab"]')
            print(f"    Found {len(tabs)} tab elements")
            for tab in tabs[:10]:
                try:
                    text = await tab.inner_text()
                    cls = await tab.get_attribute('class') or ''
                    print(f"      Tab: '{text.strip()[:30]}' | class: {cls[:40]}")
                except:
                    pass

            # Look for menu items
            menu_items = await page.query_selector_all('[class*="menu"], [class*="Menu"], [class*="item"], [class*="Item"]')
            print(f"\n    Found {len(menu_items)} menu-like elements")

            # Filter for section-related
            for item in menu_items:
                try:
                    text = await item.inner_text()
                    if any(x in text for x in ['Learn', 'Explore', 'Analyse', 'Design']):
                        cls = await item.get_attribute('class') or ''
                        tag = await item.evaluate('el => el.tagName')
                        print(f"      {tag}: '{text.strip()[:40]}' | class: {cls[:30]}")
                except:
                    pass

            # Step 7: Try different methods to click i-Learn
            print("\n[7] TRYING TO CLICK i-Learn SECTION")
            print("-" * 50)

            section_found = False

            # Method 1: Direct text
            try:
                await page.get_by_text("i-Learn", exact=True).click(timeout=3000)
                section_found = True
                print("    SUCCESS: Clicked i-Learn by exact text")
            except Exception as e:
                print(f"    Method 1 (exact text): Failed - {str(e)[:40]}")

            # Method 2: Contains text
            if not section_found:
                try:
                    await page.locator('text=/i-Learn/').first.click(timeout=3000)
                    section_found = True
                    print("    SUCCESS: Clicked i-Learn by regex")
                except Exception as e:
                    print(f"    Method 2 (regex): Failed - {str(e)[:40]}")

            # Method 3: Look for any element with i-Learn and click
            if not section_found:
                try:
                    elems = await page.query_selector_all('*')
                    for elem in elems:
                        try:
                            text = await elem.inner_text()
                            if text.strip() == 'i-Learn':
                                await elem.click()
                                section_found = True
                                print("    SUCCESS: Clicked i-Learn element directly")
                                break
                        except:
                            continue
                except Exception as e:
                    print(f"    Method 3 (direct element): Failed - {str(e)[:40]}")

            # Method 4: Click by XPath
            if not section_found:
                try:
                    await page.click('//text()[contains(.,"i-Learn")]/parent::*', timeout=3000)
                    section_found = True
                    print("    SUCCESS: Clicked i-Learn by XPath")
                except Exception as e:
                    print(f"    Method 4 (XPath): Failed - {str(e)[:40]}")

            await asyncio.sleep(2)

            # Step 8: Look for Project link
            print("\n[8] LOOKING FOR PROJECT LINK")
            print("-" * 50)

            body = await page.inner_text('body')
            body_safe = body.encode('ascii', 'replace').decode('ascii')

            # Find project-related text
            for line in body_safe.split('\n'):
                line = line.strip()
                if 'project' in line.lower() or 'Project' in line:
                    if len(line) < 100:
                        print(f"    {line}")

            # Try to click on Project
            print("\n    Trying to click Project...")
            project_clicked = False

            try:
                await page.get_by_text("Project", exact=False).first.click(timeout=5000)
                project_clicked = True
                print("    SUCCESS: Clicked on Project")
            except Exception as e:
                print(f"    Failed to click Project: {str(e)[:40]}")

            await asyncio.sleep(3)
            print(f"    Current URL: {page.url}")

            # Step 9: Explore problem page
            if 'attempt' in page.url or project_clicked:
                print("\n[9] EXPLORING PROBLEM PAGE")
                print("-" * 50)

                # Find the code editor
                print("\n    Looking for code editor...")
                editor_selectors = [
                    '.ace_editor',
                    '.ace_content',
                    '.monaco-editor',
                    '.CodeMirror',
                    '[class*="editor"]',
                    'textarea',
                ]

                for sel in editor_selectors:
                    elems = await page.query_selector_all(sel)
                    if elems:
                        print(f"      {sel}: {len(elems)} elements")

                # Find input fields
                print("\n    Looking for input fields...")
                inputs = await page.query_selector_all('input')
                for inp in inputs:
                    try:
                        inp_type = await inp.get_attribute('type') or ''
                        placeholder = await inp.get_attribute('placeholder') or ''
                        name = await inp.get_attribute('name') or ''
                        cls = await inp.get_attribute('class') or ''
                        if inp_type in ['text', ''] or placeholder or 'arg' in (name + cls).lower():
                            print(f"      type={inp_type}, placeholder={placeholder}, name={name}")
                    except:
                        pass

                # Find submit buttons
                print("\n    Looking for submit/run buttons...")
                buttons = await page.query_selector_all('button')
                for btn in buttons:
                    try:
                        text = await btn.inner_text()
                        text = text.strip()
                        if text and any(x in text.lower() for x in ['submit', 'run', 'execute', 'check']):
                            cls = await btn.get_attribute('class') or ''
                            print(f"      Button: '{text}' | class: {cls[:40]}")
                    except:
                        pass

            print("\n" + "=" * 70)
            print("EXPLORATION COMPLETE")
            print("Browser staying open for 90 seconds...")
            print("=" * 70)

            await asyncio.sleep(90)

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

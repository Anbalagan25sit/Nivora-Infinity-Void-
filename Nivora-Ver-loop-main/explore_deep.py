"""
E-Box Deep Exploration - After clicking section
"""

import asyncio
import sys
import os
from dotenv import load_dotenv

load_dotenv()
sys.path.insert(0, os.path.dirname(__file__))

async def explore_after_section():
    from playwright.async_api import async_playwright

    print("=" * 70)
    print("E-BOX DEEP EXPLORATION")
    print("=" * 70)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()

        try:
            # Login
            print("\n[1] Login...")
            await page.goto("https://pro.e-box.co.in/login", timeout=30000)
            await asyncio.sleep(1)
            await page.fill('input[name="username"]', 'SIT25CS170')
            await page.fill('input[name="password"]', 'SIT25CS170')
            await page.click('button[type="submit"]')
            await asyncio.sleep(2)

            # Navigate to course
            print("[2] Navigate to course...")
            await page.wait_for_selector('a[href*="course"]', timeout=10000)
            courses = await page.query_selector_all('a[href*="course"]')
            for course in courses:
                text = await course.inner_text()
                if 'differential' in text.lower():
                    await course.click()
                    break
            await asyncio.sleep(2)

            # Click on topic
            print("[3] Click on topic...")
            await page.get_by_text("Solution Of Ordinary", exact=False).first.click()
            await asyncio.sleep(2)

            # Explore the section tabs structure
            print("\n[4] EXPLORING SECTION TABS")
            print("-" * 50)

            # The sections are <a> tags with class "item" in a menu
            menu = await page.query_selector('.ui.pointing.secondary.menu')
            if menu:
                print("    Found section menu!")
                links = await menu.query_selector_all('a.item')
                print(f"    Found {len(links)} section links:")
                for link in links:
                    text = await link.inner_text()
                    cls = await link.get_attribute('class')
                    href = await link.get_attribute('href') or 'no href'
                    print(f"      - '{text.strip()}' | class: {cls} | href: {href[:40]}")

            # Click on i-Learn section
            print("\n[5] CLICKING i-Learn SECTION")
            print("-" * 50)

            # Use the specific selector for section links
            try:
                ilearn = await page.query_selector('a.item:has-text("i-Learn")')
                if ilearn:
                    await ilearn.click()
                    print("    Clicked i-Learn!")
                else:
                    # Alternative: click by text
                    await page.click('a.item >> text="i-Learn"')
                    print("    Clicked i-Learn (alternative)!")
            except Exception as e:
                print(f"    Error clicking i-Learn: {e}")

            await asyncio.sleep(3)  # Wait for content to load

            # Now explore what's visible after clicking i-Learn
            print("\n[6] EXPLORING CONTENT AFTER SECTION CLICK")
            print("-" * 50)

            body = await page.inner_text('body')
            body_safe = body.encode('ascii', 'replace').decode('ascii')

            # Print relevant lines
            print("\n    Content containing 'Project' or percentage:")
            for line in body_safe.split('\n'):
                line = line.strip()
                if ('project' in line.lower() or '%' in line) and len(line) < 120:
                    print(f"      {line}")

            # Look for clickable project elements
            print("\n    Looking for project links/buttons...")

            # Find elements that might be project links
            project_selectors = [
                'a:has-text("Project")',
                '[class*="project"]',
                '[class*="Project"]',
                'a[href*="attempt"]',
                'a[href*="project"]',
                '.session-item',
                '[class*="session"]',
            ]

            for sel in project_selectors:
                try:
                    elems = await page.query_selector_all(sel)
                    if elems:
                        print(f"\n      Selector '{sel}': {len(elems)} elements")
                        for elem in elems[:3]:
                            text = await elem.inner_text()
                            text_clean = ' '.join(text.split())[:60]
                            cls = await elem.get_attribute('class') or ''
                            href = await elem.get_attribute('href') or ''
                            print(f"        text: '{text_clean}'")
                            print(f"        class: {cls[:40]}, href: {href[:40]}")
                except:
                    pass

            # Look for the specific project card/item
            print("\n    Looking for project card with completion percentage...")

            # Projects usually show completion percentage
            all_elements = await page.query_selector_all('*')
            for elem in all_elements:
                try:
                    text = await elem.inner_text()
                    if 'Completed' in text and ('Project' in text or 'iLearn' in text.replace('-', '').replace(' ', '')):
                        if len(text) < 200:
                            tag = await elem.evaluate('el => el.tagName')
                            cls = await elem.get_attribute('class') or ''
                            print(f"\n      Found project element:")
                            print(f"        Tag: {tag}")
                            print(f"        Class: {cls[:50]}")
                            print(f"        Text: {text[:100]}")

                            # Check if it's clickable
                            is_clickable = tag.lower() in ['a', 'button'] or await elem.evaluate('el => el.onclick !== null')
                            print(f"        Clickable: {is_clickable}")

                            # Try to click it
                            if tag.lower() in ['a', 'button', 'div']:
                                print("        Attempting to click...")
                                await elem.click()
                                await asyncio.sleep(3)
                                print(f"        New URL: {page.url}")
                                break
                except:
                    pass

            # Step 7: If we're on problem page, explore it
            print("\n[7] EXPLORING CURRENT PAGE")
            print("-" * 50)

            current_url = page.url
            print(f"    URL: {current_url}")

            if 'attempt' in current_url:
                print("\n    ON PROBLEM PAGE!")

                # Find code editor
                print("\n    Code editor elements:")
                for sel in ['.ace_editor', '.ace_content', '[class*="editor"]', 'textarea']:
                    elems = await page.query_selector_all(sel)
                    if elems:
                        print(f"      {sel}: {len(elems)} elements")

                # Find command line input
                print("\n    Input fields:")
                inputs = await page.query_selector_all('input')
                for inp in inputs:
                    placeholder = await inp.get_attribute('placeholder') or ''
                    name = await inp.get_attribute('name') or ''
                    if placeholder or name:
                        print(f"      placeholder='{placeholder}', name='{name}'")

                # Find submit button
                print("\n    Buttons:")
                buttons = await page.query_selector_all('button')
                for btn in buttons:
                    text = await btn.inner_text()
                    if text.strip():
                        print(f"      '{text.strip()}'")

            print("\n" + "=" * 70)
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


if __name__ == "__main__":
    asyncio.run(explore_after_section())

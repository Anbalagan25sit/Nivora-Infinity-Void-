"""
Debug Command Line Arguments Input Field on E-Box
"""

import asyncio
import sys
import os
from dotenv import load_dotenv

load_dotenv()
sys.path.insert(0, os.path.dirname(__file__))

async def debug_command_args():
    from playwright.async_api import async_playwright

    print("=" * 70)
    print("E-BOX COMMAND ARGUMENTS DEBUG")
    print("=" * 70)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()

        try:
            # Quick navigation to problem page
            print("\n[1] Navigating to problem page...")
            await page.goto("https://pro.e-box.co.in/login")
            await asyncio.sleep(1)

            # Login
            await page.fill('input[name="username"]', 'SIT25CS170')
            await page.fill('input[name="password"]', 'SIT25CS170')
            await page.click('button[type="submit"]')
            await asyncio.sleep(2)

            # Navigate to course
            await page.wait_for_selector('a[href*="course"]')
            courses = await page.query_selector_all('a[href*="course"]')
            for course in courses:
                text = await course.inner_text()
                if 'differential' in text.lower():
                    await course.click()
                    break
            await asyncio.sleep(2)

            # Click topic
            await page.get_by_text("Solution Of Ordinary", exact=False).first.click()
            await asyncio.sleep(1)

            # Click i-Design section
            idesign_link = await page.query_selector('a.item:has-text("i-Design")')
            if idesign_link:
                await idesign_link.click()
            await asyncio.sleep(2)

            # Click project link
            attempt_link = await page.query_selector('a[href*="attempt"]')
            if attempt_link:
                await attempt_link.click()
                await asyncio.sleep(3)

            print(f"    Problem page URL: {page.url}")

            # Now we're on the problem page - let's find ALL input fields
            print("\n[2] EXPLORING ALL INPUT ELEMENTS")
            print("-" * 50)

            inputs = await page.query_selector_all('input')
            print(f"    Found {len(inputs)} input elements total:")

            for i, inp in enumerate(inputs):
                try:
                    inp_type = await inp.get_attribute('type') or 'text'
                    name = await inp.get_attribute('name') or ''
                    placeholder = await inp.get_attribute('placeholder') or ''
                    cls = await inp.get_attribute('class') or ''
                    value = await inp.get_attribute('value') or ''

                    # Check if visible
                    is_visible = await inp.is_visible()

                    print(f"\n      Input [{i}]:")
                    print(f"        Type: {inp_type}")
                    print(f"        Name: {name}")
                    print(f"        Placeholder: {placeholder}")
                    print(f"        Class: {cls[:50]}")
                    print(f"        Value: {value}")
                    print(f"        Visible: {is_visible}")

                    # Check if this could be command args field
                    if any(keyword in (name + placeholder + cls).lower() for keyword in ['arg', 'command', 'parameter', 'input']):
                        print(f"        >>> POSSIBLE COMMAND ARGS FIELD! <<<")

                except Exception as e:
                    print(f"      Input [{i}]: Error reading attributes - {e}")

            # Look for textareas too
            print("\n[3] EXPLORING TEXTAREA ELEMENTS")
            print("-" * 50)

            textareas = await page.query_selector_all('textarea')
            print(f"    Found {len(textareas)} textarea elements:")

            for i, ta in enumerate(textareas):
                try:
                    name = await ta.get_attribute('name') or ''
                    placeholder = await ta.get_attribute('placeholder') or ''
                    cls = await ta.get_attribute('class') or ''
                    is_visible = await ta.is_visible()

                    print(f"\n      Textarea [{i}]:")
                    print(f"        Name: {name}")
                    print(f"        Placeholder: {placeholder}")
                    print(f"        Class: {cls[:50]}")
                    print(f"        Visible: {is_visible}")

                except Exception as e:
                    print(f"      Textarea [{i}]: Error - {e}")

            # Look for any element containing "command" or "argument"
            print("\n[4] SEARCHING FOR COMMAND/ARGUMENT RELATED TEXT")
            print("-" * 50)

            body_text = await page.inner_text('body')
            body_safe = body_text.encode('ascii', 'replace').decode('ascii')

            lines = body_safe.split('\n')
            for i, line in enumerate(lines):
                line = line.strip()
                if any(keyword in line.lower() for keyword in ['command', 'argument', 'args', 'parameter', 'input']):
                    if len(line) < 120 and line:
                        print(f"    Line {i}: {line}")

            # Look for labels that might indicate command args
            print("\n[5] EXPLORING LABELS AND DIVS")
            print("-" * 50)

            labels = await page.query_selector_all('label')
            for label in labels:
                try:
                    text = await label.inner_text()
                    if text and any(keyword in text.lower() for keyword in ['command', 'argument', 'parameter', 'input']):
                        for_attr = await label.get_attribute('for') or ''
                        print(f"    Label: '{text.strip()}' | for='{for_attr}'")
                except:
                    pass

            # Look for divs or spans with command-related content
            for selector in ['div', 'span', 'p']:
                elements = await page.query_selector_all(selector)
                for elem in elements[:50]:  # Limit to first 50
                    try:
                        text = await elem.inner_text()
                        if text and len(text) < 100:
                            if any(keyword in text.lower() for keyword in ['command line', 'arguments', 'args', 'input parameters']):
                                cls = await elem.get_attribute('class') or ''
                                print(f"    {selector.upper()}: '{text.strip()}' | class: {cls[:40]}")
                    except:
                        pass

            # Try to find input fields by their position relative to the code editor
            print("\n[6] LOOKING FOR INPUTS NEAR CODE EDITOR")
            print("-" * 50)

            # Find the editor container
            editor = await page.query_selector('[class*="editor"]')
            if editor:
                print("    Found code editor")

                # Look for input fields that are siblings or in parent/child relationship
                parent = await editor.evaluate('el => el.parentElement')
                if parent:
                    nearby_inputs = await page.evaluate('''(editor) => {
                        const container = editor.parentElement;
                        const inputs = container.querySelectorAll('input, textarea');
                        return Array.from(inputs).map(input => ({
                            type: input.type || 'text',
                            name: input.name || '',
                            placeholder: input.placeholder || '',
                            className: input.className || '',
                            tagName: input.tagName
                        }));
                    }''', editor)

                    print(f"    Found {len(nearby_inputs)} inputs near editor:")
                    for inp in nearby_inputs:
                        print(f"      {inp['tagName']}: type={inp['type']}, name={inp['name']}, placeholder={inp['placeholder']}")

            # Final check - look at the page structure around typical command line input locations
            print("\n[7] CHECKING TYPICAL LOCATIONS FOR COMMAND INPUTS")
            print("-" * 50)

            # Often command inputs are below the editor or in a form
            forms = await page.query_selector_all('form')
            print(f"    Found {len(forms)} forms on page")

            for i, form in enumerate(forms):
                try:
                    form_inputs = await form.query_selector_all('input, textarea')
                    print(f"      Form {i}: {len(form_inputs)} inputs")

                    for j, inp in enumerate(form_inputs):
                        name = await inp.get_attribute('name') or ''
                        placeholder = await inp.get_attribute('placeholder') or ''
                        print(f"        Input {j}: name={name}, placeholder={placeholder}")
                except:
                    pass

            print("\n" + "=" * 70)
            print("Browser staying open for 90 seconds for manual inspection...")
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
    asyncio.run(debug_command_args())
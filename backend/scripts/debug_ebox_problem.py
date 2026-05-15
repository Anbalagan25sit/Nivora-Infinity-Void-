"""
Debug E-Box Problem Page - Find elements on the problem page
"""

import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

async def debug_problem_page():
    """Navigate to a problem page and inspect the DOM."""
    print("=" * 60)
    print("E-Box Problem Page Debug")
    print("=" * 60)

    from browser_automation import BrowserAutomationEngine
    from ebox_automation import login_to_ebox, navigate_to_course

    browser = BrowserAutomationEngine(headless=False)

    try:
        await browser.start()
        print("Browser started")

        # Login
        print("\n1. Logging in...")
        login_result = await login_to_ebox(browser)
        if not login_result.get("success"):
            print(f"Login failed: {login_result}")
            return
        print("   Login successful!")

        # Navigate to course
        print("\n2. Navigating to Differential Equations course...")
        course_result = await navigate_to_course(browser, "Differential Equations And Complex Analysis")
        if not course_result.get("success"):
            print(f"Course navigation failed: {course_result}")
            return
        print("   Course navigation successful!")

        await asyncio.sleep(2)
        page = browser.page

        # Now we're on the course page - let's look for topics
        print("\n3. Looking for topics in sidebar...")

        # Get all text on the page
        body_text = await page.inner_text('body')

        # Look for specific topic patterns
        topic_patterns = [
            "Solution Of Ordinary",
            "Vector Calculus",
            "Analytic Functions",
            "Complex Integration",
            "Partial Differential"
        ]

        for pattern in topic_patterns:
            if pattern.lower() in body_text.lower():
                print(f"   Found topic: {pattern}")

        # Try to click on first topic
        print("\n4. Trying to click on 'Solution Of Ordinary Differential'...")
        try:
            await page.get_by_text("Solution Of Ordinary", exact=False).first.click()
            await asyncio.sleep(2)
            print("   Clicked on topic!")
        except Exception as e:
            print(f"   Could not click topic: {e}")

        # Look for section tabs (i-Learn, i-Design, etc)
        print("\n5. Looking for section tabs...")
        section_tabs = ["i-Learn", "i-Explore", "i-Analyse", "i-Design"]
        for tab in section_tabs:
            try:
                elem = await page.query_selector(f'text="{tab}"')
                if elem:
                    print(f"   Found tab: {tab}")
            except:
                pass

        # Try to click i-Design
        print("\n6. Clicking on i-Design tab...")
        try:
            await page.get_by_text("i-Design", exact=True).click()
            await asyncio.sleep(2)
            print("   Clicked i-Design!")
        except Exception as e:
            print(f"   Could not click i-Design: {e}")

        # Look for project link
        print("\n7. Looking for project link...")
        try:
            # Look for text containing "Project"
            project_elem = await page.query_selector('text=/Project/i')
            if project_elem:
                text = await project_elem.text_content()
                print(f"   Found project element: {text[:80]}...")
                await project_elem.click()
                await asyncio.sleep(3)
                print("   Clicked on project!")
        except Exception as e:
            print(f"   Project click error: {e}")

        # Now on problem page - let's analyze it
        print("\n8. Analyzing problem page...")

        current_url = await browser.get_current_url()
        print(f"   URL: {current_url}")

        # Get page content
        body_text = await page.inner_text('body')

        # Look for key elements
        print("\n9. Key content found:")

        # Problem title
        if "Problem" in body_text:
            # Find the problem title
            lines = body_text.split('\n')
            for i, line in enumerate(lines):
                if 'Problem' in line or 'Simulat' in line or 'Context' in line:
                    print(f"   Line {i}: {line[:100]}...")
                    if i < 10:
                        break

        # Look for code editor elements
        print("\n10. Looking for code-related elements...")

        code_selectors = [
            'textarea',
            '.ace_editor',
            '.monaco-editor',
            '[class*="editor"]',
            '[class*="code"]',
            'input[placeholder*="argument"]',
            'input[placeholder*="command"]',
            'input[name*="arg"]',
        ]

        for selector in code_selectors:
            try:
                elems = await page.query_selector_all(selector)
                if elems and len(elems) > 0:
                    print(f"   Found {len(elems)} element(s) for: {selector}")
            except:
                pass

        # Look for numbered steps (1, 2, 3, etc on the sidebar)
        print("\n11. Looking for numbered steps...")
        try:
            # Steps are usually in a sidebar
            steps = await page.query_selector_all('[class*="step"], [class*="question"], .sidebar li')
            print(f"   Found {len(steps)} step elements")
        except:
            pass

        # Look for submit/run buttons
        print("\n12. Looking for submit buttons...")
        submit_patterns = ['Submit', 'Run', 'Execute', 'Check', 'Verify']
        for pattern in submit_patterns:
            try:
                elem = await page.query_selector(f'button:has-text("{pattern}")')
                if elem:
                    print(f"   Found button: {pattern}")
            except:
                pass

        # Dump some of the page HTML structure
        print("\n13. Page HTML structure (partial)...")
        try:
            html = await page.content()
            # Look for interesting class names
            import re
            classes = re.findall(r'class="([^"]+)"', html)
            unique_classes = list(set(classes))
            interesting = [c for c in unique_classes if any(x in c.lower() for x in ['problem', 'question', 'editor', 'code', 'step', 'submit', 'arg', 'input'])]
            print(f"   Interesting classes: {interesting[:20]}")
        except Exception as e:
            print(f"   Could not get HTML: {e}")

        # Keep browser open
        print("\n" + "=" * 60)
        print("Browser staying open for 120 seconds - manually inspect the page!")
        print("=" * 60)

        await asyncio.sleep(120)

    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()

    finally:
        await browser.close()
        print("\nBrowser closed.")


if __name__ == "__main__":
    asyncio.run(debug_problem_page())

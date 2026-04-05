"""
Test E-Box Full Automation Flow
Tests: Login -> Course -> Topic -> Section -> Project -> Analyze -> Generate Code -> Submit
"""

import asyncio
import sys
import os

# Load .env file
from dotenv import load_dotenv
load_dotenv()

sys.path.insert(0, os.path.dirname(__file__))

async def test_full_flow():
    from browser_automation import BrowserAutomationEngine
    from ebox_automation import (
        login_to_ebox, navigate_to_course, click_topic, click_section,
        click_project, analyze_problem_page, generate_solution_code, submit_code
    )

    browser = BrowserAutomationEngine(headless=False)

    try:
        await browser.start()
        print("Browser started")

        # Step 1: Login
        print("\n1. LOGGING IN...")
        login_result = await login_to_ebox(browser)
        print(f"   Result: {login_result.get('success')}")
        if not login_result.get("success"):
            return

        # Step 2: Navigate to course
        print("\n2. NAVIGATING TO COURSE...")
        course_result = await navigate_to_course(browser, "Differential Equations And Complex Analysis")
        print(f"   Result: {course_result.get('success')}")
        if not course_result.get("success"):
            return

        await asyncio.sleep(2)

        # Step 3: Click topic
        print("\n3. CLICKING TOPIC...")
        topic_result = await click_topic(browser, "Solution Of Ordinary Differential")
        print(f"   Result: {topic_result.get('success')}")
        if not topic_result.get("success"):
            print("   Trying alternative...")
            # Try clicking directly
            page = browser.page
            await page.get_by_text("Solution Of Ordinary", exact=False).first.click()
            await asyncio.sleep(1)

        # Step 4: Click section
        print("\n4. CLICKING SECTION (i-Design)...")
        section_result = await click_section(browser, "i-Design")
        print(f"   Result: {section_result.get('success')}")
        if not section_result.get("success"):
            print("   Trying alternative...")
            page = browser.page
            await page.get_by_text("i-Design").first.click()
            await asyncio.sleep(1)

        # Step 5: Click project
        print("\n5. CLICKING PROJECT...")
        project_result = await click_project(browser)
        print(f"   Result: {project_result.get('success')}")
        if not project_result.get("success"):
            print("   Trying alternative...")
            page = browser.page
            await page.get_by_text("Project", exact=False).first.click()
            await asyncio.sleep(2)

        # Step 6: Analyze problem
        print("\n6. ANALYZING PROBLEM PAGE...")
        problem_result = await analyze_problem_page(browser)
        print(f"   Result: {problem_result.get('success')}")
        if problem_result.get("success"):
            problem = problem_result["problem"]
            # Use ASCII-safe printing
            title = problem.get('problem_title', 'N/A')[:60].encode('ascii', 'replace').decode('ascii')
            lang = problem.get('programming_language', 'N/A')
            inp = problem.get('input_format', 'N/A')[:60].encode('ascii', 'replace').decode('ascii')
            print(f"   Title: {title}...")
            print(f"   Language: {lang}")
            print(f"   Input format: {inp}...")

        # Step 7: Generate solution code
        print("\n7. GENERATING SOLUTION CODE...")
        if problem_result.get("success"):
            solution_result = await generate_solution_code(problem_result["problem"])
            print(f"   Result: {solution_result.get('success')}")
            if solution_result.get("success"):
                print(f"   Code length: {len(solution_result.get('code', ''))} chars")
                print(f"   Command args: {solution_result.get('command_args', 'None')}")
                expl = solution_result.get('explanation', 'N/A')[:100].encode('ascii', 'replace').decode('ascii')
                print(f"   Explanation: {expl}...")

                # Step 8: Submit code
                print("\n8. SUBMITTING CODE...")
                submit_result = await submit_code(
                    browser,
                    solution_result["code"],
                    solution_result.get("command_args", "")
                )
                print(f"   Result: {submit_result.get('success')}")
                if not submit_result.get("success"):
                    print(f"   Error: {submit_result.get('error')}")

        print("\n" + "=" * 60)
        print("TEST COMPLETE - Browser staying open 60 seconds")
        print("=" * 60)
        await asyncio.sleep(60)

    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        await asyncio.sleep(30)

    finally:
        await browser.close()
        print("Browser closed")


if __name__ == "__main__":
    asyncio.run(test_full_flow())

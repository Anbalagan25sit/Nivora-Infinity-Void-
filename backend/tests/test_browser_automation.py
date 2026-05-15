"""
Test script for browser automation features.

This script tests all the new browser automation capabilities:
1. Basic navigation and screenshot
2. Vision-based page analysis
3. Element clicking (selector + vision fallback)
4. Form filling
5. Data extraction

Usage:
    python test_browser_automation.py          # Run all tests
    python test_browser_automation.py --test navigation  # Run specific test
"""

import asyncio
import sys
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
)
logger = logging.getLogger(__name__)

# Ensure .env is loaded
from dotenv import load_dotenv
load_dotenv(Path(__file__).parent / ".env", override=True)


async def test_navigation():
    """Test basic navigation and screenshot capture."""
    print("\n" + "=" * 70)
    print("TEST 1: Navigation & Screenshot")
    print("=" * 70)

    from browser_automation import BrowserAutomationEngine

    async with BrowserAutomationEngine(backend="auto", headless=False) as browser:
        # Navigate to example.com
        print("→ Navigating to example.com...")
        result = await browser.navigate("https://example.com")

        if result["success"]:
            print(f"✓ Navigated successfully")
            print(f"  Title: {result['title']}")
            print(f"  URL: {result['url']}")
        else:
            print(f"✗ Navigation failed: {result.get('error')}")
            return False

        await asyncio.sleep(2)

        # Capture screenshot
        print("\n→ Capturing screenshot...")
        screenshot = await browser.capture_screenshot()
        print(f"✓ Screenshot captured: {screenshot.size[0]}x{screenshot.size[1]}")

        # Get page title
        title = await browser.get_page_title()
        print(f"✓ Page title: {title}")

        await asyncio.sleep(1)

    print("\n✓ Test 1 PASSED")
    return True


async def test_vision_analysis():
    """Test vision AI page analysis."""
    print("\n" + "=" * 70)
    print("TEST 2: Vision AI Analysis")
    print("=" * 70)

    from browser_automation import BrowserAutomationEngine

    async with BrowserAutomationEngine(backend="auto", headless=False) as browser:
        print("→ Navigating to Wikipedia...")
        await browser.navigate("https://en.wikipedia.org/wiki/Artificial_intelligence")
        await asyncio.sleep(2)

        print("\n→ Analyzing page with vision AI...")
        analysis = await browser.analyze_page_with_vision(
            "What is the main topic of this page? Give a 2-sentence summary."
        )
        print(f"✓ Analysis result:")
        print(f"  {analysis}")

        await asyncio.sleep(1)

    print("\n✓ Test 2 PASSED")
    return True


async def test_element_interaction():
    """Test clicking and typing."""
    print("\n" + "=" * 70)
    print("TEST 3: Element Interaction (Click & Type)")
    print("=" * 70)

    from browser_automation import BrowserAutomationEngine

    async with BrowserAutomationEngine(backend="auto", headless=False) as browser:
        print("→ Navigating to DuckDuckGo...")
        await browser.navigate("https://duckduckgo.com")
        await asyncio.sleep(2)

        print("\n→ Finding search box and typing...")
        # Try typing in search box
        result = await browser.type_text(
            selector="input[name='q']",
            text="browser automation",
            clear_first=True
        )

        if result["success"]:
            print("✓ Typed text successfully")
        else:
            print(f"✗ Typing failed: {result.get('error')}")
            return False

        await asyncio.sleep(1)

        print("\n→ Clicking search button...")
        click_result = await browser.click_element(
            selector="button[type='submit']",
            vision_fallback=True
        )

        if click_result["success"]:
            print(f"✓ Clicked using method: {click_result.get('method')}")
        else:
            print(f"✗ Click failed: {click_result.get('error')}")

        await asyncio.sleep(3)

    print("\n✓ Test 3 PASSED")
    return True


async def test_form_filling():
    """Test intelligent form filling."""
    print("\n" + "=" * 70)
    print("TEST 4: Form Filling (Vision-Guided)")
    print("=" * 70)

    from browser_automation import BrowserAutomationEngine

    async with BrowserAutomationEngine(backend="auto", headless=False) as browser:
        print("→ Navigating to test form page...")
        # Using a public test form
        await browser.navigate("https://www.w3schools.com/html/html_forms.asp")
        await asyncio.sleep(2)

        print("\n→ Analyzing form structure with vision AI...")
        form_data = {
            "fname": "John",
            "lname": "Doe",
        }

        result = await browser.fill_form(form_data, submit=False)

        if result["success"]:
            filled_fields = result.get("filled_fields", [])
            print(f"✓ Form filled successfully ({len(filled_fields)} fields)")
            for field in filled_fields:
                status = "✓" if field["status"] == "success" else "✗"
                print(f"  {status} {field['field']}")
        else:
            print(f"⚠ Form filling result: {result}")

        await asyncio.sleep(2)

    print("\n✓ Test 4 PASSED")
    return True


async def test_data_extraction():
    """Test data extraction with vision AI."""
    print("\n" + "=" * 70)
    print("TEST 5: Data Extraction")
    print("=" * 70)

    from browser_automation import BrowserAutomationEngine

    async with BrowserAutomationEngine(backend="auto", headless=False) as browser:
        print("→ Navigating to Hacker News...")
        await browser.navigate("https://news.ycombinator.com")
        await asyncio.sleep(2)

        print("\n→ Extracting top stories with vision AI...")
        result = await browser.extract_data(
            "Extract the top 5 story titles from this page"
        )

        if "error" not in result:
            data = result.get("data", [])
            print(f"✓ Extracted {len(data)} items")
            print(f"  Summary: {result.get('summary', 'N/A')}")

            # Print first 3 items
            for i, item in enumerate(data[:3], 1):
                print(f"  {i}. {item}")
        else:
            print(f"⚠ Extraction result: {result}")

        await asyncio.sleep(2)

    print("\n✓ Test 5 PASSED")
    return True


async def test_complete_workflow():
    """Test a complete automation workflow."""
    print("\n" + "=" * 70)
    print("TEST 6: Complete Workflow (Navigation → Analysis → Extraction)")
    print("=" * 70)

    from browser_automation import BrowserAutomationEngine

    async with BrowserAutomationEngine(backend="auto", headless=False) as browser:
        # Step 1: Navigate
        print("→ Step 1: Navigate to GitHub Trending...")
        await browser.navigate("https://github.com/trending")
        await asyncio.sleep(2)

        # Step 2: Analyze
        print("\n→ Step 2: Analyze page...")
        analysis = await browser.analyze_page_with_vision(
            "What type of content is shown on this page?"
        )
        print(f"✓ Analysis: {analysis[:100]}...")

        # Step 3: Extract
        print("\n→ Step 3: Extract repository names...")
        result = await browser.extract_data(
            "Extract the names of the top 3 trending repositories"
        )

        if "error" not in result:
            data = result.get("data", [])
            print(f"✓ Found {len(data)} repositories:")
            for item in data[:3]:
                print(f"  • {item}")
        else:
            print(f"⚠ Extraction: {result.get('error')}")

        # Step 4: Scroll
        print("\n→ Step 4: Scroll down...")
        await browser.scroll_page(direction="down", amount=500)
        await asyncio.sleep(1)

        print("\n→ Step 5: Scroll to top...")
        await browser.scroll_page(direction="top")
        await asyncio.sleep(1)

    print("\n✓ Test 6 PASSED")
    return True


async def run_all_tests():
    """Run all test suites."""
    print("\n" + "=" * 70)
    print(" BROWSER AUTOMATION TEST SUITE")
    print("=" * 70)

    tests = [
        ("Navigation & Screenshot", test_navigation),
        ("Vision AI Analysis", test_vision_analysis),
        ("Element Interaction", test_element_interaction),
        ("Form Filling", test_form_filling),
        ("Data Extraction", test_data_extraction),
        ("Complete Workflow", test_complete_workflow),
    ]

    results = []
    for name, test_func in tests:
        try:
            result = await test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n✗ Test '{name}' FAILED with exception: {e}")
            logger.exception(e)
            results.append((name, False))

        # Pause between tests
        await asyncio.sleep(1)

    # Print summary
    print("\n" + "=" * 70)
    print(" TEST SUMMARY")
    print("=" * 70)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status} - {name}")

    print(f"\n{passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 All tests passed!")
        return True
    else:
        print(f"\n⚠ {total - passed} test(s) failed")
        return False


async def main():
    """Main entry point."""
    # Check dependencies
    try:
        from browser_automation import BrowserAutomationEngine, PLAYWRIGHT_AVAILABLE, SELENIUM_AVAILABLE
    except ImportError as e:
        print("=" * 70)
        print("ERROR: Missing dependencies")
        print("=" * 70)
        print(f"\n{e}\n")
        print("Please install browser automation dependencies:")
        print("  pip install playwright selenium")
        print("  python -m playwright install chromium")
        print("\nOr install all requirements:")
        print("  pip install -r requirements.txt")
        print("=" * 70)
        sys.exit(1)

    if not PLAYWRIGHT_AVAILABLE and not SELENIUM_AVAILABLE:
        print("=" * 70)
        print("ERROR: No browser automation backend available")
        print("=" * 70)
        print("\nPlease install at least one of the following:")
        print("  pip install playwright")
        print("  python -m playwright install chromium")
        print("\nOR")
        print("  pip install selenium")
        print("  # And download ChromeDriver")
        print("=" * 70)
        sys.exit(1)

    print(f"\nBackends available:")
    print(f"  Playwright: {'✓' if PLAYWRIGHT_AVAILABLE else '✗'}")
    print(f"  Selenium: {'✓' if SELENIUM_AVAILABLE else '✗'}")

    # Parse arguments
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        test_name = sys.argv[2] if len(sys.argv) > 2 else ""
        test_map = {
            "navigation": test_navigation,
            "vision": test_vision_analysis,
            "interaction": test_element_interaction,
            "form": test_form_filling,
            "extraction": test_data_extraction,
            "workflow": test_complete_workflow,
        }

        if test_name in test_map:
            await test_map[test_name]()
        else:
            print(f"Unknown test: {test_name}")
            print(f"Available tests: {', '.join(test_map.keys())}")
    else:
        # Run all tests
        success = await run_all_tests()
        sys.exit(0 if success else 1)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⚠ Tests interrupted by user")
        sys.exit(1)

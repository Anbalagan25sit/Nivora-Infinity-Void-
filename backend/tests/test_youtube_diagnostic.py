"""
Simple YouTube Automation Test (No LiveKit Required)

This tests the vision AI and browser automation directly.
"""

import asyncio
import sys
import os

# Fix Windows encoding issues
if sys.platform == "win32":
    import codecs
    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test that all imports work."""
    print("Testing imports...")
    try:
        import computer_use as _cu
        print("  ✓ computer_use imported")

        from aws_config import bedrock_client, bedrock_model
        print("  ✓ aws_config imported")

        import pyautogui
        print("  ✓ pyautogui imported")

        from PIL import Image
        print("  ✓ PIL imported")

        return True
    except Exception as e:
        print(f"  ✗ Import failed: {e}")
        return False


def test_aws_credentials():
    """Test AWS Bedrock access."""
    print("\nTesting AWS Bedrock access...")
    try:
        from aws_config import bedrock_client, bedrock_model

        client = bedrock_client()
        model = bedrock_model()

        print(f"  ✓ AWS Bedrock client created")
        print(f"  ✓ Model: {model}")

        return True
    except Exception as e:
        print(f"  ✗ AWS test failed: {e}")
        return False


def test_screen_capture():
    """Test screen capture."""
    print("\nTesting screen capture...")
    try:
        import computer_use as _cu

        img = _cu.capture_screen()
        print(f"  ✓ Screen captured: {img.size[0]}x{img.size[1]}")

        return True
    except Exception as e:
        print(f"  ✗ Screen capture failed: {e}")
        return False


async def test_vision_simple():
    """Test vision AI with a simple query."""
    print("\nTesting AWS Nova Pro vision...")
    try:
        import computer_use as _cu

        # Capture screen
        img = _cu.capture_screen()

        # Simple vision test
        prompt = """
Describe what you see on this screen in one sentence.
Return JSON: {"description": "<your description>"}
IMPORTANT: Return ONLY valid JSON.
"""

        print("  Sending to AWS Nova Pro...")
        response = _cu.analyze_screen(prompt, img, temperature=0.1, backend="aws")

        if "error" in response:
            print(f"  ✗ Vision error: {response.get('error')}")
            print(f"    Raw: {response.get('raw', '')[:200]}")
            return False

        description = response.get("description", "No description")
        print(f"  ✓ Vision response: {description}")

        return True
    except Exception as e:
        print(f"  ✗ Vision test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_youtube_search():
    """Test opening YouTube search (without clicking)."""
    print("\nTesting YouTube search...")
    try:
        import webbrowser
        from urllib.parse import quote_plus

        query = "lofi hip hop radio live"
        encoded_query = quote_plus(query)
        url = f"https://www.youtube.com/results?search_query={encoded_query}&sp=EgJAAQ%253D%253D"

        print(f"  Opening: {url}")
        webbrowser.open(url)

        print("  ✓ YouTube search opened in browser")
        print("  (Check your browser to verify it worked)")

        return True
    except Exception as e:
        print(f"  ✗ YouTube search failed: {e}")
        return False


async def main():
    """Run all tests."""
    print("="*70)
    print("YOUTUBE AUTOMATION - DIAGNOSTIC TEST")
    print("="*70)

    results = []

    # Test 1: Imports
    results.append(("Imports", test_imports()))

    # Test 2: AWS credentials
    results.append(("AWS Credentials", test_aws_credentials()))

    # Test 3: Screen capture
    results.append(("Screen Capture", test_screen_capture()))

    # Test 4: Vision AI
    results.append(("Vision AI", await test_vision_simple()))

    # Test 5: YouTube search
    results.append(("YouTube Search", await test_youtube_search()))

    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)

    for test_name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{test_name:.<40} {status}")

    total_passed = sum(1 for _, passed in results if passed)
    total_tests = len(results)

    print(f"\nPassed: {total_passed}/{total_tests}")

    if total_passed == total_tests:
        print("\n🎉 All tests passed! YouTube automation is ready to use.")
        print("\nNext step: Integrate with your Nivora agent")
        print("Add the youtube_search_and_play tool to your agent's tool list.")
    else:
        print("\n⚠️  Some tests failed. Please check the errors above.")

        if not results[1][1]:  # AWS failed
            print("\n💡 Tip: Make sure your .env file has:")
            print("   AWS_ACCESS_KEY_ID=...")
            print("   AWS_SECRET_ACCESS_KEY=...")
            print("   AWS_REGION=us-east-1")
            print("   AWS_BEDROCK_MODEL=amazon.nova-pro-v1:0")


if __name__ == "__main__":
    asyncio.run(main())

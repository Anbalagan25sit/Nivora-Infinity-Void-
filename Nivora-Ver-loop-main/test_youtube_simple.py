"""
Minimal YouTube Test - Just open and search
No vision AI needed for this test
"""

import webbrowser
import time
from urllib.parse import quote_plus

def test_youtube_open():
    """Test 1: Just open YouTube search"""
    print("Test 1: Opening YouTube...")

    query = "lofi hip hop radio live"
    encoded = quote_plus(query)
    url = f"https://www.youtube.com/results?search_query={encoded}&sp=EgJAAQ%253D%253D"

    print(f"URL: {url}")
    webbrowser.open(url)

    print("SUCCESS: YouTube opened in browser!")
    print("Check your browser - you should see live stream results for 'lofi hip hop radio'")
    return True

def test_aws_bedrock():
    """Test 2: Check AWS Bedrock access"""
    print("\nTest 2: Testing AWS Bedrock...")

    try:
        from aws_config import bedrock_client, bedrock_model

        client = bedrock_client()
        model = bedrock_model()

        print(f"SUCCESS: AWS Bedrock client created")
        print(f"Model: {model}")
        return True

    except Exception as e:
        print(f"FAILED: {e}")
        return False

def test_computer_use():
    """Test 3: Test computer_use module"""
    print("\nTest 3: Testing computer_use module...")

    try:
        import computer_use as cu

        # Test screen capture
        img = cu.capture_screen()
        width, height = img.size

        print(f"SUCCESS: Screen captured ({width}x{height})")
        return True

    except Exception as e:
        print(f"FAILED: {e}")
        return False

if __name__ == "__main__":
    print("="*60)
    print("YOUTUBE AUTOMATION - SIMPLE TEST")
    print("="*60)
    print()

    results = []

    # Run tests
    results.append(("YouTube Open", test_youtube_open()))

    time.sleep(2)  # Wait for browser

    results.append(("AWS Bedrock", test_aws_bedrock()))
    results.append(("Computer Use", test_computer_use()))

    # Summary
    print("\n" + "="*60)
    print("RESULTS:")
    print("="*60)

    for name, passed in results:
        status = "PASS" if passed else "FAIL"
        print(f"{name}: {status}")

    passed_count = sum(1 for _, p in results if p)
    total = len(results)

    print(f"\nPassed: {passed_count}/{total}")

    if passed_count == total:
        print("\nAll tests passed!")
        print("\nYour YouTube automation is ready!")
        print("Next: Run your Nivora agent and say:")
        print("  'play recently repo tamil gaming live'")
    else:
        print("\nSome tests failed. Check errors above.")

"""
Simple E-Box Automation Test (Windows Compatible)
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(__file__))

def test_imports():
    """Test if E-Box automation can be imported."""
    print("=" * 60)
    print("E-Box Automation Test Suite")
    print("=" * 60)

    # Test 1: Import check
    print("\n1. Testing imports...")
    try:
        from ebox_automation import (
            complete_ebox_course,
            ebox_help_with_problem,
            extract_course_and_topic,
            EBOX_USERNAME,
            EBOX_PASSWORD,
            COURSE_MAPPINGS
        )
        print("   OK - All imports successful")
        return True
    except ImportError as e:
        print(f"   FAIL - Import failed: {e}")
        return False


def test_credentials():
    """Test credentials are configured."""
    print("\n2. Testing credentials...")
    from ebox_automation import EBOX_USERNAME, EBOX_PASSWORD

    if EBOX_USERNAME == "SIT25CS170" and EBOX_PASSWORD == "SIT25CS170":
        print(f"   OK - Credentials configured: {EBOX_USERNAME}")
        return True
    else:
        print(f"   FAIL - Unexpected credentials: {EBOX_USERNAME}")
        return False


def test_parsing():
    """Test natural language parsing."""
    print("\n3. Testing natural language parsing...")
    from ebox_automation import extract_course_and_topic

    test_cases = [
        ("finish differential equations", {"course": "Differential Equations And Complex Analysis"}),
        ("complete biology course", {"course": "Biology for Engineers"}),
        ("solve solution of ordinary differential equations", {"topic": "Solution Of Ordinary Differential Equations"}),
    ]

    all_pass = True
    for input_text, expected_keys in test_cases:
        result = extract_course_and_topic(input_text)
        matches = all(result.get(k) == v for k, v in expected_keys.items())

        if matches:
            print(f"   OK - '{input_text}'")
        else:
            print(f"   FAIL - '{input_text}' -> Expected {expected_keys}, got {result}")
            all_pass = False

    return all_pass


def test_tool_registration():
    """Test tool registration in tools.py."""
    print("\n4. Testing tool registration...")
    try:
        from tools import ALL_TOOLS
        tool_names = [t.id if hasattr(t, 'id') else str(t) for t in ALL_TOOLS]

        # Only check for the main tools (save/clear login removed since E-Box doesn't support persistent sessions)
        tools_to_check = [
            "complete_ebox_course",
            "ebox_help_with_problem",
        ]

        all_found = True
        for tool_name in tools_to_check:
            if tool_name in tool_names:
                print(f"   OK - {tool_name} registered in ALL_TOOLS")
            else:
                print(f"   FAIL - {tool_name} not found in ALL_TOOLS")
                all_found = False

        return all_found

    except Exception as e:
        print(f"   FAIL - Tool registration check failed: {e}")
        return False


def test_dependencies():
    """Test required dependencies."""
    print("\n5. Testing dependencies...")

    try:
        import boto3
        print("   OK - boto3 (AWS) available")
        aws_ok = True
    except ImportError:
        print("   FAIL - boto3 not installed")
        aws_ok = False

    try:
        from browser_automation import BrowserAutomationEngine
        print("   OK - BrowserAutomationEngine available")
        browser_ok = True
    except ImportError as e:
        print(f"   FAIL - Browser automation not available: {e}")
        browser_ok = False

    return aws_ok and browser_ok


def main():
    """Run all tests."""
    print("\n")
    print("*" * 60)
    print(" E-BOX AUTOMATION TEST SUITE")
    print(" Testing Nivora's Course Automation")
    print("*" * 60)

    results = []

    # Run tests
    results.append(("Imports", test_imports()))
    results.append(("Credentials", test_credentials()))
    results.append(("Parsing", test_parsing()))
    results.append(("Tool Registration", test_tool_registration()))
    results.append(("Dependencies", test_dependencies()))

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)

    for name, passed in results:
        status = "PASS" if passed else "FAIL"
        print(f"  {name}: {status}")

    all_passed = all(result[1] for result in results)

    print("\n" + "=" * 60)
    if all_passed:
        print("ALL TESTS PASSED!")
    else:
        print("SOME TESTS FAILED - Check output above")

    print("\nTo use:")
    print("  1. Run: python agent.py")
    print("  2. Connect via LiveKit client")
    print("  3. Say: 'finish differential equations' or 'solve this problem'")
    print("\n" + "=" * 60 + "\n")

    return 0 if all_passed else 1


if __name__ == "__main__":
    exit(main())

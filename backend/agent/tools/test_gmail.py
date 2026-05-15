"""
Gmail Tool Test Script
======================
Quick tests for Gmail functionality.

Usage:
    python agent/tools/test_gmail.py
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from agent.tools.gmail_tool import (
    send_email,
    read_emails,
    search_emails,
    reply_to_email,
    get_email_summary,
    gmail_service,
    TOKEN_FILE
)


def test_authentication():
    """Test if authentication is set up."""
    print("\n" + "=" * 60)
    print("TEST 1: Authentication")
    print("=" * 60)

    if not TOKEN_FILE.exists():
        print("[X] FAIL: No token file found")
        print(f"   Expected location: {TOKEN_FILE}")
        print("   Run: python agent/tools/setup_gmail.py")
        return False

    try:
        service = gmail_service.get_service()
        profile = service.users().getProfile(userId='me').execute()
        email = profile.get('emailAddress', 'Unknown')
        print(f"[OK] PASS: Authenticated as {email}")
        return True
    except Exception as e:
        print(f"[X] FAIL: {e}")
        return False


def test_email_summary():
    """Test get_email_summary function."""
    print("\n" + "=" * 60)
    print("TEST 2: Email Summary")
    print("=" * 60)

    try:
        result = get_email_summary()
        print("[OK] PASS:")
        print(result)
        return True
    except Exception as e:
        print(f"[X] FAIL: {e}")
        return False


def test_read_unread():
    """Test reading unread emails."""
    print("\n" + "=" * 60)
    print("TEST 3: Read Unread Emails")
    print("=" * 60)

    try:
        result = read_emails(max_results=3, query="is:unread")
        print("[OK] PASS:")
        print(result)
        return True
    except Exception as e:
        print(f"[X] FAIL: {e}")
        return False


def test_search():
    """Test search functionality."""
    print("\n" + "=" * 60)
    print("TEST 4: Search Emails")
    print("=" * 60)

    # Search for recent emails (last 7 days)
    try:
        result = search_emails(query="newer_than:7d", max_results=5)
        print("[OK] PASS:")
        print(result)
        return True
    except Exception as e:
        print(f"[X] FAIL: {e}")
        return False


def test_send_email_dry_run():
    """Don't actually send - just validate parameters."""
    print("\n" + "=" * 60)
    print("TEST 5: Send Email (Dry Run)")
    print("=" * 60)

    # Just validate the function exists and has correct signature
    import inspect
    sig = inspect.signature(send_email)
    params = list(sig.parameters.keys())

    expected_params = ['to', 'subject', 'body']
    if params == expected_params:
        print(f"[OK] PASS: Function signature correct: {params}")
        print("   (Not sending test email - use manually if needed)")
        return True
    else:
        print(f"❌ FAIL: Expected params {expected_params}, got {params}")
        return False


def test_reply_validation():
    """Validate reply function."""
    print("\n" + "=" * 60)
    print("TEST 6: Reply Function (Validation)")
    print("=" * 60)

    import inspect
    sig = inspect.signature(reply_to_email)
    params = list(sig.parameters.keys())

    expected_params = ['thread_id', 'body']
    if params == expected_params:
        print(f"[OK] PASS: Function signature correct: {params}")
        print("   (Not sending test reply - use manually if needed)")
        return True
    else:
        print(f"❌ FAIL: Expected params {expected_params}, got {params}")
        return False


def main():
    print("\n")
    print("=" * 60)
    print("  Gmail Tool Test Suite for Nivora")
    print("=" * 60)

    tests = [
        ("Authentication", test_authentication),
        ("Email Summary", test_email_summary),
        ("Read Unread", test_read_unread),
        ("Search", test_search),
        ("Send Email", test_send_email_dry_run),
        ("Reply", test_reply_validation),
    ]

    results = []
    for name, test_func in tests:
        try:
            passed = test_func()
            results.append((name, passed))
        except Exception as e:
            print(f"\n[X] EXCEPTION in {name}: {e}")
            results.append((name, False))

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "[OK] PASS" if result else "[X] FAIL"
        print(f"{status}: {name}")

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        print("\n[SUCCESS] All tests passed! Gmail tool is ready to use.")
        return 0
    else:
        print(f"\n[WARNING] {total - passed} test(s) failed. Check errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())

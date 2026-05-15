"""
Notion Tool Test Script
=======================
Tests for Notion API functionality.

Usage (from project root):
    python agent/tools/test_notion.py
"""

import sys
from pathlib import Path

# Add to Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from agent.tools.notion_tool import (
    search_notion,
    notion_service,
    NOTION_API_KEY
)


def test_api_key():
    """Test if API key is configured."""
    print("\n" + "=" * 60)
    print("TEST 1: API Key Configuration")
    print("=" * 60)

    if not NOTION_API_KEY:
        print("[X] FAIL: NOTION_API_KEY not found in .env")
        print("    Add to .env: NOTION_API_KEY=secret_xxxxx")
        return False

    print(f"[OK] PASS: API key is set")
    print(f"    Starts with: {NOTION_API_KEY[:15]}...")
    return True


def test_connection():
    """Test Notion API connection."""
    print("\n" + "=" * 60)
    print("TEST 2: API Connection")
    print("=" * 60)

    try:
        response = notion_service.client.search(query="", page_size=1)
        print("[OK] PASS: Successfully connected to Notion API")
        return True
    except Exception as e:
        print(f"[X] FAIL: {e}")
        return False


def test_search():
    """Test search functionality."""
    print("\n" + "=" * 60)
    print("TEST 3: Search Function")
    print("=" * 60)

    try:
        result = search_notion("")
        print("[OK] PASS:")
        print(result)
        return True
    except Exception as e:
        print(f"[X] FAIL: {e}")
        return False


def test_accessible_pages():
    """Test access to pages."""
    print("\n" + "=" * 60)
    print("TEST 4: Accessible Pages")
    print("=" * 60)

    try:
        response = notion_service.client.search(query="", page_size=10)
        results = response.get('results', [])

        if not results:
            print("[!] WARNING: No pages accessible")
            print("    Share some pages with your integration:")
            print("    1. Open page in Notion")
            print("    2. Click '...' > 'Add connections'")
            print("    3. Select your integration")
            return False

        print(f"[OK] PASS: {len(results)} pages/databases accessible")

        # Show first few
        for i, item in enumerate(results[:5], 1):
            item_type = item.get('object', 'unknown')
            item_id = item.get('id', '')

            # Get title
            if item_type == 'page':
                properties = item.get('properties', {})
                title = 'Untitled'
                for prop_name, prop in properties.items():
                    if prop.get('type') == 'title':
                        rich_text = prop.get('title', [])
                        if rich_text:
                            title = rich_text[0].get('plain_text', 'Untitled')
                        break
            elif item_type == 'database':
                title_obj = item.get('title', [])
                title = title_obj[0].get('plain_text', 'Untitled') if title_obj else 'Untitled'
            else:
                title = 'Unknown'

            print(f"    {i}. {title} ({item_type})")
            print(f"       ID: {item_id}")

        return True

    except Exception as e:
        print(f"[X] FAIL: {e}")
        return False


def test_function_signatures():
    """Validate function signatures."""
    print("\n" + "=" * 60)
    print("TEST 5: Function Signatures")
    print("=" * 60)

    import inspect
    from agent.tools.notion_tool import (
        create_notion_page,
        read_notion_page,
        add_to_notion_database,
        update_notion_page,
        save_agent_output
    )

    functions = [
        ("create_notion_page", create_notion_page, ['title', 'content', 'parent_page_id']),
        ("search_notion", search_notion, ['query']),
        ("read_notion_page", read_notion_page, ['page_id_or_url']),
        ("add_to_notion_database", add_to_notion_database, ['database_id', 'properties']),
        ("update_notion_page", update_notion_page, ['page_id', 'content']),
        ("save_agent_output", save_agent_output, ['title', 'content']),
    ]

    all_passed = True
    for name, func, expected_params in functions:
        sig = inspect.signature(func)
        params = list(sig.parameters.keys())

        if params == expected_params:
            print(f"[OK] {name}: {params}")
        else:
            print(f"[X] {name}: Expected {expected_params}, got {params}")
            all_passed = False

    return all_passed


def main():
    print("\n")
    print("=" * 60)
    print("  Notion Tool Test Suite for Nivora")
    print("=" * 60)

    tests = [
        ("API Key", test_api_key),
        ("Connection", test_connection),
        ("Search", test_search),
        ("Accessible Pages", test_accessible_pages),
        ("Function Signatures", test_function_signatures),
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
        print("\n[SUCCESS] All tests passed! Notion tool is ready to use.")
        print("\nNext steps:")
        print("1. Share pages with your integration in Notion")
        print("2. Add NOTION_TOOLS to agent configuration")
        print("3. Try voice command: 'Search Notion for my notes'")
        return 0
    else:
        print(f"\n[WARNING] {total - passed} test(s) failed.")

        if not NOTION_API_KEY:
            print("\nAction required:")
            print("1. Create integration at https://www.notion.so/my-integrations")
            print("2. Copy integration token")
            print("3. Add to .env: NOTION_API_KEY=secret_xxxxx")

        return 1


if __name__ == "__main__":
    sys.exit(main())

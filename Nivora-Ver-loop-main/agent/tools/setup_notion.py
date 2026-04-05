"""
Notion Tool Setup Script
=========================
One-time setup to test Notion API connection.

Prerequisites:
1. Create Notion integration at https://www.notion.so/my-integrations
2. Copy integration token to .env as NOTION_API_KEY
3. Share pages/databases with your integration

Usage (from project root):
    python agent/tools/setup_notion.py
"""

import os
import sys
from pathlib import Path

# Add to Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from notion_client import Client


ENV_FILE = Path(".env")
NOTION_API_KEY = os.getenv("NOTION_API_KEY")


def check_env_file():
    """Check if .env file exists and has NOTION_API_KEY."""
    if not ENV_FILE.exists():
        print("[X] .env file not found in project root")
        print(f"    Expected location: {ENV_FILE.absolute()}")
        print()
        print("Create .env file with:")
        print("NOTION_API_KEY=secret_xxxxx")
        return False

    if not NOTION_API_KEY:
        print("[X] NOTION_API_KEY not found in .env")
        print()
        print("Add to .env:")
        print("NOTION_API_KEY=secret_xxxxx")
        print()
        print("Get your key from:")
        print("https://www.notion.so/my-integrations")
        return False

    print(f"[OK] Found .env file: {ENV_FILE.absolute()}")
    print(f"[OK] NOTION_API_KEY is set (starts with: {NOTION_API_KEY[:10]}...)")
    return True


def test_connection():
    """Test Notion API connection."""
    print("\nTesting Notion API connection...")

    try:
        client = Client(auth=NOTION_API_KEY)

        # Search for pages to test connection
        response = client.search(query="", page_size=10)
        results = response.get('results', [])

        print(f"[OK] Connected to Notion API successfully!")
        print(f"     Your integration has access to {len(results)} pages/databases")

        if results:
            print("\n     Accessible pages:")
            for i, item in enumerate(results[:5], 1):
                item_type = item.get('object', 'unknown')
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

                print(f"     {i}. {title} ({item_type})")

            if len(results) > 5:
                print(f"     ... and {len(results) - 5} more")

        else:
            print("\n     [!] No pages accessible yet!")
            print("     Share some Notion pages with your integration:")
            print("     1. Open a page in Notion")
            print("     2. Click '...' menu > 'Add connections'")
            print("     3. Select your integration")

        return True

    except Exception as e:
        print(f"[X] Connection failed: {e}")
        print("\nTroubleshooting:")
        print("1. Verify your API key is correct")
        print("2. Check that your integration is active")
        print("3. Share at least one page with your integration")
        return False


def main():
    print("=" * 60)
    print("Notion API Setup for Nivora")
    print("=" * 60)
    print()

    # Check environment
    if not check_env_file():
        return 1

    # Test connection
    if not test_connection():
        return 1

    print()
    print("=" * 60)
    print("[SUCCESS] Notion integration is ready!")
    print("=" * 60)
    print()
    print("Next steps:")
    print("1. Add NOTION_TOOLS to your agent configuration")
    print("2. Try voice command: 'Search Notion for my notes'")
    print()
    print("Optional: Set NOTION_DEFAULT_DATABASE_ID in .env for quick task adding")
    print("Optional: Create 'Nivora Notes' page and share it for agent output logging")

    return 0


if __name__ == "__main__":
    sys.exit(main())

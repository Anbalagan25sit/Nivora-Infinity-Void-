"""
Quick Test for YouTube Automation

This script demonstrates the YouTube automation features.
Run this to test the vision-guided YouTube playback.
"""

import asyncio
from unittest.mock import MagicMock

# Mock LiveKit context for standalone testing
class MockRoom:
    name = "test-session"

class MockContext:
    room = MockRoom()

async def test_youtube_automation():
    """Test YouTube automation features."""
    print("="*60)
    print("YOUTUBE AUTOMATION TEST")
    print("="*60)

    # Import tools
    from youtube_automation import (
        youtube_search_and_play,
        youtube_control_playback,
        youtube_find_live_streams
    )

    context = MockContext()

    print("\n1. Testing: Search and play live stream")
    print("-" * 60)
    print("Query: 'lofi hip hop radio live'")
    print("\nThis will:")
    print("  - Open YouTube in your browser")
    print("  - Search for lofi hip hop live streams")
    print("  - Use vision AI to find the best match")
    print("  - Automatically click and play")
    print("\nStarting in 3 seconds...")

    await asyncio.sleep(3)

    result = await youtube_search_and_play(
        context,
        query="lofi hip hop radio live",
        prefer_live=True
    )

    print("\nResult:")
    print(result)

    print("\n" + "="*60)
    print("Test complete!")
    print("="*60)

    print("\nTry these queries with Nivora:")
    print("  - 'play recently repo tamil gaming live'")
    print("  - 'play latest MrBeast video'")
    print("  - 'find gaming live streams'")
    print("  - 'play lofi hip hop radio'")


if __name__ == "__main__":
    print("YouTube Automation Test Script")
    print("This will open YouTube in your browser and test vision-guided playback.\n")

    response = input("Ready to test? (y/n): ")
    if response.lower() == 'y':
        asyncio.run(test_youtube_automation())
    else:
        print("Test cancelled.")
        print("\nYou can still use these features with Nivora by saying:")
        print("  'play recently repo tamil gaming live'")

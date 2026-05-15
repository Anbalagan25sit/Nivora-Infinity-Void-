#!/usr/bin/env python3
"""
Tool Validation Script
Tests all tools for common issues and ensures they're working correctly.
"""

import sys
import os
import asyncio
import traceback
from typing import List, Tuple

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

def test_imports() -> List[Tuple[str, bool, str]]:
    """Test all module imports."""
    results = []

    modules = [
        'tools',
        'spotify_api',
        'spotify_control',
        'agent',
        'prompts',
        'config',
        'computer_use',
        'screen_share',
        'edge_tts_plugin',
    ]

    for module in modules:
        try:
            __import__(module)
            results.append((module, True, "OK"))
        except Exception as e:
            results.append((module, False, str(e)))

    return results


def test_spotify_api() -> List[Tuple[str, bool, str]]:
    """Test Spotify API functions."""
    results = []

    try:
        import spotify_api

        # Test configuration
        is_conf = spotify_api.is_configured()
        results.append(("Spotify configured", is_conf, "OK" if is_conf else "No credentials"))

        # Test function existence
        functions = ['play', 'pause', 'next_track', 'previous_track',
                    'toggle_shuffle', 'toggle_repeat', 'search', 'get_current_playback']

        for func in functions:
            exists = hasattr(spotify_api, func)
            results.append((f"spotify_api.{func}", exists, "OK" if exists else "MISSING"))

    except Exception as e:
        results.append(("Spotify API test", False, str(e)))

    return results


def test_tools_count() -> List[Tuple[str, bool, str]]:
    """Test tool counts."""
    results = []

    try:
        import tools

        total = len(tools.ALL_TOOLS)
        results.append(("Total tools", total > 0, f"{total} tools loaded"))

        spotify_tools = len(tools.ALL_SPOTIFY_TOOLS)
        results.append(("Spotify tools", spotify_tools > 0, f"{spotify_tools} tools"))

        social_tools = len(tools.SOCIAL_TOOLS)
        results.append(("Social tools", social_tools >= 0, f"{social_tools} tools"))

    except Exception as e:
        results.append(("Tools count", False, str(e)))

    return results


def test_critical_tools() -> List[Tuple[str, bool, str]]:
    """Test critical tool functions exist."""
    results = []

    try:
        import tools

        tool_names = [tools._get_tool_name(t) for t in tools.ALL_TOOLS]

        critical = [
            'spotify_play',
            'spotify_control',
            'play_youtube_video',
            'open_website',
            'web_search',
            'send_email',
            'read_emails',
            'system_control',
            'take_note',
            'describe_screen_share',
        ]

        for tool in critical:
            exists = tool in tool_names
            results.append((f"Tool: {tool}", exists, "OK" if exists else "MISSING"))

    except Exception as e:
        results.append(("Critical tools", False, str(e)))

    return results


def test_env_vars() -> List[Tuple[str, bool, str]]:
    """Test environment variables."""
    results = []

    env_vars = {
        'AWS_ACCESS_KEY_ID': 'Required for AWS Bedrock',
        'AWS_SECRET_ACCESS_KEY': 'Required for AWS Bedrock',
        'AWS_REGION': 'Optional (defaults to us-east-1)',
        'LIVEKIT_URL': 'Required for LiveKit',
        'LIVEKIT_API_KEY': 'Required for LiveKit',
        'LIVEKIT_API_SECRET': 'Required for LiveKit',
        'GROQ_API_KEY': 'Required for STT (Groq Whisper)',
        'SPOTIFY_CLIENT_ID': 'Optional (for Spotify API)',
        'SPOTIFY_CLIENT_SECRET': 'Optional (for Spotify API)',
        'SPOTIFY_REFRESH_TOKEN': 'Optional (for Spotify API)',
    }

    for var, desc in env_vars.items():
        value = os.getenv(var)
        exists = bool(value and value.strip())
        status = "OK" if exists else "MISSING"
        results.append((f"ENV: {var}", exists, f"{status} - {desc}"))

    return results


async def test_tool_execution() -> List[Tuple[str, bool, str]]:
    """Test actual tool execution (safe tests only)."""
    results = []

    try:
        from tools import web_search, open_website, get_weather
        from livekit.agents import RunContext

        # Create a mock context
        class MockContext:
            pass

        ctx = MockContext()

        # Test 1: Web search (read-only)
        try:
            result = await web_search(ctx, "test query")
            success = isinstance(result, str) and len(result) > 0
            results.append(("web_search execution", success, "OK" if success else "Empty result"))
        except Exception as e:
            results.append(("web_search execution", False, str(e)))

        # Test 2: Get weather (read-only)
        try:
            result = await get_weather(ctx, "London")
            success = isinstance(result, str) and "London" in result
            results.append(("get_weather execution", success, "OK" if success else "Invalid result"))
        except Exception as e:
            results.append(("get_weather execution", False, str(e)))

    except Exception as e:
        results.append(("Tool execution tests", False, str(e)))

    return results


def print_results(title: str, results: List[Tuple[str, bool, str]]):
    """Print test results."""
    print(f"\n{'=' * 80}")
    print(f"{title}")
    print('=' * 80)

    for test, success, message in results:
        icon = '[OK]' if success else '[FAIL]'
        status = 'PASS' if success else 'FAIL'
        print(f"{icon} {test:40s} {message}")


async def main():
    """Run all tests."""
    print("\n" + "=" * 80)
    print("NIVORA TOOL VALIDATION SUITE")
    print("=" * 80)

    all_results = []

    # Run all test suites
    tests = [
        ("Module Imports", test_imports),
        ("Spotify API", test_spotify_api),
        ("Tool Counts", test_tools_count),
        ("Critical Tools", test_critical_tools),
        ("Environment Variables", test_env_vars),
    ]

    for title, test_func in tests:
        results = test_func()
        print_results(title, results)
        all_results.extend(results)

    # Async tests
    print_results("Tool Execution Tests", await test_tool_execution())

    # Summary
    total = len(all_results)
    passed = sum(1 for _, success, _ in all_results if success)
    failed = total - passed

    print(f"\n{'=' * 80}")
    print(f"SUMMARY: {passed}/{total} tests passed ({failed} failed)")
    print('=' * 80)

    if failed > 0:
        print("\n[WARNING] Some tests failed. Check the output above for details.")
        return 1
    else:
        print("\n[SUCCESS] All tests passed! Your Nivora installation is working correctly.")
        return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))

#!/usr/bin/env python3
"""
Test script for Nivora Browser Agent Integration

This script verifies that all components of the browser agent system
can be imported and work together correctly.
"""

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def test_imports():
    """Test that all required modules can be imported."""
    print("[*] Testing imports...")

    try:
        # Test browser automation engine
        from browser_automation import BrowserAutomationEngine
        print("[+] BrowserAutomationEngine imported successfully")

        # Test browser-use adapter
        from browser_use_adapter import BrowserUseAdapter, is_browser_use_available
        print(f"[+] BrowserUseAdapter imported successfully (browser-use available: {is_browser_use_available()})")

        # Test enhanced browser tools
        from tools import (
            browser_visual_click, smart_form_fill_enhanced,
            ecommerce_price_compare, social_media_compose,
            website_data_mining
        )
        print("[+] Enhanced browser tools imported successfully")

        # Test browser agent prompts
        from browser_agent_prompts import build_browser_agent_instructions
        print("[+] Browser agent prompts imported successfully")

        # Test browser agent class (without LLM initialization)
        import browser_agent
        print("[+] BrowserAgent class imported successfully")

        # Test multi-agent integration
        from multi_agent_livekit import AgentConfig
        print(f"[+] Multi-agent integration successful (Browser voice: {AgentConfig.BROWSER_VOICE_ID})")

        # Test edge TTS voice mapping
        from edge_tts_plugin import VOICE_MAPPING
        if "browser_jenny_neural" in VOICE_MAPPING:
            print("[+] Browser agent voice mapping configured correctly")
        else:
            print("[-] Browser agent voice mapping missing")
            return False

        return True

    except ImportError as e:
        print(f"[-] Import failed: {e}")
        return False
    except Exception as e:
        print(f"[-] Unexpected error: {e}")
        return False


def test_browser_automation_backends():
    """Test browser automation backend availability."""
    print("\n[*] Testing browser automation backends...")

    try:
        from browser_automation import PLAYWRIGHT_AVAILABLE, BROWSER_USE_AVAILABLE

        print(f"  Playwright available: {PLAYWRIGHT_AVAILABLE}")
        print(f"  browser-use available: {BROWSER_USE_AVAILABLE}")

        if PLAYWRIGHT_AVAILABLE:
            print("[+] Primary browser automation backend (Playwright) is available")
        elif BROWSER_USE_AVAILABLE:
            print("[+] Alternative browser automation backend (browser-use) is available")
        else:
            print("[!] No browser automation backends available")
            return False

        return True

    except Exception as e:
        print(f"[-] Backend test failed: {e}")
        return False


def test_agent_personality():
    """Test browser agent personality and instructions."""
    print("\n[*] Testing browser agent personality...")

    try:
        from browser_agent_prompts import build_browser_agent_instructions

        instructions = build_browser_agent_instructions("test automation task")

        # Check if key personality elements are present
        personality_checks = [
            "friendly" in instructions.lower(),
            "browser" in instructions.lower(),
            "automation" in instructions.lower(),
            "form" in instructions.lower() or "social" in instructions.lower(),
            "test automation task" in instructions  # Entry topic should be included
        ]

        if all(personality_checks):
            print("[+] Browser agent personality configured correctly")
            return True
        else:
            print("[-] Browser agent personality missing required elements")
            return False

    except Exception as e:
        print(f"[-] Personality test failed: {e}")
        return False


def test_tool_integration():
    """Test that enhanced browser tools are properly integrated."""
    print("\n[*] Testing tool integration...")

    try:
        from tools import ALL_TOOLS

        enhanced_tools = [
            "browser_visual_click",
            "smart_form_fill_enhanced",
            "ecommerce_price_compare",
            "social_media_compose",
            "website_data_mining"
        ]

        tool_names = [getattr(tool, '__name__', str(tool)) for tool in ALL_TOOLS]

        missing_tools = []
        for tool_name in enhanced_tools:
            if tool_name not in tool_names:
                missing_tools.append(tool_name)

        if not missing_tools:
            print("[+] All enhanced browser tools integrated into ALL_TOOLS")
            return True
        else:
            print(f"[-] Missing tools in ALL_TOOLS: {missing_tools}")
            return False

    except Exception as e:
        print(f"[-] Tool integration test failed: {e}")
        return False


def main():
    """Run all tests."""
    print("Nivora Browser Agent Integration Test")
    print("=" * 50)

    tests = [
        test_imports,
        test_browser_automation_backends,
        test_agent_personality,
        test_tool_integration,
    ]

    passed = 0
    total = len(tests)

    for test in tests:
        if test():
            passed += 1
        print()  # Add spacing between tests

    # Summary
    print("=" * 50)
    print(f"Test Results: {passed}/{total} tests passed")

    if passed == total:
        print("SUCCESS: All tests passed! Browser agent integration is ready.")
        print("\nNext steps:")
        print("1. Set up Azure OpenAI credentials in .env file")
        print("2. Run the multi-agent system: python multi_agent_livekit.py")
        print("3. Test browser automation via voice commands")
        print("4. Try agent transfers: 'Help me fill out a web form'")
        return True
    else:
        print("FAILURE: Some tests failed. Please fix the issues before proceeding.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
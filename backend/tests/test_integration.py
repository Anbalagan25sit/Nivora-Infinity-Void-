"""
Test Integration of Browser-Use Tools with Nivora Agent
Verifies that browser-use tools are properly loaded and accessible
"""

import os
import sys
import logging

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def test_tools_import():
    """Test that tools.py imports browser-use tools"""
    print("\n" + "="*80)
    print("TEST 1: Import browser-use tools from tools.py")
    print("="*80)

    try:
        from tools import ALL_TOOLS, BROWSER_USE_TOOLS

        print(f"[OK] ALL_TOOLS loaded: {len(ALL_TOOLS)} tools total")
        print(f"[OK] BROWSER_USE_TOOLS loaded: {len(BROWSER_USE_TOOLS)} tools")

        if BROWSER_USE_TOOLS:
            print("\nBrowser-use tools available:")
            for tool in BROWSER_USE_TOOLS:
                tool_name = getattr(tool, 'id', getattr(tool, '__name__', str(tool)))
                print(f"   - {tool_name}")
            return True
        else:
            print("[WARN] BROWSER_USE_TOOLS is empty (browser-use not installed)")
            return False

    except ImportError as e:
        print(f"[FAIL] Failed to import from tools.py: {e}")
        return False


def test_multi_agent_import():
    """Test that multi_agent_livekit.py imports browser-use tools"""
    print("\n" + "="*80)
    print("TEST 2: Import from multi_agent_livekit.py")
    print("="*80)

    try:
        # Add parent directory to path
        import multi_agent_livekit

        # Check if browser-use tools are in NIVORA_TOOLS
        from multi_agent_livekit import AgentConfig

        nivora_tools = AgentConfig.NIVORA_TOOLS
        print(f"[OK] AgentConfig.NIVORA_TOOLS loaded: {len(nivora_tools)} tools")

        # Check for browser-use tools (FunctionTool has 'id' attribute, not 'name')
        browser_use_tools = [
            t for t in nivora_tools
            if hasattr(t, 'id') and any(x in t.id for x in ['ebox', 'browser_use'])
        ]

        if browser_use_tools:
            print(f"[OK] Found {len(browser_use_tools)} browser-use tools in NIVORA_TOOLS:")
            for tool in browser_use_tools:
                tool_id = getattr(tool, 'id', getattr(tool, '__name__', str(tool)))
                print(f"   - {tool_id}")
            return True
        else:
            print("[WARN] No browser-use tools found in NIVORA_TOOLS")
            print("   (This is OK if browser-use is not installed)")
            return False

    except ImportError as e:
        print(f"[FAIL] Failed to import multi_agent_livekit: {e}")
        return False


def test_agent_py_import():
    """Test that agent.py can load all tools"""
    print("\n" + "="*80)
    print("TEST 3: Import tools in agent.py")
    print("="*80)

    try:
        # agent.py imports ALL_TOOLS from tools
        from tools import ALL_TOOLS

        print(f"[OK] agent.py can access ALL_TOOLS: {len(ALL_TOOLS)} tools")

        # Check for browser-use tools in ALL_TOOLS (use 'id' attribute for FunctionTool)
        browser_use_count = sum(
            1 for t in ALL_TOOLS
            if hasattr(t, 'id') and 'ebox' in t.id.lower()
        )

        if browser_use_count > 0:
            print(f"[OK] Found {browser_use_count} E-Box/browser-use tools in ALL_TOOLS")
            return True
        else:
            print("[WARN] No E-Box tools found (browser-use may not be installed)")
            return False

    except Exception as e:
        print(f"[FAIL] Failed to test agent.py imports: {e}")
        return False


def test_direct_import():
    """Test direct import of browser-use tools"""
    print("\n" + "="*80)
    print("TEST 4: Direct import of browser_use_tools.py")
    print("="*80)

    try:
        from browser_use_tools import (
            solve_ebox_differential_equations,
            solve_ebox_specific_section,
            explain_browser_use_agent
        )

        print("[OK] Successfully imported browser_use_tools:")
        print(f"   - solve_ebox_differential_equations: {solve_ebox_differential_equations}")
        print(f"   - solve_ebox_specific_section: {solve_ebox_specific_section}")
        print(f"   - explain_browser_use_agent: {explain_browser_use_agent}")

        # Check if they have proper decorators (FunctionTool has 'id' attribute)
        for tool in [solve_ebox_differential_equations, solve_ebox_specific_section, explain_browser_use_agent]:
            if hasattr(tool, 'id'):
                print(f"   [OK] {tool.id} is properly decorated")
            else:
                print(f"   [WARN] Tool missing @function_tool decorator")

        return True

    except ImportError as e:
        print(f"[FAIL] Failed to import browser_use_tools: {e}")
        print("   Install with: pip install browser-use langchain langchain-aws")
        return False


def test_aws_credentials():
    """Test AWS credentials for browser-use agent"""
    print("\n" + "="*80)
    print("TEST 5: AWS Bedrock credentials (for browser-use LLM)")
    print("="*80)

    aws_key = os.getenv("AWS_ACCESS_KEY_ID", "").strip()
    aws_secret = os.getenv("AWS_SECRET_ACCESS_KEY", "").strip()
    aws_region = os.getenv("AWS_REGION", "us-east-1").strip()
    aws_model = os.getenv("AWS_BEDROCK_MODEL", "amazon.nova-pro-v1:0").strip()

    if aws_key and aws_secret:
        print(f"[OK] AWS credentials found")
        print(f"   Region: {aws_region}")
        print(f"   Model: {aws_model}")
        print(f"   Browser-use agent will use AWS Bedrock Nova Pro!")
        return True
    else:
        print("[WARN] AWS credentials not found")
        print("   Browser-use agent will need ANTHROPIC_API_KEY or OPENAI_API_KEY")

        if os.getenv("ANTHROPIC_API_KEY"):
            print("   [OK] Found ANTHROPIC_API_KEY (fallback)")
            return True
        elif os.getenv("OPENAI_API_KEY"):
            print("   [OK] Found OPENAI_API_KEY (fallback)")
            return True
        else:
            print("   [FAIL] No LLM credentials found!")
            return False


def main():
    """Run all integration tests"""
    print("\n" + "="*80)
    print("BROWSER-USE TOOLS INTEGRATION TEST")
    print("="*80)
    print("Testing integration of browser-use tools with Nivora agent system\n")

    results = {
        "tools.py import": test_tools_import(),
        "multi_agent_livekit.py import": test_multi_agent_import(),
        "agent.py import": test_agent_py_import(),
        "Direct browser_use_tools import": test_direct_import(),
        "AWS credentials": test_aws_credentials(),
    }

    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)

    for test_name, passed in results.items():
        status = "[PASS]" if passed else "[FAIL]"
        print(f"{status} - {test_name}")

    all_passed = all(results.values())

    print("\n" + "="*80)
    if all_passed:
        print("[SUCCESS] ALL TESTS PASSED!")
        print("="*80)
        print("\nBrowser-use tools are properly integrated!")
        print("\nNext steps:")
        print("1. Start agent: python agent.py")
        print("   OR: python multi_agent_livekit.py")
        print("2. Test voice command: 'Solve my differential equations course'")
        print("3. Watch browser-use agent solve problems autonomously!")
    else:
        print("[WARNING] SOME TESTS FAILED")
        print("="*80)
        print("\nIssues found:")

        if not results["Direct browser_use_tools import"]:
            print("* Browser-use not installed")
            print("  Fix: pip install browser-use langchain langchain-aws")

        if not results["AWS credentials"]:
            print("* No LLM credentials configured")
            print("  Fix: Add to .env:")
            print("       AWS_ACCESS_KEY_ID=...")
            print("       AWS_SECRET_ACCESS_KEY=...")
            print("       (or ANTHROPIC_API_KEY or OPENAI_API_KEY)")

    print("\n")
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())

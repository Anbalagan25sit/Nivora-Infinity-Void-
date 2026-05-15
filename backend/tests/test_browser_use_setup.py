"""
Quick Test Script for Browser-Use E-Box Agent
Run this to test the browser-use agent setup
"""

import asyncio
import logging
import os
import sys

# Check dependencies
def check_dependencies():
    """Check if all required packages are installed"""
    required = {
        'browser_use': 'browser-use',
        'langchain': 'langchain',
        'playwright': 'playwright'
    }

    missing = []
    for module, package in required.items():
        try:
            __import__(module)
            print(f"✅ {package} installed")
        except ImportError:
            print(f"❌ {package} NOT installed")
            missing.append(package)

    if missing:
        print(f"\n⚠️  Missing packages: {', '.join(missing)}")
        print(f"\nInstall with:")
        print(f"pip install {' '.join(missing)}")
        return False

    return True


def check_api_keys():
    """Check if LLM API keys are configured"""
    api_keys = {
        'AWS (Bedrock Nova Pro)': ['AWS_ACCESS_KEY_ID', 'AWS_SECRET_ACCESS_KEY'],
        'ANTHROPIC_API_KEY': 'Anthropic Claude',
        'OPENAI_API_KEY': 'OpenAI GPT-4'
    }

    found = False

    # Check AWS credentials (RECOMMENDED - already configured for Nivora!)
    if os.getenv('AWS_ACCESS_KEY_ID') and os.getenv('AWS_SECRET_ACCESS_KEY'):
        print(f"✅ AWS Bedrock Nova Pro credentials found (RECOMMENDED)")
        print(f"   Model: {os.getenv('AWS_BEDROCK_MODEL', 'amazon.nova-pro-v1:0')}")
        print(f"   Region: {os.getenv('AWS_REGION', 'us-east-1')}")
        found = True
    else:
        print(f"❌ AWS Bedrock credentials not found")

    # Check Anthropic
    if os.getenv('ANTHROPIC_API_KEY'):
        print(f"✅ Anthropic Claude API key found (optional fallback)")
        found = True
    else:
        print(f"ℹ️  Anthropic API key not set (optional)")

    # Check OpenAI
    if os.getenv('OPENAI_API_KEY'):
        print(f"✅ OpenAI GPT-4 API key found (optional fallback)")
        found = True
    else:
        print(f"ℹ️  OpenAI API key not set (optional)")

    if not found:
        print("\n⚠️  No LLM configured!")
        print("The browser-use agent needs an LLM. Options:")
        print("\n1. AWS Bedrock Nova Pro (RECOMMENDED - already configured!):")
        print("   AWS_ACCESS_KEY_ID=AKIA...")
        print("   AWS_SECRET_ACCESS_KEY=...")
        print("   AWS_REGION=us-east-1")
        print("   AWS_BEDROCK_MODEL=amazon.nova-pro-v1:0")
        print("\n2. Anthropic Claude (alternative):")
        print("   ANTHROPIC_API_KEY=sk-ant-xxxxx")
        print("\n3. OpenAI GPT-4 (alternative):")
        print("   OPENAI_API_KEY=sk-xxxxx")
        return False

    print("\n✅ At least one LLM is configured!")
    return True


def check_playwright():
    """Check if Playwright browsers are installed"""
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            try:
                p.chromium.launch(headless=True)
                print("✅ Playwright Chromium installed")
                return True
            except Exception:
                print("❌ Playwright Chromium NOT installed")
                print("\nInstall with:")
                print("  playwright install chromium")
                return False
    except Exception as e:
        print(f"❌ Playwright check failed: {e}")
        return False


async def run_quick_test():
    """Run a quick test of the browser-use agent"""
    print("\n" + "="*80)
    print("BROWSER-USE AGENT QUICK TEST")
    print("="*80)

    from browser_use_agent import EBoxBrowserAgent, EBoxConfig

    # Configure for quick test (just i-Learn, visible browser)
    config = EBoxConfig(
        course_name="Differential Equations And Complex Analysis",
        sections=["i-Learn"],  # Just test one section
        headless=False,  # Show browser
        timeout=30000  # 30 seconds
    )

    print("\n📋 Test Configuration:")
    print(f"  Course: {config.course_name}")
    print(f"  Sections: {config.sections}")
    print(f"  Headless: {config.headless}")
    print(f"  Timeout: {config.timeout}ms")

    print("\n🤖 Initializing browser-use agent...")
    print("  (This will open a browser window)")

    agent = EBoxBrowserAgent(config)

    print("\n🚀 Starting autonomous problem solving...")
    print("  The agent will:")
    print("    1. Login to E-Box")
    print("    2. Navigate to Differential Equations course")
    print("    3. Attempt to solve problems in i-Learn")
    print("\n  ⏱️  This may take several minutes...")
    print("  👀 Watch the browser window to see the agent in action!\n")

    result = await agent.solve_differential_equations_course()

    print("\n" + "="*80)
    print("TEST RESULT")
    print("="*80)

    if result.get("success"):
        print("✅ Agent completed successfully!")
        print(f"   Actions taken: {result.get('actions_taken', 'unknown')}")
        print("\n   The browser-use agent is working correctly!")
        print("   You can now integrate it with Nivora.")
    else:
        print("❌ Agent encountered an error:")
        print(f"   {result.get('error')}")
        print("\n   Troubleshooting:")
        print("   1. Check E-Box credentials in .env")
        print("   2. Verify E-Box website is accessible")
        print("   3. Check browser console for errors")
        print("   4. Review BROWSER_USE_AGENT_GUIDE.md")

    print("="*80 + "\n")


async def main():
    """Main test function"""
    print("🔍 Checking browser-use agent setup...\n")

    # Run checks
    checks = [
        ("Dependencies", check_dependencies),
        ("API Keys", check_api_keys),
        ("Playwright", check_playwright)
    ]

    all_passed = True
    for name, check_func in checks:
        print(f"\n📦 Checking {name}:")
        print("-" * 40)
        if not check_func():
            all_passed = False

    if not all_passed:
        print("\n❌ Setup incomplete. Please fix the issues above.")
        print("\nRefer to BROWSER_USE_AGENT_GUIDE.md for detailed instructions.")
        return

    print("\n" + "="*80)
    print("✅ ALL CHECKS PASSED!")
    print("="*80)

    # Ask if user wants to run test
    print("\n🚀 Ready to run browser-use agent test!")
    print("   This will open a browser and attempt to solve E-Box problems.")
    print("   Duration: 2-5 minutes")

    response = input("\n   Run test now? (y/N): ").strip().lower()

    if response == 'y':
        await run_quick_test()
    else:
        print("\n✅ Setup verified! Run this script again when ready to test.")
        print("   Or run manually: python browser_use_agent.py")


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

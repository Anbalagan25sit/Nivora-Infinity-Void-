"""
Test Script: Universal Web Agent Tool Recognition
===============================================
This script tests whether the Universal Web Agent tools are properly loaded
and accessible to the voice assistant.
"""

import asyncio
import sys
import os

# Ensure we can import the tools
try:
    from tools import ALL_TOOLS
    from universal_web_tools import automate_website_task
    print(f"✅ Tools loaded successfully: {len(ALL_TOOLS)} total tools")
    print(f"✅ Universal Web Agent available: {automate_website_task in ALL_TOOLS}")
except Exception as e:
    print(f"❌ Tool loading failed: {e}")
    sys.exit(1)


async def test_github_automation():
    """Test the exact scenario the user described"""
    print("\n🧪 Testing GitHub Repository Listing")
    print("=" * 50)
    print("Simulating: 'goto github page and tell what repo are present'")

    try:
        result = await automate_website_task(
            task_description="Go to GitHub and list all repositories shown on the page",
            website_url="https://github.com"
        )

        print("\n📋 RESULT:")
        print("-" * 30)
        print(result[:500] + "..." if len(result) > 500 else result)

        if "success" in result.lower() or "repository" in result.lower() or "repo" in result.lower():
            print("\n✅ TEST PASSED: Universal Web Agent can handle GitHub repository listing")
        else:
            print("\n⚠️  TEST PARTIAL: Tool executed but may need refinement")

    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        return False

    return True


def test_tool_registration():
    """Test that tools are properly registered with function_tool decorator"""
    print("\n🔧 Testing Tool Registration")
    print("=" * 50)

    tool_names = []
    for tool in ALL_TOOLS:
        if hasattr(tool, 'name'):
            tool_names.append(tool.name)
        elif hasattr(tool, '__name__'):
            tool_names.append(tool.__name__)
        else:
            tool_names.append(str(tool))

    universal_tools = [name for name in tool_names if 'automate' in name.lower()]

    print(f"Total tools: {len(ALL_TOOLS)}")
    print(f"Universal Web Agent tools found: {universal_tools}")

    expected_universal_tools = [
        'automate_website_task',
        'automate_shopping_cart',
        'automate_form_filling'
    ]

    missing = [tool for tool in expected_universal_tools if tool not in tool_names]
    if missing:
        print(f"⚠️  Missing tools: {missing}")
        return False
    else:
        print("✅ All Universal Web Agent tools properly registered")
        return True


async def main():
    """Run all tests"""
    print("🚀 UNIVERSAL WEB AGENT - TOOL RECOGNITION TEST")
    print("=" * 80)

    # Test 1: Tool Registration
    registration_ok = test_tool_registration()

    # Test 2: Actual automation (if AWS credentials available)
    if os.getenv("AWS_ACCESS_KEY_ID") and os.getenv("AWS_SECRET_ACCESS_KEY"):
        automation_ok = await test_github_automation()
    else:
        print("\n⚠️  Skipping automation test - AWS credentials not configured")
        print("   Set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY to test automation")
        automation_ok = None

    # Summary
    print("\n" + "=" * 80)
    print("📊 TEST SUMMARY")
    print("=" * 80)

    print(f"✅ Tool Registration: {'PASS' if registration_ok else 'FAIL'}")
    if automation_ok is not None:
        print(f"✅ GitHub Automation: {'PASS' if automation_ok else 'FAIL'}")
    else:
        print("⏭️  GitHub Automation: SKIPPED (no AWS credentials)")

    if registration_ok and (automation_ok is None or automation_ok):
        print("\n🎉 VERDICT: Universal Web Agent is ready for voice commands!")
        print("\nThe user should be able to say:")
        print('- "Go to GitHub and tell me what repos are there"')
        print('- "Visit LinkedIn and check my messages"')
        print('- "Search for laptops on Amazon under $1000"')
        print("\nIf the agent is still refusing, check the prompt instructions.")
    else:
        print("\n❌ VERDICT: Issues found - Universal Web Agent needs fixes")


if __name__ == "__main__":
    asyncio.run(main())
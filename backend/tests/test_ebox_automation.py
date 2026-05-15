"""
E-Box Automation Test Script
Run this to verify the E-Box automation is working correctly.
"""

import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(__file__))

async def test_ebox_automation():
    """Test E-Box automation components."""
    print("🧪 E-Box Automation Test Suite\n")
    print("=" * 60)

    # Test 1: Import check
    print("\n1️⃣ Testing imports...")
    try:
        from ebox_automation import (
            complete_ebox_course,
            ebox_quick_answer,
            extract_course_and_unit,
            EBOX_USERNAME,
            EBOX_PASSWORD,
            COURSE_MAPPINGS
        )
        print("   ✅ All imports successful")
    except ImportError as e:
        print(f"   ❌ Import failed: {e}")
        return False

    # Test 2: Credential check
    print("\n2️⃣ Testing credentials...")
    if EBOX_USERNAME == "SIT25CS170" and EBOX_PASSWORD == "SIT25CS170":
        print(f"   ✅ Credentials configured: {EBOX_USERNAME}")
    else:
        print(f"   ❌ Unexpected credentials: {EBOX_USERNAME}")
        return False

    # Test 3: Natural language parsing
    print("\n3️⃣ Testing natural language parsing...")
    test_cases = [
        ("finish my course", {"all": True}),
        ("complete unit 3", {"unit": 3}),
        ("do compiler design unit 2", {"course": "Compiler Design", "unit": 2}),
        ("complete section 3 of unit 1", {"unit": 1, "section": 3}),
    ]

    for input_text, expected_keys in test_cases:
        result = extract_course_and_unit(input_text)
        matches = all(result.get(k) == v for k, v in expected_keys.items())

        if matches:
            print(f"   ✅ '{input_text}' → {result}")
        else:
            print(f"   ❌ '{input_text}' → {result} (expected {expected_keys})")

    # Test 4: Course mappings
    print("\n4️⃣ Testing course mappings...")
    print(f"   Available mappings: {len(COURSE_MAPPINGS)}")
    for abbr, full_name in list(COURSE_MAPPINGS.items())[:5]:
        print(f"   • '{abbr}' → '{full_name}'")
    print("   ✅ Course mappings loaded")

    # Test 5: Tool registration
    print("\n5️⃣ Testing tool registration...")
    try:
        from tools import ALL_TOOLS
        tool_names = [t.name if hasattr(t, 'name') else str(t) for t in ALL_TOOLS]

        if "complete_ebox_course" in str(tool_names):
            print("   ✅ complete_ebox_course registered in ALL_TOOLS")
        else:
            print("   ⚠️  complete_ebox_course not found in ALL_TOOLS")

        if "ebox_quick_answer" in str(tool_names):
            print("   ✅ ebox_quick_answer registered in ALL_TOOLS")
        else:
            print("   ⚠️  ebox_quick_answer not found in ALL_TOOLS")

    except Exception as e:
        print(f"   ❌ Tool registration check failed: {e}")

    # Test 6: Browser automation dependency
    print("\n6️⃣ Testing browser automation...")
    try:
        from browser_automation import BrowserAutomationEngine
        print("   ✅ BrowserAutomationEngine available")
    except ImportError as e:
        print(f"   ❌ Browser automation not available: {e}")
        print("   💡 Install: pip install playwright && playwright install chromium")

    # Test 7: AWS Bedrock (vision AI)
    print("\n7️⃣ Testing AWS Bedrock...")
    try:
        import boto3
        import json

        bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')
        print("   ✅ AWS Bedrock client created")

        # Check credentials
        aws_key = os.getenv("AWS_ACCESS_KEY_ID", "").strip()
        aws_secret = os.getenv("AWS_SECRET_ACCESS_KEY", "").strip()

        if aws_key and aws_secret:
            print(f"   ✅ AWS credentials configured")
        else:
            print(f"   ⚠️  AWS credentials not found in environment")

    except Exception as e:
        print(f"   ❌ AWS Bedrock setup failed: {e}")

    # Test 8: Prompt instructions
    print("\n8️⃣ Testing prompt integration...")
    try:
        from prompts import AGENT_INSTRUCTION

        if "E-BOX COURSE AUTOMATION" in AGENT_INSTRUCTION:
            print("   ✅ E-Box instructions found in AGENT_INSTRUCTION")
        else:
            print("   ⚠️  E-Box instructions not in prompt")

        if "complete_ebox_course" in AGENT_INSTRUCTION:
            print("   ✅ Tool name mentioned in prompt")
        else:
            print("   ⚠️  Tool name not mentioned in prompt")

    except Exception as e:
        print(f"   ❌ Prompt check failed: {e}")

    # Summary
    print("\n" + "=" * 60)
    print("✅ Test suite completed!")
    print("\nℹ️  To test live automation:")
    print("   1. Run: python agent.py")
    print("   2. Connect via LiveKit client")
    print("   3. Say: 'finish my course' or 'complete unit 3'")
    print("\n📖 See EBOX_AUTOMATION_GUIDE.md for full documentation")

    return True


async def test_quick_answer():
    """Test the quick answer functionality."""
    print("\n" + "=" * 60)
    print("🧠 Testing AI Question Solver\n")

    try:
        from ebox_automation import solve_question_with_ai

        test_question = {
            "question_text": "What is a compiler?",
            "options": [
                "A program that translates high-level code to machine code",
                "A hardware component",
                "A database system",
                "An operating system"
            ],
            "question_type": "multiple_choice"
        }

        print("Test Question:")
        print(f"  Q: {test_question['question_text']}")
        for i, opt in enumerate(test_question['options'], 1):
            print(f"  {i}. {opt}")

        print("\n🤖 Asking AI...")

        result = await solve_question_with_ai(test_question)

        if result.get("success"):
            print(f"\n✅ AI Answer: {result['answer_text']}")
            print(f"   Confidence: {result['confidence']:.0%}")
            print(f"   Reasoning: {result['reasoning']}")
        else:
            print(f"\n❌ AI failed: {result.get('error')}")

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    print("""
╔══════════════════════════════════════════════════════════╗
║         E-BOX AUTOMATION TEST SUITE                      ║
║         Testing Nivora's Course Automation               ║
╚══════════════════════════════════════════════════════════╝
    """)

    # Run basic tests
    asyncio.run(test_ebox_automation())

    # Ask if user wants to test AI
    print("\n" + "=" * 60)
    response = input("\n🤔 Test AI question solver? (requires AWS credentials) [y/N]: ")

    if response.lower() == 'y':
        asyncio.run(test_quick_answer())

    print("\n✨ All tests complete!\n")

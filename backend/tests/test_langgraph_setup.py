"""
Test script for LangGraph + Claude API integration
Verifies:
1. ANTHROPIC_API_KEY is configured
2. LangGraph dependencies are installed
3. Browser-use agent can connect to Claude
4. Workflow graph builds correctly
"""

import os
import sys
import logging
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_anthropic_key():
    """Test 1: Verify Anthropic API key"""
    logger.info("=" * 80)
    logger.info("TEST 1: Anthropic API Key")
    logger.info("=" * 80)

    load_dotenv()
    api_key = os.getenv("ANTHROPIC_API_KEY")

    if not api_key:
        logger.error("❌ ANTHROPIC_API_KEY not found in .env!")
        logger.error("Add to .env: ANTHROPIC_API_KEY=sk-ant-api03-xxxxx")
        return False

    if not api_key.startswith("sk-ant-"):
        logger.error(f"❌ Invalid key format: {api_key[:20]}...")
        logger.error("Should start with 'sk-ant-'")
        return False

    logger.info(f"✅ ANTHROPIC_API_KEY found: {api_key[:20]}...{api_key[-4:]}")
    return True

def test_langgraph_imports():
    """Test 2: Verify LangGraph installed"""
    logger.info("\n" + "=" * 80)
    logger.info("TEST 2: LangGraph Dependencies")
    logger.info("=" * 80)

    try:
        from langgraph.graph import StateGraph, END
        from langgraph.checkpoint.memory import MemorySaver
        logger.info("✅ langgraph installed")

        from langchain_anthropic import ChatAnthropic
        logger.info("✅ langchain-anthropic installed")

        from browser_use import Agent, Browser
        logger.info("✅ browser-use installed")

        return True
    except ImportError as e:
        logger.error(f"❌ Missing dependency: {e}")
        logger.error("Install with: pip install langgraph langgraph-checkpoint langchain-anthropic browser-use")
        return False

def test_claude_connection():
    """Test 3: Test Claude API connection"""
    logger.info("\n" + "=" * 80)
    logger.info("TEST 3: Claude API Connection")
    logger.info("=" * 80)

    try:
        from langchain_anthropic import ChatAnthropic
        load_dotenv()

        llm = ChatAnthropic(
            model="claude-3-5-sonnet-20241022",
            temperature=0.7,
            anthropic_api_key=os.getenv("ANTHROPIC_API_KEY")
        )

        logger.info("✅ Claude LLM initialized")
        logger.info(f"   Model: {llm.model}")
        logger.info(f"   Temperature: {llm.temperature}")

        # Test with a simple invoke
        logger.info("Testing API call...")
        response = llm.invoke("Say 'Hello from Nivora!' in exactly 5 words.")
        logger.info(f"✅ API Response: {response.content}")

        return True
    except Exception as e:
        logger.error(f"❌ Claude connection failed: {e}")
        logger.error("Check your ANTHROPIC_API_KEY and internet connection")
        return False

def test_langgraph_workflow():
    """Test 4: Build LangGraph workflow"""
    logger.info("\n" + "=" * 80)
    logger.info("TEST 4: LangGraph Workflow")
    logger.info("=" * 80)

    try:
        from browser_use_langgraph import EBoxLangGraphAgent, EBoxConfig

        config = EBoxConfig(
            course_name="Test Course",
            sections=["i-Learn"],
            headless=True
        )

        agent = EBoxLangGraphAgent(config)
        logger.info("✅ EBoxLangGraphAgent created")
        logger.info(f"   Course: {agent.config.course_name}")
        logger.info(f"   Sections: {agent.config.sections}")
        logger.info(f"   LLM: {agent.llm.model}")

        # Check graph structure
        if agent.graph:
            logger.info("✅ LangGraph workflow compiled")
            # Get node names
            nodes = list(agent.graph.nodes.keys()) if hasattr(agent.graph, 'nodes') else []
            logger.info(f"   Workflow nodes: {nodes if nodes else 'Graph structure compiled'}")
        else:
            logger.error("❌ Graph not compiled")
            return False

        return True
    except Exception as e:
        logger.error(f"❌ Workflow build failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_livekit_tools():
    """Test 5: Verify LiveKit tool integration"""
    logger.info("\n" + "=" * 80)
    logger.info("TEST 5: LiveKit Tool Integration")
    logger.info("=" * 80)

    try:
        from browser_use_langgraph_tools import (
            solve_ebox_course_langgraph,
            solve_ebox_section_langgraph
        )

        logger.info("✅ LangGraph tools imported")
        logger.info(f"   Tool 1: {solve_ebox_course_langgraph.__name__}")
        logger.info(f"   Tool 2: {solve_ebox_section_langgraph.__name__}")

        # Check function signatures
        import inspect
        sig1 = inspect.signature(solve_ebox_course_langgraph)
        sig2 = inspect.signature(solve_ebox_section_langgraph)

        logger.info(f"   solve_ebox_course_langgraph params: {list(sig1.parameters.keys())}")
        logger.info(f"   solve_ebox_section_langgraph params: {list(sig2.parameters.keys())}")

        return True
    except ImportError as e:
        logger.error(f"❌ Tool import failed: {e}")
        return False

def main():
    """Run all tests"""
    logger.info("\n" + "🚀" * 40)
    logger.info("NIVORA LANGGRAPH + CLAUDE INTEGRATION TEST SUITE")
    logger.info("🚀" * 40 + "\n")

    results = {
        "Anthropic API Key": test_anthropic_key(),
        "LangGraph Dependencies": test_langgraph_imports(),
        "Claude API Connection": test_claude_connection(),
        "LangGraph Workflow": test_langgraph_workflow(),
        "LiveKit Tools": test_livekit_tools(),
    }

    # Summary
    logger.info("\n" + "=" * 80)
    logger.info("TEST SUMMARY")
    logger.info("=" * 80)

    passed = sum(results.values())
    total = len(results)

    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        logger.info(f"{status}: {test_name}")

    logger.info("=" * 80)
    logger.info(f"OVERALL: {passed}/{total} tests passed")
    logger.info("=" * 80)

    if passed == total:
        logger.info("\n🎉 ALL TESTS PASSED!")
        logger.info("Your LangGraph + Claude integration is ready!")
        logger.info("\nNext steps:")
        logger.info("1. Install dependencies: pip install langgraph langgraph-checkpoint")
        logger.info("2. Test standalone: python browser_use_langgraph.py")
        logger.info("3. Run Nivora: python multi_agent_livekit.py")
        logger.info('4. Say: "Solve my E-Box course with orchestration"')
        return 0
    else:
        logger.error(f"\n❌ {total - passed} test(s) failed!")
        logger.error("Fix the issues above before proceeding.")
        return 1

if __name__ == "__main__":
    sys.exit(main())

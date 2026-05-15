"""
LiveKit Agent Tools for Browser-Use E-Box Agent
Integrates browser-use autonomous agent with Nivora voice assistant
"""

import logging
from typing import Annotated
from livekit.agents import RunContext, function_tool

from generic_browser_agent import GenericBrowserAgent

logger = logging.getLogger(__name__)


@function_tool(
    description="Autonomously execute a general web task in the browser (e.g., play a video, check Instagram, search GitHub, use Slack, etc.)"
)
async def execute_generic_browser_task(
    context: RunContext,
    task: Annotated[str, "The natural language instruction for the browser agent (e.g., 'Go to youtube and play a music video')"],
    headless: Annotated[bool, "Run browser in headless mode. Default: False"] = False
) -> str:
    """
    Use the generic browser-use AI agent to navigate the web and perform arbitrary tasks autonomously.
    """
    try:
        logger.info(f"[GenericBrowserTool] Starting autonomous generic task: {task}")
        
        agent = GenericBrowserAgent(headless=headless)
        result = await agent.execute_task(task)

        if result.get("success"):
            return f"✅ Successfully executed task: '{task}'. Result: {result.get('result')}"
        else:
            return f"❌ Agent encountered an error executing '{task}': {result.get('error')}"

    except Exception as e:
        logger.error(f"[GenericBrowserTool] Error: {e}")
        return f"❌ Failed to run generic browser agent: {str(e)}"


# Export tools list for easy registration
BROWSER_USE_TOOLS = [
    execute_generic_browser_task
]

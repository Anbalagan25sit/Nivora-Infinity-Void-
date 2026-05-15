"""
Generic Browser Agent
Autonomous web agent using browser-use library to perform arbitrary tasks on the web.
Capable of navigating Instagram, Slack, GitHub, playing videos, and more.
"""

import asyncio
import logging
from typing import Dict, Any, Optional

from browser_use import Agent, Browser
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'legacy'))
from browser_use_agent import _init_llm  # Reuse the LLM setup from the E-Box agent

logger = logging.getLogger(__name__)

class GenericBrowserAgent:
    """
    Generic browser-use agent for autonomous web interactions.
    It takes an arbitrary user prompt and executes it using the browser.
    """

    def __init__(self, headless: bool = False):
        self.headless = headless
        self.browser: Optional[Browser] = None
        self.agent: Optional[Agent] = None
        self.llm = _init_llm()

    async def execute_task(self, prompt: str) -> Dict[str, Any]:
        """
        Execute a natural language task on the web.
        """
        try:
            # Create browser directly with kwargs (new in browser-use v0.1.30+)
            self.browser = Browser(
                headless=self.headless,
                disable_security=True,
            )

            # Keep the task prompt extremely direct to prevent LLM confusion
            task = f"Execute the following task autonomously in the browser without asking for user input: {prompt}"

            # Initialize agent
            self.agent = Agent(
                task=task,
                llm=self.llm,
                browser=self.browser,
                max_actions_per_step=10,
            )

            logger.info(f"[GenericBrowserAgent] Starting task: '{prompt}'")

            # Run the agent
            result = await self.agent.run()

            return {
                "success": True,
                "message": "Task execution completed.",
                "result": str(result),
                "actions_taken": getattr(getattr(self.agent, 'state', None), 'n_steps', 0) if self.agent else 0
            }

        except Exception as e:
            logger.error(f"[GenericBrowserAgent] Error: {e}")
            import traceback
            traceback.print_exc()
            return {
                "success": False,
                "error": str(e)
            }
        finally:
            if self.browser:
                try:
                    # Let the browser stay open for a few seconds if not headless so the user can see the final state
                    if not self.headless:
                        await asyncio.sleep(5)
                    await self.browser.close()
                except Exception:
                    pass

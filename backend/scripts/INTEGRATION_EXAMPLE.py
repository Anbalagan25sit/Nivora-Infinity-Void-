"""
Example: Integrating Browser-Use Tools with Nivora Agent
This shows how to add the browser-use AI agent to your existing LiveKit agent
"""

# ============================================================================
# OPTION 1: Add to multi_agent_livekit.py (RECOMMENDED)
# ============================================================================

# At the top of multi_agent_livekit.py, add import:
from browser_use_tools import (
    solve_ebox_differential_equations,
    solve_ebox_specific_section,
    explain_browser_use_agent
)

# Then in AgentConfig class, add to NIVORA_TOOLS:
class AgentConfig:
    """Configuration for agent tools and settings"""

    NIVORA_TOOLS = [
        # Existing tools
        web_search,
        spotify_play_media,
        describe_screen_share,
        # ... other existing tools ...

        # NEW: Browser-use AI agent tools
        solve_ebox_differential_equations,
        solve_ebox_specific_section,
        explain_browser_use_agent,
    ]

    INFIN_TOOLS = [
        # Keep Infin tools as-is
        # ...
    ]


# ============================================================================
# OPTION 2: Add to tools.py (Alternative)
# ============================================================================

# At the end of tools.py, add:
from browser_use_tools import (
    solve_ebox_differential_equations,
    solve_ebox_specific_section,
    explain_browser_use_agent
)

# The tools are already decorated with @function_tool
# They will be automatically discovered if tools.py is imported


# ============================================================================
# OPTION 3: Create separate agent specializing in E-Box (Advanced)
# ============================================================================

from browser_use_agent import EBoxBrowserAgent, EBoxConfig
from livekit.agents import RunContext, function_tool

class EBoxSpecialistAgent:
    """Specialized agent just for E-Box automation"""

    def __init__(self):
        self.ebox_agent = None

    @function_tool(
        description="Launch autonomous E-Box problem solver for differential equations"
    )
    async def launch_ebox_solver(
        self,
        context: RunContext
    ) -> str:
        """Launch the browser-use agent to solve E-Box problems"""
        config = EBoxConfig(
            course_name="Differential Equations And Complex Analysis",
            sections=["i-Learn", "i-Analyse"],
            headless=True  # Run in background
        )

        self.ebox_agent = EBoxBrowserAgent(config)
        result = await self.ebox_agent.solve_differential_equations_course()

        if result.get("success"):
            return f"Successfully solved E-Box course! Actions: {result.get('actions_taken')}"
        else:
            return f"Error: {result.get('error')}"


# ============================================================================
# USAGE EXAMPLES
# ============================================================================

# Example 1: Voice command triggers tool
"""
User: "Nivora, solve my differential equations course"

Agent flow:
1. Nivora hears command
2. LLM recognizes intent → calls solve_ebox_differential_equations()
3. Browser-use agent launches
4. Autonomous solving begins
5. Returns result to user
"""

# Example 2: Programmatic usage
"""
from browser_use_tools import solve_ebox_differential_equations

async def handle_user_request(context):
    result = await solve_ebox_differential_equations(
        context=context,
        sections="i-Learn,i-Analyse",
        headless=False  # Show browser
    )
    return result
"""

# Example 3: Custom wrapper with progress updates
"""
@function_tool(description="Solve E-Box with progress updates")
async def solve_with_progress(context: RunContext) -> str:
    # Initialize agent
    agent = EBoxBrowserAgent(EBoxConfig(headless=False))

    # Could add callbacks here for progress updates
    # (future enhancement to browser-use integration)

    result = await agent.solve_differential_equations_course()
    return f"Completed: {result}"
"""


# ============================================================================
# TESTING THE INTEGRATION
# ============================================================================

"""
Step 1: Verify dependencies installed
$ python test_browser_use_setup.py

Step 2: Test standalone agent
$ python browser_use_agent.py

Step 3: Add tools to agent (see options above)

Step 4: Restart Nivora
$ python multi_agent_livekit.py

Step 5: Test via voice
"Nivora, solve my differential equations course"

Step 6: Monitor logs
Look for:
  [BrowserAgent] Starting autonomous agent...
  [BrowserAgent] Browser initialized
  [EBoxTool] Starting browser-use autonomous agent...
"""


# ============================================================================
# ADVANCED: Custom LLM Configuration
# ============================================================================

# If you want to use a different LLM for the browser-use agent,
# modify browser_use_agent.py:

"""
def _init_llm(self):
    # Use AWS Bedrock instead of Anthropic/OpenAI
    from langchain_aws import ChatBedrock

    return ChatBedrock(
        model_id="anthropic.claude-3-5-sonnet-20241022-v2:0",
        region_name="us-east-1",
        model_kwargs={"temperature": 0.7}
    )
"""


# ============================================================================
# TROUBLESHOOTING
# ============================================================================

"""
Issue: "ModuleNotFoundError: No module named 'browser_use'"
Fix: pip install browser-use

Issue: "No LLM API key configured"
Fix: Add ANTHROPIC_API_KEY or OPENAI_API_KEY to .env

Issue: "Browser not found"
Fix: playwright install chromium

Issue: "Agent gets stuck"
Fix: Run with headless=False to see what's happening
     Check E-Box website is accessible
     Verify credentials are correct

Issue: "Wrong answers submitted"
Fix: Use Claude Opus or GPT-4 (better reasoning)
     Lower temperature for more deterministic responses
     Add example solutions to the task prompt
"""


# ============================================================================
# COMPLETE EXAMPLE: Updated multi_agent_livekit.py snippet
# ============================================================================

"""
# File: multi_agent_livekit.py

import asyncio
from livekit.agents import WorkerOptions, cli
from livekit import rtc

# Import existing tools
from tools import (
    web_search,
    spotify_play_media,
    describe_screen_share,
    # ... other tools
)

# Import NEW browser-use tools
from browser_use_tools import (
    solve_ebox_differential_equations,
    solve_ebox_specific_section,
    explain_browser_use_agent
)

class AgentConfig:
    NIVORA_TOOLS = [
        web_search,
        spotify_play_media,
        describe_screen_share,
        # ... existing tools ...

        # Browser-use AI agent (autonomous E-Box solver)
        solve_ebox_differential_equations,
        solve_ebox_specific_section,
        explain_browser_use_agent,
    ]

# Rest of multi_agent_livekit.py remains the same
"""


# ============================================================================
# SUMMARY
# ============================================================================

print("""
✅ Browser-Use Integration Complete!

Files created:
  - browser_use_agent.py       (Main agent)
  - browser_use_tools.py        (LiveKit tools)
  - test_browser_use_setup.py   (Setup tester)
  - BROWSER_USE_AGENT_GUIDE.md  (Documentation)

Next steps:
  1. Run: python test_browser_use_setup.py
  2. Add tools to multi_agent_livekit.py (see above)
  3. Restart Nivora
  4. Test: "Solve my differential equations course"

Voice commands:
  "Solve my differential equations course"
  "Complete i-Learn section"
  "Solve vector calculus in i-Analyse"
  "How does the E-Box agent work?"

Documentation:
  - BROWSER_USE_AGENT_GUIDE.md
  - BROWSER_USE_INTEGRATION_SUMMARY.md
  - CLAUDE.md (updated)
""")

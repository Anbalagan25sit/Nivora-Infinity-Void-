"""
LangGraph-Orchestrated Browser-Use Agent for E-Box
Uses LangGraph for better state management, visibility, and control flow
https://github.com/browser-use/browser-use
"""

import asyncio
import logging
import os
from typing import Dict, Any, Optional, TypedDict, Annotated
from dataclasses import dataclass
from dotenv import load_dotenv

# LangGraph imports
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

# Browser-use imports
from browser_use import Agent, Browser

load_dotenv()

logger = logging.getLogger(__name__)

# E-Box credentials
EBOX_USERNAME = os.getenv("EBOX_USERNAME", "SIT25CS170")
EBOX_PASSWORD = os.getenv("EBOX_PASSWORD", "SIT25CS170")
EBOX_LOGIN_URL = "https://pro.e-box.co.in/login"


@dataclass
class EBoxConfig:
    """Configuration for E-Box automation"""
    course_name: str = "Differential Equations And Complex Analysis"
    sections: list = None
    headless: bool = False

    def __post_init__(self):
        if self.sections is None:
            self.sections = ["i-Learn", "i-Analyse"]


class AgentState(TypedDict):
    """State schema for LangGraph orchestration"""
    # Task tracking
    current_task: str
    task_phase: str  # "login", "navigate", "solve", "verify", "complete"

    # Progress tracking
    problems_solved: int
    problems_failed: int
    current_topic: str
    current_section: str

    # Agent state
    browser_agent: Optional[Agent]
    browser: Optional[Browser]

    # Results
    errors: list
    success_messages: list
    agent_output: Optional[str]

    # Control flow
    should_retry: bool
    max_retries: int
    retry_count: int


def _init_llm():
    """Initialize Claude LLM for browser-use"""
    if not os.getenv("ANTHROPIC_API_KEY"):
        raise ValueError("ANTHROPIC_API_KEY not found! Set it in .env file")

    logger.info("[LangGraph] Using Anthropic Claude 3.5 Sonnet")
    from langchain_anthropic import ChatAnthropic
    return ChatAnthropic(
        model="claude-3-5-sonnet-20241022",
        temperature=0.7,
        anthropic_api_key=os.getenv("ANTHROPIC_API_KEY")
    )


class EBoxLangGraphAgent:
    """LangGraph-orchestrated browser-use agent for E-Box"""

    def __init__(self, config: Optional[EBoxConfig] = None):
        self.config = config or EBoxConfig()
        self.llm = _init_llm()
        self.graph = self._build_graph()

    def _build_graph(self) -> StateGraph:
        """Build LangGraph workflow for E-Box automation"""

        # Create workflow graph
        workflow = StateGraph(AgentState)

        # Add nodes (steps in the workflow)
        workflow.add_node("initialize", self._initialize_node)
        workflow.add_node("login", self._login_node)
        workflow.add_node("navigate_to_course", self._navigate_node)
        workflow.add_node("solve_problems", self._solve_node)
        workflow.add_node("verify_completion", self._verify_node)
        workflow.add_node("handle_error", self._error_node)
        workflow.add_node("finalize", self._finalize_node)

        # Set entry point
        workflow.set_entry_point("initialize")

        # Define edges (transitions)
        workflow.add_edge("initialize", "login")
        workflow.add_conditional_edges(
            "login",
            self._should_retry_or_continue,
            {
                "continue": "navigate_to_course",
                "retry": "login",
                "error": "handle_error"
            }
        )
        workflow.add_conditional_edges(
            "navigate_to_course",
            self._should_retry_or_continue,
            {
                "continue": "solve_problems",
                "retry": "navigate_to_course",
                "error": "handle_error"
            }
        )
        workflow.add_conditional_edges(
            "solve_problems",
            self._should_retry_or_continue,
            {
                "continue": "verify_completion",
                "retry": "solve_problems",
                "error": "handle_error"
            }
        )
        workflow.add_conditional_edges(
            "verify_completion",
            self._check_completion,
            {
                "complete": "finalize",
                "continue": "solve_problems",
                "error": "handle_error"
            }
        )
        workflow.add_edge("handle_error", "finalize")
        workflow.add_edge("finalize", END)

        # Compile with memory for checkpoints
        memory = MemorySaver()
        return workflow.compile(checkpointer=memory)

    async def _initialize_node(self, state: AgentState) -> AgentState:
        """Initialize browser and agent"""
        logger.info("[LangGraph] 📋 PHASE: Initialize")

        try:
            # Create browser
            browser = Browser(headless=self.config.headless)

            # Create browser-use agent with initial task
            task = self._build_login_task()
            agent = Agent(
                task=task,
                llm=self.llm,
                browser=browser,
                max_actions_per_step=10
            )

            state["browser"] = browser
            state["browser_agent"] = agent
            state["task_phase"] = "initialize"
            state["problems_solved"] = 0
            state["problems_failed"] = 0
            state["errors"] = []
            state["success_messages"] = []
            state["retry_count"] = 0
            state["max_retries"] = 3

            logger.info("[LangGraph] ✅ Initialization complete")
            return state

        except Exception as e:
            logger.error(f"[LangGraph] ❌ Initialization failed: {e}")
            state["errors"].append(f"Init error: {str(e)}")
            state["should_retry"] = False
            return state

    async def _login_node(self, state: AgentState) -> AgentState:
        """Login to E-Box"""
        logger.info("[LangGraph] 🔐 PHASE: Login")
        state["task_phase"] = "login"

        try:
            # Update agent task for login
            login_task = f"""
Navigate to {EBOX_LOGIN_URL} and login with:
- Username: {EBOX_USERNAME}
- Password: {EBOX_PASSWORD}

Wait for dashboard to load. Confirm you see the course list.
"""
            state["browser_agent"].task = login_task

            # Run agent
            result = await state["browser_agent"].run()

            state["agent_output"] = str(result)
            state["success_messages"].append("Login successful")
            state["should_retry"] = False
            logger.info("[LangGraph] ✅ Login complete")

            return state

        except Exception as e:
            logger.error(f"[LangGraph] ❌ Login failed: {e}")
            state["errors"].append(f"Login error: {str(e)}")
            state["should_retry"] = state["retry_count"] < state["max_retries"]
            state["retry_count"] += 1
            return state

    async def _navigate_node(self, state: AgentState) -> AgentState:
        """Navigate to course"""
        logger.info(f"[LangGraph] 🧭 PHASE: Navigate to {self.config.course_name}")
        state["task_phase"] = "navigate"

        try:
            nav_task = f"""
Find and click on the course: "{self.config.course_name}"
Wait for the course page to load.
You should see Topics in the left sidebar and Section tabs (i-Learn, i-Explore, i-Analyse).
"""
            state["browser_agent"].task = nav_task
            result = await state["browser_agent"].run()

            state["agent_output"] = str(result)
            state["success_messages"].append("Course navigation successful")
            state["should_retry"] = False
            logger.info("[LangGraph] ✅ Navigation complete")

            return state

        except Exception as e:
            logger.error(f"[LangGraph] ❌ Navigation failed: {e}")
            state["errors"].append(f"Navigation error: {str(e)}")
            state["should_retry"] = state["retry_count"] < state["max_retries"]
            state["retry_count"] += 1
            return state

    async def _solve_node(self, state: AgentState) -> AgentState:
        """Solve problems in current section"""
        current_section = state.get("current_section") or self.config.sections[0]
        logger.info(f"[LangGraph] 🧮 PHASE: Solve problems in {current_section}")
        state["task_phase"] = "solve"
        state["current_section"] = current_section

        try:
            solve_task = f"""
Click on "{current_section}" tab.

For each Topic in the left sidebar:
1. Click on the Topic name
2. Look for problems/projects to solve
3. For differential equation problems:
   - Read the problem carefully
   - Apply appropriate solution method (ODEs, PDEs, Laplace, etc.)
   - Submit the answer
4. Move to the next problem

Solve ALL problems in {current_section} section.
Report how many problems you solved successfully.
"""
            state["browser_agent"].task = solve_task
            result = await state["browser_agent"].run()

            state["agent_output"] = str(result)
            # Extract problem count from result (simple heuristic)
            state["problems_solved"] += self._extract_problem_count(str(result))
            state["success_messages"].append(f"{current_section} problems solved")
            state["should_retry"] = False
            logger.info(f"[LangGraph] ✅ Solved problems in {current_section}")

            return state

        except Exception as e:
            logger.error(f"[LangGraph] ❌ Problem solving failed: {e}")
            state["errors"].append(f"Solve error: {str(e)}")
            state["problems_failed"] += 1
            state["should_retry"] = state["retry_count"] < state["max_retries"]
            state["retry_count"] += 1
            return state

    async def _verify_node(self, state: AgentState) -> AgentState:
        """Verify completion of current section"""
        logger.info("[LangGraph] ✔️ PHASE: Verify completion")
        state["task_phase"] = "verify"

        try:
            verify_task = """
Check if all problems in the current section are completed.
Look for completion indicators (green checkmarks, 100% progress, etc.)
Report completion status.
"""
            state["browser_agent"].task = verify_task
            result = await state["browser_agent"].run()

            state["agent_output"] = str(result)
            state["success_messages"].append("Verification complete")
            state["should_retry"] = False

            return state

        except Exception as e:
            logger.error(f"[LangGraph] ⚠️ Verification warning: {e}")
            state["errors"].append(f"Verify warning: {str(e)}")
            state["should_retry"] = False
            return state

    async def _error_node(self, state: AgentState) -> AgentState:
        """Handle errors"""
        logger.error(f"[LangGraph] 🚨 PHASE: Error handling")
        logger.error(f"[LangGraph] Errors encountered: {state['errors']}")
        state["task_phase"] = "error"
        return state

    async def _finalize_node(self, state: AgentState) -> AgentState:
        """Clean up and return results"""
        logger.info("[LangGraph] 🏁 PHASE: Finalize")
        state["task_phase"] = "complete"

        # Close browser
        if state.get("browser"):
            try:
                await state["browser"].close()
            except:
                pass

        logger.info(f"[LangGraph] ✅ Complete! Solved: {state['problems_solved']}, Failed: {state['problems_failed']}")
        return state

    def _should_retry_or_continue(self, state: AgentState) -> str:
        """Conditional routing: retry, continue, or error"""
        if state.get("errors") and state.get("should_retry", False):
            logger.info(f"[LangGraph] 🔄 Retrying... ({state['retry_count']}/{state['max_retries']})")
            return "retry"
        elif state.get("errors"):
            logger.error("[LangGraph] ❌ Max retries exceeded, moving to error handler")
            return "error"
        else:
            return "continue"

    def _check_completion(self, state: AgentState) -> str:
        """Check if all sections are complete"""
        current_section = state.get("current_section")
        sections = self.config.sections

        if current_section == sections[-1]:
            logger.info("[LangGraph] 🎉 All sections complete!")
            return "complete"
        else:
            # Move to next section
            next_idx = sections.index(current_section) + 1
            state["current_section"] = sections[next_idx]
            logger.info(f"[LangGraph] ➡️ Moving to next section: {sections[next_idx]}")
            return "continue"

    def _extract_problem_count(self, result_text: str) -> int:
        """Extract number of solved problems from agent output"""
        # Simple heuristic - look for numbers in the result
        import re
        numbers = re.findall(r'\d+', result_text)
        return int(numbers[0]) if numbers else 1

    def _build_login_task(self) -> str:
        """Build initial task description"""
        return f"""
You are an autonomous E-Box automation agent.

TASK: Login to E-Box platform and prepare for problem solving.

URL: {EBOX_LOGIN_URL}
Username: {EBOX_USERNAME}
Password: {EBOX_PASSWORD}

START NOW!
"""

    async def run(self) -> Dict[str, Any]:
        """Execute the LangGraph workflow"""
        logger.info("[LangGraph] 🚀 Starting orchestrated E-Box automation")

        # Initial state
        initial_state = {
            "current_task": "E-Box Differential Equations Course",
            "task_phase": "start",
            "problems_solved": 0,
            "problems_failed": 0,
            "current_topic": "",
            "current_section": self.config.sections[0],
            "browser_agent": None,
            "browser": None,
            "errors": [],
            "success_messages": [],
            "agent_output": None,
            "should_retry": False,
            "max_retries": 3,
            "retry_count": 0
        }

        # Run graph with config for thread
        config = {"configurable": {"thread_id": "ebox_session_1"}}

        try:
            # Execute workflow
            final_state = None
            async for state in self.graph.astream(initial_state, config):
                # Log state transitions
                for node_name, node_state in state.items():
                    logger.info(f"[LangGraph] Node '{node_name}' executed")
                    final_state = node_state

            # Return results
            return {
                "success": len(final_state.get("errors", [])) == 0,
                "problems_solved": final_state.get("problems_solved", 0),
                "problems_failed": final_state.get("problems_failed", 0),
                "success_messages": final_state.get("success_messages", []),
                "errors": final_state.get("errors", []),
                "final_phase": final_state.get("task_phase", "unknown")
            }

        except Exception as e:
            logger.error(f"[LangGraph] ❌ Workflow error: {e}")
            import traceback
            traceback.print_exc()
            return {
                "success": False,
                "error": str(e),
                "problems_solved": 0,
                "problems_failed": 0
            }


async def main():
    """Test the LangGraph-orchestrated agent"""
    config = EBoxConfig(
        course_name="Differential Equations And Complex Analysis",
        sections=["i-Learn"],  # Test with one section first
        headless=False
    )

    agent = EBoxLangGraphAgent(config)
    result = await agent.run()

    print("\n" + "="*80)
    print("LANGGRAPH E-BOX AUTOMATION RESULT")
    print("="*80)
    print(f"Success: {result.get('success')}")
    print(f"Problems Solved: {result.get('problems_solved')}")
    print(f"Problems Failed: {result.get('problems_failed')}")
    print(f"Final Phase: {result.get('final_phase')}")

    if result.get('success_messages'):
        print("\n✅ Success Messages:")
        for msg in result['success_messages']:
            print(f"  - {msg}")

    if result.get('errors'):
        print("\n❌ Errors:")
        for err in result['errors']:
            print(f"  - {err}")

    print("="*80)


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    asyncio.run(main())

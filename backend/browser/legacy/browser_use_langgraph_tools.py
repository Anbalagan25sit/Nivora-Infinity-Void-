"""
LiveKit tools for LangGraph-orchestrated browser-use agent
Integrates LangGraph workflow into Nivora voice assistant
"""

import logging
from livekit import agents
from browser_use_langgraph import EBoxLangGraphAgent, EBoxConfig

logger = logging.getLogger(__name__)


@agents.llm.function_tool()
async def solve_ebox_course_langgraph(
    course_name: str = "Differential Equations And Complex Analysis",
    sections: str = "i-Learn,i-Analyse",
    headless: bool = True
) -> str:
    """
    Solve E-Box course problems using LangGraph-orchestrated autonomous agent.

    This tool uses Claude API with LangGraph for better orchestration, state management,
    and visibility into the automation process.

    Args:
        course_name: Name of the E-Box course (default: "Differential Equations And Complex Analysis")
        sections: Comma-separated sections to complete (default: "i-Learn,i-Analyse")
        headless: Run browser in headless mode (default: True for voice assistant)

    Returns:
        str: Summary of automation results including problems solved and errors

    Example voice commands:
        - "Solve my differential equations course using LangGraph"
        - "Complete i-Learn section with orchestration"
        - "Use the advanced agent to finish my E-Box course"
    """
    logger.info(f"[LangGraph Tool] Starting orchestrated E-Box automation")
    logger.info(f"[LangGraph Tool] Course: {course_name}")
    logger.info(f"[LangGraph Tool] Sections: {sections}")

    try:
        # Parse sections
        section_list = [s.strip() for s in sections.split(",")]

        # Create config
        config = EBoxConfig(
            course_name=course_name,
            sections=section_list,
            headless=headless
        )

        # Create and run LangGraph agent
        agent = EBoxLangGraphAgent(config)
        result = await agent.run()

        # Format response for voice assistant
        if result.get("success"):
            response = f"Successfully completed E-Box automation! "
            response += f"Solved {result.get('problems_solved', 0)} problems "

            if result.get('problems_failed', 0) > 0:
                response += f"with {result['problems_failed']} failures. "

            if result.get('success_messages'):
                response += f"Completed phases: {', '.join(result['success_messages'])}."

            return response
        else:
            error_msg = result.get('error', 'Unknown error')
            response = f"E-Box automation encountered errors: {error_msg}. "

            if result.get('problems_solved', 0) > 0:
                response += f"However, managed to solve {result['problems_solved']} problems before failing."

            return response

    except Exception as e:
        logger.error(f"[LangGraph Tool] Error: {e}")
        import traceback
        traceback.print_exc()
        return f"Failed to run LangGraph automation: {str(e)}"


@agents.llm.function_tool()
async def solve_ebox_section_langgraph(
    section_name: str,
    topic_name: str = "all",
    course_name: str = "Differential Equations And Complex Analysis"
) -> str:
    """
    Solve a specific section or topic in E-Box using LangGraph orchestration.

    Args:
        section_name: Section to solve (i-Learn, i-Analyse, i-Explore, i-Design)
        topic_name: Specific topic name, or "all" for entire section (default: "all")
        course_name: Course name (default: "Differential Equations And Complex Analysis")

    Returns:
        str: Summary of results for the specific section/topic

    Example voice commands:
        - "Solve i-Learn section with LangGraph"
        - "Use orchestration to complete i-Analyse"
        - "Solve vector calculus topic with advanced agent"
    """
    logger.info(f"[LangGraph Tool] Solving {section_name} section")

    try:
        config = EBoxConfig(
            course_name=course_name,
            sections=[section_name],
            headless=True
        )

        agent = EBoxLangGraphAgent(config)
        result = await agent.run()

        if result.get("success"):
            return f"Completed {section_name} section! Solved {result.get('problems_solved', 0)} problems."
        else:
            return f"Encountered issues in {section_name}: {result.get('error', 'Unknown error')}"

    except Exception as e:
        logger.error(f"[LangGraph Tool] Error: {e}")
        return f"Failed to solve {section_name}: {str(e)}"


# Tool list for easy import
LANGGRAPH_TOOLS = [
    solve_ebox_course_langgraph,
    solve_ebox_section_langgraph
]

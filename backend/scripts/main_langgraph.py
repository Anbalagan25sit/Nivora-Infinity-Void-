import os
import json
import logging
from typing import Dict, Any, List, TypedDict, Literal
import asyncio
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

try:
    from langgraph.graph import StateGraph, END, START
    from langgraph.checkpoint.memory import MemorySaver
except ImportError:
    StateGraph = END = START = MemorySaver = None

# Using AWS Bedrock directly as it is the primary LLM for Nivora
try:
    from langchain_aws import ChatBedrockConverse
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False

from goal_manager import GoalManager
from memory_store import MemoryStore

logger = logging.getLogger(__name__)

class SupervisorState(TypedDict):
    """
    The state dictionary representing the global conversation context for the LangGraph agent.
    Tracks messages, active goals, episodic facts, and the next node to route to.
    """
    messages: List[Any]
    current_intent: str
    active_goals: List[Dict[str, Any]]
    episodic_facts: Dict[str, str]
    next_node: str
    user_id: str

class MainSupervisor:
    """
    A LangGraph state machine acting as the top-level supervisor for Nivora.
    It decides whether to answer a user directly (Chat), create a persistent
    background task (Plan), or store a new fact (Memory).
    """
    def __init__(self, user_id: str = "default_user"):
        if not StateGraph or not LANGCHAIN_AVAILABLE:
            raise ImportError("Missing required packages. Run: pip install langgraph langgraph-checkpoint langchain-aws")

        self.user_id = user_id
        self.goal_manager = GoalManager()
        self.memory_store = MemoryStore()

        # Initialize LLM (using AWS Bedrock Nova Pro for advanced reasoning)
        # Using the same environment variables as the rest of the app
        aws_region = os.getenv("AWS_REGION", "us-east-1")
        model_id = os.getenv("AWS_BEDROCK_MODEL", "amazon.nova-pro-v1:0")

        if not os.getenv("AWS_ACCESS_KEY_ID") or not os.getenv("AWS_SECRET_ACCESS_KEY"):
            raise ValueError("AWS credentials are required for the Supervisor reasoning engine.")

        self.llm = ChatBedrockConverse(
            model=model_id,
            region_name=aws_region,
            temperature=0.0, # Zero temp for more deterministic routing
        )

        self.graph = self._build_graph()

    def _build_graph(self):
        """Build the state machine graph."""
        workflow = StateGraph(SupervisorState)

        # Add nodes
        workflow.add_node("planner", self._node_planner)
        workflow.add_node("conversational", self._node_conversational)
        workflow.add_node("memory_manager", self._node_memory_manager)
        workflow.add_node("task_delegator", self._node_task_delegator)

        # Set entry point
        workflow.set_entry_point("planner")

        # Add conditional edges from the planner
        workflow.add_conditional_edges(
            "planner",
            lambda state: state["next_node"],
            {
                "conversational": "conversational",
                "memory_manager": "memory_manager",
                "task_delegator": "task_delegator",
                "end": END
            }
        )

        # End all terminal nodes
        workflow.add_edge("conversational", END)
        workflow.add_edge("memory_manager", END)
        workflow.add_edge("task_delegator", END)

        # Compile with simple memory
        memory = MemorySaver()
        return workflow.compile(checkpointer=memory)

    async def _node_planner(self, state: SupervisorState) -> SupervisorState:
        """
        The brain. Evaluates the user's latest message.
        Does it require a persistent background task, a factual memory update, or just a direct chat response?
        """
        logger.info("[Supervisor] Planning node activated.")

        user_input = state["messages"][-1].content

        prompt = f"""
You are the Supervisor AI for Nivora. Your job is to classify the user's intent into one of three categories:
1. 'conversational': The user is asking a general question, asking for code help, or chatting. You should answer immediately.
2. 'task_delegator': The user is asking you to perform a long-running, multi-step task in the background (e.g., scraping, monitoring, sending bulk emails, complex browser automation).
3. 'memory_manager': The user is telling you a personal fact, preference, or something to remember for later (e.g., "My favorite color is blue", "Remember that I use Python").

Current User Input: "{user_input}"

Reply ONLY with a JSON object in this exact format:
{{"next_node": "conversational|task_delegator|memory_manager"}}
"""
        try:
            response = await self.llm.ainvoke([HumanMessage(content=prompt)])
            # Naive JSON extraction (in prod, use structured output)
            content = response.content.replace("```json", "").replace("```", "").strip()
            data = json.loads(content)
            next_node = data.get("next_node", "conversational")

            # Validate routing
            if next_node not in ["conversational", "task_delegator", "memory_manager"]:
                next_node = "conversational"
        except Exception as e:
            logger.error(f"[Supervisor] Planner error: {e}")
            next_node = "conversational"

        state["next_node"] = next_node
        return state

    async def _node_conversational(self, state: SupervisorState) -> SupervisorState:
        """Handle standard Voice/Chat queries using context and memory."""
        logger.info("[Supervisor] Conversational node activated.")

        # Inject facts from memory
        facts = state["episodic_facts"]
        fact_str = "\\n".join([f"- {k}: {v}" for k, v in facts.items()])

        system_msg = SystemMessage(content=f"""
You are Nivora, a helpful conversational AI. Use the following stored facts about the user to personalize your response:
{fact_str}
""")
        messages = [system_msg] + state["messages"]
        response = await self.llm.ainvoke(messages)

        # Append response to messages list
        state["messages"].append(response)
        return state

    async def _node_memory_manager(self, state: SupervisorState) -> SupervisorState:
        """Extract a fact and save it to SQLite memory."""
        logger.info("[Supervisor] Memory manager activated.")
        user_input = state["messages"][-1].content

        prompt = f"""
Extract the key and value from the user's statement to save as a persistent fact.
User said: "{user_input}"
Reply ONLY with JSON format: {{"key": "the_topic", "value": "the_fact"}}
"""
        try:
            response = await self.llm.ainvoke([HumanMessage(content=prompt)])
            content = response.content.replace("```json", "").replace("```", "").strip()
            data = json.loads(content)

            key = data.get("key")
            val = data.get("value")

            if key and val:
                self.memory_store.save_fact(key, val, state["user_id"])
                logger.info(f"Saved fact: {key} = {val}")
                reply = AIMessage(content=f"Got it. I'll remember that your {key} is {val}.")
            else:
                reply = AIMessage(content="I couldn't quite extract the fact from that.")
        except Exception as e:
            logger.error(f"Memory extraction failed: {e}")
            reply = AIMessage(content="Sorry, I had trouble saving that to my memory.")

        state["messages"].append(reply)
        return state

    async def _node_task_delegator(self, state: SupervisorState) -> SupervisorState:
        """Create a persistent goal and background tasks in SQLite."""
        logger.info("[Supervisor] Task Delegator activated.")
        user_input = state["messages"][-1].content

        # Create a new top-level goal
        goal_id = self.goal_manager.create_goal(user_input)

        # In a real implementation, you would use LLM tool calling to generate the sub-tasks here.
        # For this skeleton, we generate a mock task and queue it.
        # We assume `tool_name` maps to something in `background_worker.py`

        self.goal_manager.add_task(
            goal_id=goal_id,
            description="Background automation task initiated by supervisor.",
            tool_name="simulate_background_job",
            tool_args={"query": user_input}
        )

        reply = AIMessage(content="I've created a background task for that. I will let you know when it's finished.")
        state["messages"].append(reply)
        return state

    async def process_user_message(self, message: str, thread_id: str = "default") -> str:
        """Entry point for handling a new user message from LiveKit voice."""

        # Load context
        facts = self.memory_store.get_all_facts(self.user_id)
        active_goals = self.goal_manager.get_all_active_goals()

        initial_state: SupervisorState = {
            "messages": [HumanMessage(content=message)],
            "current_intent": "",
            "active_goals": active_goals,
            "episodic_facts": facts,
            "next_node": "",
            "user_id": self.user_id
        }

        config = {"configurable": {"thread_id": thread_id}}

        # Run graph
        result_state = None
        async for state in self.graph.astream(initial_state, config):
            result_state = state

        # The final dictionary output is inside the node key (e.g. state['conversational'])
        final_messages = list(result_state.values())[0].get("messages", [])

        # Return the last AI message
        if final_messages and isinstance(final_messages[-1], AIMessage):
            return final_messages[-1].content
        return "I processed that."

if __name__ == "__main__":
    # Test the standalone orchestrator
    from dotenv import load_dotenv
    load_dotenv()
    logging.basicConfig(level=logging.INFO)

    async def main():
        supervisor = MainSupervisor()

        print("Testing memory extraction...")
        resp1 = await supervisor.process_user_message("Remember that my name is Alex.")
        print(f"Supervisor: {resp1}")

        print("Testing general conversation (should use memory)...")
        resp2 = await supervisor.process_user_message("What is my name?")
        print(f"Supervisor: {resp2}")

        print("Testing background task delegation...")
        resp3 = await supervisor.process_user_message("Monitor the weather in London every 10 minutes.")
        print(f"Supervisor: {resp3}")

    asyncio.run(main())

"""
Nivora Voice Agent — Universal Web Automation Edition
---------------------------------------------------
Stack: AWS Nova Pro (LLM) · Sarvam STT · Edge TTS (FREE) · Silero VAD

🚀 NEW: UNIVERSAL WEB AUTOMATION CAPABILITIES
- Advanced AI reasoning for ANY website
- Multi-step planning and execution
- Adaptive learning from website patterns
- Robust error handling and recovery
- Universal e-commerce, productivity, and form automation

Config is loaded from config.py which reads .env.
Agent instructions are loaded from prompts.py (AGENT_INSTRUCTION).

🎯 VOICE COMMANDS NOW AVAILABLE:
- "Search for gaming laptops under $1500 on Amazon"
- "Compare iPhone prices across Amazon, eBay, and Best Buy"
- "Fill out this job application form automatically"
- "Book a table for 2 at Italian restaurants tonight"
- "Apply for software engineer jobs on LinkedIn"
- "Monitor Tesla stock price and alert when it drops"

FREE TTS: Edge TTS (Microsoft Neural Voices - no API key needed!)
"""

# --- BEGIN AUTO PATCH: add sub-packages to sys.path ---
import sys as _sys, os as _os
_backend = _os.path.dirname(_os.path.abspath(__file__))
for _sub in ("core", "llm", "tools", "browser", "media"):
    _p = _os.path.join(_backend, _sub)
    if _p not in _sys.path:
        _sys.path.insert(0, _p)
del _sys, _os, _backend, _sub, _p
# --- END AUTO PATCH ---



import logging
import os
import asyncio
import socket

# FIX: Prevent Windows WinError 64 (Connection Lost) for LiveKit WebSockets
socket.setdefaulttimeout(300)
import re
import httpx

# ============================================================================
# FIX: Windows Network Stability for LiveKit WebSocket Connections
# ============================================================================
# Disable HTTP/2 and aiohttp extensions for better Windows compatibility
os.environ['AIOHTTP_NO_EXTENSIONS'] = '1'
os.environ['AIOHTTP_CONNECTOR_LIMIT'] = '100'

# Optimize thread counts for faster Silero VAD inference
# Using 2-4 threads improves VAD speed without excessive memory usage
os.environ.setdefault("OPENBLAS_NUM_THREADS", "2")
os.environ.setdefault("OMP_NUM_THREADS", "2")
os.environ.setdefault("MKL_NUM_THREADS", "2")
os.environ.setdefault("GOTO_NUM_THREADS", "2")
os.environ.setdefault("NUMEXPR_NUM_THREADS", "2")

from livekit import agents
from livekit.agents import Agent, AgentSession, JobContext, room_io
from livekit.agents.llm.mcp import MCPServerHTTP
from livekit.plugins import silero, sarvam, aws

# Import our custom Edge TTS plugin
import edge_tts_plugin

# Import Agentic AI components
from background_worker import BackgroundWorker
from memory_store import MemoryStore

from config import N8N_MCP_URL, N8N_BEARER_TOKEN
from prompts import AGENT_INSTRUCTION
from tools import ALL_TOOLS

# Check if Instagram tools are available
try:
    from agent.tools.instagram_tool import send_instagram_dm
    INSTAGRAM_AVAILABLE = True
    print("Instagram DM tools loaded!")
except ImportError as e:
    INSTAGRAM_AVAILABLE = False
    print(f"Instagram tools not available: {e}")

# AWS config
AWS_REGION = os.getenv("AWS_REGION", "us-east-1").strip()
AWS_BEDROCK_MODEL = os.getenv("AWS_BEDROCK_MODEL", "amazon.nova-pro-v1:0").strip()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
)
logger = logging.getLogger(__name__)


def strip_thinking_tags(text: str) -> str:
    """
    Remove thinking tags and similar internal reasoning blocks from text.
    Ensures user never sees the agent's internal thought process.
    """
    if not text:
        return text

    # Remove all common thinking/reasoning tag patterns
    patterns = [
        r'<thinking>.*?</thinking>',
        r'<reflection>.*?</reflection>',
        r'<reasoning>.*?</reasoning>',
        r'<analysis>.*?</analysis>',
        r'<thought>.*?</thought>',
        r'<browser_thought>.*?</browser_thought>',
        r'<internal>.*?</internal>',
        r'\[thinking:.*?\]',
        r'\[internal:.*?\]',
        # Remove any XML-like tags with "think", "reason", "reflect" in name
        r'<[^>]*(?:think|reason|reflect|analy)[^>]*>.*?</[^>]*(?:think|reason|reflect|analy)[^>]*>',
    ]

    for pattern in patterns:
        text = re.sub(pattern, '', text, flags=re.DOTALL | re.IGNORECASE)

    # Clean up extra whitespace left behind
    text = re.sub(r'\n\s*\n\s*\n', '\n\n', text)  # Max 2 newlines
    text = re.sub(r' +', ' ', text)  # Multiple spaces to single
    text = text.strip()

    return text


class NivoraAgent(Agent):
    """Custom agent class that filters thinking tags from responses."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Wrap the LLM to filter responses before they reach the chat UI
        # Only apply if _llm is properly initialized (not NotGiven)
        if hasattr(self, '_llm') and self._llm is not None:
            # Check if _llm has chat attribute (it's a valid LLM instance)
            if hasattr(self._llm, 'chat'):
                original_chat = self._llm.chat

                async def filtered_chat(*args, **kwargs):
                    result = await original_chat(*args, **kwargs)
                    # Filter thinking tags from LLM response before it's displayed
                    if hasattr(result, 'choices'):
                        for choice in result.choices:
                            if hasattr(choice, 'message') and hasattr(choice.message, 'content'):
                                if isinstance(choice.message.content, str):
                                    choice.message.content = strip_thinking_tags(choice.message.content)
                    return result

                self._llm.chat = filtered_chat

    async def on_message(self, message):
        """Filter thinking tags before TTS speaks and before displaying in chat."""
        print(f"DEBUG: Ada is about to say: {message.content}")
        if hasattr(message, 'content') and isinstance(message.content, str):
            original = message.content
            message.content = strip_thinking_tags(message.content)
            if message.content != original:
                logger.info(f"🔇 Filtered thinking tags from response (kept hidden from user)")
        return await super().on_message(message)

# AWS config
AWS_REGION = os.getenv("AWS_REGION", "us-east-1").strip()
AWS_BEDROCK_MODEL = os.getenv("AWS_BEDROCK_MODEL", "amazon.nova-pro-v1:0").strip()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# MCP server factory
# ---------------------------------------------------------------------------

_MCP_TOOLS = [
    "spotify_play",
    "spotify_pause",
    "spotify_search",
    "spotify_shuffle",
    "youtube_open",
    "open_app",
    "open_website",
    "open_github",
]

async def _build_mcp_server() -> MCPServerHTTP | None:
    """
    Construct the MCPServerHTTP instance and probe the endpoint.
    Returns None (with a warning) if the server is unreachable so the agent
    can still start without MCP tools.
    """
    if not N8N_MCP_URL:
        logger.warning("N8N_MCP_URL is not set — MCP tools will be unavailable.")
        return None

    server = MCPServerHTTP(
        url=N8N_MCP_URL,
        transport_type="sse",
        headers={"Authorization": f"Bearer {N8N_BEARER_TOKEN}"},
        allowed_tools=_MCP_TOOLS,
    )

    # Connectivity probe — a lightweight GET to the base URL.
    # Treat any 4xx/5xx as "unavailable" so the agent starts cleanly without MCP.
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            resp = await client.get(N8N_MCP_URL)
            if resp.status_code >= 400:
                logger.warning(
                    "MCP server returned HTTP %s — skipping MCP tools to avoid _setup_toolset crash. URL: %s",
                    resp.status_code,
                    N8N_MCP_URL,
                )
                return None
            logger.info("MCP server reachable (HTTP %s): %s", resp.status_code, N8N_MCP_URL)
    except Exception as e:
        logger.warning(
            "MCP server unreachable at startup (%s) — proceeding without MCP tools. Error: %s",
            N8N_MCP_URL,
            e,
        )
        return None

    return server


async def _validate_aws_credentials() -> None:
    """
    Validate AWS credentials at startup.
    """
    aws_key = os.getenv("AWS_ACCESS_KEY_ID", "").strip()
    aws_secret = os.getenv("AWS_SECRET_ACCESS_KEY", "").strip()
    if not aws_key or not aws_secret:
        raise RuntimeError("AWS_ACCESS_KEY_ID or AWS_SECRET_ACCESS_KEY is missing in .env")
    logger.info(f"Using AWS Bedrock: {AWS_BEDROCK_MODEL} in {AWS_REGION}")

# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------

async def entrypoint(ctx: JobContext):
    logger.info("Agent entrypoint starting — room: %s", ctx.room.name if ctx.room else "N/A")

    await _validate_aws_credentials()
    logger.info("AWS credential check passed.")

    # Connect to the LiveKit room first
    await ctx.connect()
    logger.info("Connected to LiveKit room.")

    # Start the proactive background worker
    background_worker = BackgroundWorker()
    await background_worker.start()

    # Load Episodic Memory Store
    memory_store = MemoryStore()
    user_facts = memory_store.get_all_facts("default_user")
    logger.info(f"Loaded {len(user_facts)} episodic facts from memory store.")

    # Build MCP server (non-fatal if unreachable)
    mcp_server = await _build_mcp_server()
    mcp_servers = [mcp_server] if mcp_server else []

    # Build the AgentSession with AWS Nova Pro, Sarvam STT, and FREE Edge TTS
    session = AgentSession(
        vad=silero.VAD.load(
            min_silence_duration=0.3,  # OPTIMIZED: Faster detection (was 0.5s)
            activation_threshold=0.45,  # OPTIMIZED: More sensitive (was 0.5)
            padding_duration=0.05,      # OPTIMIZED: Minimal padding (was 0.1)
        ),
        # Sarvam STT
        stt=sarvam.STT(
            language="en-IN",
            model="saaras:v3",
            mode="transcribe",
        ),
        # AWS Bedrock Nova Pro
        llm=aws.LLM(
            model=AWS_BEDROCK_MODEL,
            region=AWS_REGION,
            temperature=0.6,  # OPTIMIZED: Lower for faster, more concise responses (was 0.8)
        ),
        # FREE TTS: Microsoft Edge Neural Voices (no API key needed!)
        tts=edge_tts_plugin.TTS(
            voice="en-US-AriaNeural",  # Sweet natural female voice
            rate="+5%",  # OPTIMIZED: Slightly faster speech rate for snappier responses
        ),
        mcp_servers=mcp_servers,
        # Raised from the default of 3 — YouTube playback alone uses 2 steps.
        # Hitting the default limit causes livekit to retry with tool_choice='none'
        # which triggers an AWS Bedrock ValidationException: toolConfig required
        # whenever toolUse/toolResult blocks exist in the conversation history.
        max_tool_steps=10,
    )
    logger.info("AgentSession created — MCP servers: %d", len(mcp_servers))

    # Log available tool capabilities
    total_tools = len(ALL_TOOLS)
    logger.info(f"Total tools available: {total_tools}")

    logger.info("Agent tools configured.")

    # Start the session with our custom NivoraAgent that filters thinking tags
    try:
        # Combine the base instructions with persistent memory facts
        final_instructions = AGENT_INSTRUCTION
        if user_facts:
            facts_context = "\\n".join([f"- {k}: {v}" for k, v in user_facts.items()])
            final_instructions += f"\\n\\n### Personal User Facts From Memory\\n{facts_context}"

        # Combine all tools, including Universal Web, Browser-Use, LangGraph, and Instagram if available
        active_tools = list(ALL_TOOLS)

        if INSTAGRAM_AVAILABLE:
            active_tools.append(send_instagram_dm)

        await session.start(
            room=ctx.room,
            agent=NivoraAgent(instructions=final_instructions, tools=active_tools),
            room_options=room_io.RoomOptions(
                video_input=True,  # Enable video input from user's camera
            ),
        )
        logger.info("AgentSession started successfully.")
    except Exception as e:
        logger.error("AgentSession failed to start: %s", e, exc_info=True)
        raise

# ---------------------------------------------------------------------------
# CLI entrypoint
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    # Force stable non-reload startup to avoid watcher IPC disconnects on Windows.
    import sys
    if len(sys.argv) == 1:
        sys.argv.append("start")
    agents.cli.run_app(agents.WorkerOptions(entrypoint_fnc=entrypoint))

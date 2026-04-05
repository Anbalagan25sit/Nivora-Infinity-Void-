"""
Nivora Voice Agent — AWS Nova Pro Edition
------------------------------------------
Stack: AWS Nova Pro (LLM) · Sarvam STT · Edge TTS (FREE) · Silero VAD

Config is loaded from config.py which reads .env.
Agent instructions are loaded from prompts.py (AGENT_INSTRUCTION).

FREE TTS: Edge TTS (Microsoft Neural Voices - no API key needed!)
"""

import logging
import os
import asyncio
import re
import httpx

# Keep thread counts low to avoid OOM on resource-constrained machines
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("GOTO_NUM_THREADS", "1")
os.environ.setdefault("NUMEXPR_NUM_THREADS", "1")

from livekit import agents
from livekit.agents import Agent, AgentSession, JobContext, room_io
from livekit.agents.llm.mcp import MCPServerHTTP
from livekit.plugins import silero, sarvam, aws

# Import our custom Edge TTS plugin
import edge_tts_plugin

from config import N8N_MCP_URL, N8N_BEARER_TOKEN
from prompts import AGENT_INSTRUCTION
from tools import ALL_TOOLS


def strip_thinking_tags(text: str) -> str:
    """
    Remove <thinking>, <reflection>, and other XML-like tags that TTS cannot speak.
    This is a safeguard in case the LLM ignores instructions.
    """
    if not text:
        return text

    # Remove thinking tags and their contents
    text = re.sub(r'<thinking>.*?</thinking>', '', text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r'<reflection>.*?</reflection>', '', text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r'<reasoning>.*?</reasoning>', '', text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r'<analysis>.*?</analysis>', '', text, flags=re.DOTALL | re.IGNORECASE)

    # Remove any other XML-like tags that might appear
    text = re.sub(r'<[^>]+>.*?</[^>]+>', '', text, flags=re.DOTALL)

    # Clean up extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()

    return text


class NivoraAgent(Agent):
    """Custom agent class that filters thinking tags from responses."""

    async def on_message(self, message):
        """Filter thinking tags before TTS speaks."""
        if hasattr(message, 'content') and isinstance(message.content, str):
            original = message.content
            message.content = strip_thinking_tags(message.content)
            if message.content != original:
                logger.warning(f"Filtered thinking tags from response")
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

    # Connectivity probe — a lightweight GET to the base URL
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            resp = await client.get(N8N_MCP_URL)
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

    # Build MCP server (non-fatal if unreachable)
    mcp_server = await _build_mcp_server()
    mcp_servers = [mcp_server] if mcp_server else []

    # Build the AgentSession with AWS Nova Pro, Sarvam STT, and FREE Edge TTS
    session = AgentSession(
        vad=silero.VAD.load(min_silence_duration=1.5),
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
            temperature=0.8,  # Slightly lower for clearer, more consistent speech
        ),
        # FREE TTS: Microsoft Edge Neural Voices (no API key needed!)
        tts=edge_tts_plugin.TTS(
            voice="en-US-AriaNeural",  # Sweet natural female voice
        ),
        mcp_servers=mcp_servers,
    )
    logger.info("AgentSession created — MCP servers: %d", len(mcp_servers))

    # Start the session with our custom NivoraAgent that filters thinking tags
    try:
        await session.start(
            room=ctx.room,
            agent=NivoraAgent(instructions=AGENT_INSTRUCTION, tools=ALL_TOOLS),
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

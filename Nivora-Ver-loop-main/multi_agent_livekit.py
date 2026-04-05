"""
Nivora Multi-Agent System — LiveKit Pattern Edition
---------------------------------------------------
Stack: Azure OpenAI GPT-4o (LLM) · Sarvam STT · Edge TTS (FREE) · Silero VAD

Implements explicit agent handoff pattern similar to LiveKit's multi-agent demo.
Infin (default) can transfer to Nivora, and vice versa.

Features:
- Explicit agent transfers with voice switching
- Screen share tracking and vision analysis
- Chat context preservation across transfers
- FREE TTS using Microsoft Edge Neural Voices (no API key needed!)
- Azure OpenAI GPT-4o for powerful, intelligent responses
"""

import logging
import os
import asyncio
from livekit import agents, rtc
from livekit.agents import Agent, AgentSession, JobContext, room_io
from livekit.agents.llm import function_tool, ChatContext
from livekit.agents.llm.mcp import MCPServerHTTP
from livekit.plugins import silero, sarvam

# Import AWS Nova Pro LLM
from aws_nova_llm import get_nova_pro_llm, validate_nova_config

# Import our custom Edge TTS plugin
import edge_tts_plugin

from config import N8N_MCP_URL, N8N_BEARER_TOKEN
from generic_agent import GenericAgent
from screen_share import start_frame_capture

# Tools
from tools import (
    open_website, web_search, get_weather, system_control,
    pause_media, next_track, previous_track, volume_control,
    take_note, read_notes, set_reminder, describe_screen_share,
    spotify_play, spotify_control, spotify_shortcut, youtube_shortcut,
    open_spotify, play_youtube_video, open_youtube,
    send_email, read_emails, google_sheets_read, google_sheets_write,
    google_calendar_list,
    # Browser automation tools
    web_automate, browser_navigate_and_analyze, fill_web_form,
    browser_extract_data, extract_contact_info,
)

from prompts import build_agent_instruction as build_nivora_instruction
from infin_prompts import build_agent_instruction as build_infin_instruction

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s — %(message)s")
logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

class AgentConfig:
    # Edge TTS voices (FREE - Microsoft Neural Voices)
    # Infin (Jarvis) - Professional female voice
    INFIN_VOICE = "en-US-AriaNeural"
    # Nivora - Calm male technical voice
    NIVORA_VOICE = "en-US-GuyNeural"
    # BrowserAgent - Friendly female voice
    BROWSER_VOICE = "en-US-JennyNeural"

    # Keep old IDs for compatibility with GenericAgent voice mapping
    NIVORA_VOICE_ID = "cgSgspJ2msm6clMCkdW9"
    INFIN_VOICE_ID = "iP95p4xoKVk53GoZ742B"
    BROWSER_VOICE_ID = "browser_jenny_neural"  # New ID for browser agent

    NIVORA_TOOLS = [
        web_search, get_weather, system_control,
        spotify_play, spotify_control, spotify_shortcut,
        youtube_shortcut, open_spotify, play_youtube_video, open_youtube,
        pause_media, next_track, previous_track, volume_control,
        open_website, describe_screen_share,
    ]

    INFIN_TOOLS = [
        send_email, read_emails, google_sheets_read, google_sheets_write,
        google_calendar_list, take_note, read_notes, set_reminder,
        web_search, get_weather, open_website,
        pause_media, next_track, previous_track, volume_control,
        describe_screen_share,
    ]

    BROWSER_TOOLS = [
        # Core browser automation
        web_automate, browser_navigate_and_analyze, fill_web_form,
        browser_extract_data, extract_contact_info, open_website,
        # Enhanced browser tools (to be imported)
        web_search, get_weather,
        play_youtube_video, open_youtube,
        describe_screen_share,
    ]

    MCP_TOOLS = [
        "spotify_play", "spotify_pause", "spotify_search", "spotify_shuffle",
        "youtube_open", "open_app", "open_website", "open_github",
    ]


# ---------------------------------------------------------------------------
# Agent Definitions
# ---------------------------------------------------------------------------

class InfinAgent(GenericAgent):
    """
    Infin (Jarvis) — Life Management Assistant
    
    Handles email, calendar, notes, reminders, and productivity.
    Can transfer to NivoraAgent for technical/study topics.
    Can analyze shared screens using vision AI.
    """
    
    def __init__(self, chat_ctx: ChatContext = None, returning: bool = False) -> None:
        # Build instructions with transfer capabilities
        base_instructions = build_infin_instruction()
        transfer_instructions = """

AGENT TRANSFER CAPABILITY:
If the user needs help with coding, debugging, learning, research, technical problems,
study topics, or asks questions like "how does X work" or "explain Y concept",
immediately call the tool call_nivora_agent to connect them to Nivora.

If the user needs help with browser automation, web forms, online shopping, social media posting,
data extraction from websites, or any web-related tasks, immediately call the tool
call_browser_agent to connect them to the Browser Assistant.

Examples that trigger transfer to Nivora:
- "Help me debug this Python code"
- "Explain how neural networks work"
- "I need to learn React"
- "Fix this error in my program"
- "How does Docker work?"
- "Research machine learning algorithms"

Examples that trigger transfer to Browser Assistant:
- "Fill out this web form for me"
- "Find the cheapest price for this product"
- "Post this content to my LinkedIn"
- "Extract contact info from this website"
- "Help me with online shopping"
- "Automate this web task"

SCREEN SHARE VISION CAPABILITY:
You have access to the describe_screen_share tool which uses AWS Nova Pro vision AI
to analyze the user's shared screen. Use this when:
- User asks you to "look at my screen", "what do you see", "read this"
- User shares an error message, document, or interface they want help with
- User asks about something visible on their screen

Example: User shares screen showing calendar app → You can see and describe it.

CRITICAL: You are a VOICE assistant. Never output <thinking> tags or internal monologue.
Just call tools and respond naturally with the results.
"""
        
        # Different greeting if returning from Nivora
        context_note = "\nThe user is returning from Nivora. Welcome them back warmly." if returning else ""
        
        super().__init__(
            instructions=base_instructions + transfer_instructions + context_note,
            llm=get_nova_pro_llm(temperature=0.7),
            chat_ctx=chat_ctx,
            voice_id=AgentConfig.INFIN_VOICE_ID,
            agent_name="Infin"
        )
        # Add Infin-specific tools using proper method
        self.update_tools(AgentConfig.INFIN_TOOLS.copy())
    
    def _get_goodbye_message(self) -> str:
        return "Goodbye. Have a wonderful day."
    
    @function_tool
    async def call_nivora_agent(self, topic: str):
        """
        Transfer the conversation to Nivora for technical/study assistance.

        Args:
            topic: The technical topic or problem the user needs help with
        """
        logger.info(f"Infin transferring to Nivora with topic: {topic}")

        # Create Nivora agent with shared context
        nivora_agent = NivoraAgent(
            chat_ctx=self.chat_ctx,
            entry_topic=topic
        )

        # Switch voice before transfer
        await nivora_agent.switch_voice()

        # Return agent and smooth handoff message
        return nivora_agent, f"Transferring you to Nivora for {topic}."

    @function_tool
    async def call_browser_agent(self, task: str):
        """
        Transfer the conversation to Browser Assistant for web automation tasks.

        Args:
            task: The browser/web task the user needs help with
        """
        logger.info(f"Infin transferring to BrowserAgent with task: {task}")

        # Import here to avoid circular imports
        from browser_agent import BrowserAgent

        # Create Browser agent with shared context
        browser_agent = BrowserAgent(
            chat_ctx=self.chat_ctx,
            entry_topic=task
        )

        # Switch voice before transfer
        await browser_agent.switch_voice()

        # Return agent and smooth handoff message
        return browser_agent, f"Let me connect you with our Browser Assistant who specializes in {task}!"


class NivoraAgent(GenericAgent):
    """
    Nivora — Study/Technical Companion
    
    Handles coding, debugging, research, learning, and technical problems.
    Can transfer back to InfinAgent for life management.
    Can analyze shared screens using vision AI - especially useful for debugging!
    """
    
    def __init__(self, chat_ctx: ChatContext = None, entry_topic: str = None) -> None:
        # Build context-aware instructions
        base_instructions = build_nivora_instruction()
        
        transfer_instructions = """

AGENT TRANSFER CAPABILITY:
If the user asks about email, calendar, scheduling, appointments, meetings,
notes, reminders, tasks, or life management topics, immediately call the
tool call_infin_agent to connect them to Infin (Jarvis).

If the user needs help with browser automation, web forms, online shopping, social media posting,
data extraction from websites, or any web-related tasks, immediately call the tool
call_browser_agent to connect them to the Browser Assistant.

Examples that trigger transfer to Infin:
- "Check my calendar"
- "Send an email to..."
- "What meetings do I have?"
- "Set a reminder for..."
- "Take a note"
- "What's on my agenda?"

Examples that trigger transfer to Browser Assistant:
- "Fill out this web form for me"
- "Find the cheapest price for this product"
- "Post this content to my LinkedIn"
- "Extract contact info from this website"
- "Help me with online shopping"
- "Automate this web task"

SCREEN SHARE VISION CAPABILITY:
You have access to the describe_screen_share tool which uses AWS Nova Pro vision AI
to analyze the user's shared screen. This is EXTREMELY useful for:
- Debugging code errors (user shares IDE with error messages)
- Reading stack traces and error logs
- Analyzing UI/UX issues in applications
- Helping with documentation or research (reading papers, articles)
- Understanding system configurations
- Reviewing code structure and architecture

When the user shares their screen:
- Proactively offer to look at it if they're describing a problem
- Use specific questions: "What's the error message?", "Which file is open?"
- Combine vision analysis with your technical knowledge

CONVERSATION FLOW:
- When you've helped with the technical issue, ask: "Is there anything else I can help you with?"
- If they're done with technical topics, suggest: "Would you like me to transfer you back to Infin?"
- Only use end_conversation if they explicitly want to leave entirely.
"""
        
        # Add entry topic context if provided
        topic_context = f"\nIMPORTANT: The user was transferred to you for this specific topic: {entry_topic}\nAddress this immediately." if entry_topic else ""
        
        super().__init__(
            instructions=base_instructions + transfer_instructions + topic_context,
            llm=get_nova_pro_llm(temperature=0.7),
            chat_ctx=chat_ctx,
            voice_id=AgentConfig.NIVORA_VOICE_ID,
            agent_name="Nivora"
        )
        # Add Nivora-specific tools using proper method
        self.update_tools(AgentConfig.NIVORA_TOOLS.copy())
        self.entry_topic = entry_topic
    
    def _get_goodbye_message(self) -> str:
        return "Goodbye. I'll be here when you need me."
    
    @function_tool
    async def call_infin_agent(self):
        """
        Transfer the conversation back to Infin for life management assistance.
        """
        logger.info("Nivora transferring back to Infin")

        # Create Infin agent with shared context
        infin_agent = InfinAgent(
            chat_ctx=self.chat_ctx,
            returning=True  # Flag to customize greeting
        )

        # Switch voice before transfer
        await infin_agent.switch_voice()

        # Return agent and smooth handoff message
        return infin_agent, "Transferring you back to Infin for life management."

    @function_tool
    async def call_browser_agent(self, task: str):
        """
        Transfer the conversation to Browser Assistant for web automation tasks.

        Args:
            task: The browser/web task the user needs help with
        """
        logger.info(f"Nivora transferring to BrowserAgent with task: {task}")

        # Import here to avoid circular imports
        from browser_agent import BrowserAgent

        # Create Browser agent with shared context
        browser_agent = BrowserAgent(
            chat_ctx=self.chat_ctx,
            entry_topic=task
        )

        # Switch voice before transfer
        await browser_agent.switch_voice()

        # Return agent and smooth handoff message
        return browser_agent, f"Let me connect you with our Browser Assistant for {task}!"


# ---------------------------------------------------------------------------
# MCP Server
# ---------------------------------------------------------------------------

async def _build_mcp_server() -> MCPServerHTTP | None:
    if not N8N_MCP_URL:
        logger.warning("N8N_MCP_URL not set — MCP tools unavailable")
        return None

    server = MCPServerHTTP(
        url=N8N_MCP_URL,
        transport_type="sse",
        headers={"Authorization": f"Bearer {N8N_BEARER_TOKEN}"},
        allowed_tools=AgentConfig.MCP_TOOLS,
    )

    try:
        import httpx
        async with httpx.AsyncClient(timeout=5) as client:
            resp = await client.get(N8N_MCP_URL)
            logger.info("MCP server reachable: %s (HTTP %s)", N8N_MCP_URL, resp.status_code)
    except Exception as e:
        logger.warning("MCP server unreachable: %s", e)
        return None

    return server


async def _validate_aws() -> None:
    """Validate AWS Nova Pro configuration."""
    if not validate_nova_config():
        raise RuntimeError("AWS credentials missing or Nova Pro not available")
    region = os.getenv("AWS_REGION", "us-east-1")
    model = os.getenv("AWS_BEDROCK_MODEL", "amazon.nova-pro-v1:0")
    logger.info(f"Using AWS Nova Pro: {model} in {region}")


# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# Screen Share Tracking
# ---------------------------------------------------------------------------

async def _setup_screen_share_tracking(ctx: JobContext):
    """
    Monitor the room for screen-share tracks and automatically start capturing
    frames when a participant begins screen sharing.
    """
    
    @ctx.room.on("track_subscribed")
    def on_track_subscribed(
        track: rtc.Track,
        publication: rtc.TrackPublication,
        participant: rtc.RemoteParticipant,
    ):
        # Only capture screen-share video tracks
        if track.kind == rtc.TrackKind.KIND_VIDEO and track.source == rtc.TrackSource.SOURCE_SCREEN_SHARE:
            logger.info(
                f"Screen share detected from {participant.identity}. Starting frame capture."
            )
            # Start async frame capture task
            asyncio.create_task(start_frame_capture(track))
    
    @ctx.room.on("track_unsubscribed")
    def on_track_unsubscribed(
        track: rtc.Track,
        publication: rtc.TrackPublication,
        participant: rtc.RemoteParticipant,
    ):
        if track.source == rtc.TrackSource.SOURCE_SCREEN_SHARE:
            logger.info(f"Screen share ended from {participant.identity}.")
    
    logger.info("Screen share tracking enabled - ready to capture shared screens")


# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------

async def entrypoint(ctx: JobContext):
    logger.info("=== Multi-Agent Nivora/Infin (Azure GPT-4o Edition) Starting ===")
    logger.info("Room: %s", ctx.room.name if ctx.room else "N/A")

    await _validate_aws()
    await ctx.connect()
    logger.info("Connected to LiveKit")

    # Setup screen share tracking
    await _setup_screen_share_tracking(ctx)

    mcp_server = await _build_mcp_server()
    mcp_servers = [mcp_server] if mcp_server else []

    # Build AgentSession with Infin as default
    # Using FREE Edge TTS + Sarvam STT + Azure GPT-4o
    session = AgentSession(
        vad=silero.VAD.load(min_silence_duration=1.5),
        # Sarvam STT
        stt=sarvam.STT(language="en-IN", model="saaras:v3", mode="transcribe"),
        # AWS Nova Pro LLM
        llm=get_nova_pro_llm(temperature=0.8),
        # FREE TTS: Microsoft Edge Neural Voices (no API key needed!)
        tts=edge_tts_plugin.TTS(
            voice=AgentConfig.INFIN_VOICE,  # Start with Infin voice (AriaNeural)
        ),
        mcp_servers=mcp_servers,
    )
    
    # Store session reference for voice switching during transfers
    GenericAgent.set_session(session)
    
    # Create initial agent (Infin)
    initial_agent = InfinAgent()

    try:
        await session.start(
            room=ctx.room,
            agent=initial_agent,
            room_options=room_io.RoomOptions(
                video_input=True,  # Enable video input from user's camera
            ),
        )
        logger.info("Multi-agent session started with Infin (Jarvis) as default agent.")
        logger.info("LLM: Azure OpenAI GPT-4o - Intelligent and powerful!")
        logger.info("Voice switching enabled - agents will change voice on transfer.")
        logger.info("Screen share analysis ready - share your screen to enable vision tools.")
        logger.info("Video input enabled - camera feed can be analyzed.")
    except Exception as e:
        logger.error("Session failed: %s", e, exc_info=True)
        raise


if __name__ == "__main__":
    agents.cli.run_app(agents.WorkerOptions(entrypoint_fnc=entrypoint))

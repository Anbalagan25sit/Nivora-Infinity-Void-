"""
Nivora Multi-Agent System — Nivora & Infin with Dynamic Switching
------------------------------------------------------------------
Stack: AWS Nova Pro (LLM) · Sarvam STT · Edge TTS (FREE) · Silero VAD

A single AgentSession with a custom agent that switches personas based on user input.

FREE TTS: Edge TTS (Microsoft Neural Voices - no API key needed)
"""

import logging
import os
from livekit import agents
from livekit.agents import Agent, AgentSession, JobContext, room_io
from livekit.agents.job import get_job_context
from livekit.agents.llm import function_tool
from livekit import api
from livekit.agents.llm.mcp import MCPServerHTTP
from livekit.plugins import aws, sarvam, silero
from livekit.agents.tts.tts import TTS as BaseTTS, TTSCapabilities

# Import our custom Edge TTS plugin
import edge_tts_plugin

from aws_config import aws_region, bedrock_model
from config import N8N_MCP_URL, N8N_BEARER_TOKEN

# Tools
from tools import (
    open_website, web_search, get_weather, system_control,
    pause_media, next_track, previous_track, volume_control,
    take_note, read_notes, set_reminder, describe_screen_share,
    spotify_play, spotify_control, spotify_shortcut, youtube_shortcut,
    open_spotify, play_youtube_video, open_youtube,
    send_email, read_emails, google_sheets_read, google_sheets_write,
    google_calendar_list,
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
    NIVORA_VOICE = "en-US-GuyNeural"    # Calm male technical voice
    INFIN_VOICE = "en-US-AriaNeural"    # Professional female voice

    # Keep old IDs for compatibility
    NIVORA_VOICE_ID = "cgSgspJ2msm6clMCkdW9"
    INFIN_VOICE_ID = "iP95p4xoKVk53GoZ742B"

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

    MCP_TOOLS = [
        "spotify_play", "spotify_pause", "spotify_search", "spotify_shuffle",
        "youtube_open", "open_app", "open_website", "open_github",
    ]


# ---------------------------------------------------------------------------
# Dynamic TTS - Properly implements BaseTTS interface
# ---------------------------------------------------------------------------

class DynamicVoiceTTS(BaseTTS):
    """TTS that can switch between Nivora and Infin voices at runtime using Edge TTS (FREE)."""

    def __init__(self):
        # Initialize with default voice (Infin - AriaNeural)
        self._current_voice = AgentConfig.INFIN_VOICE
        self._tts = edge_tts_plugin.TTS(voice=self._current_voice)

        # Get capabilities from internal TTS
        caps = getattr(self._tts, 'capabilities', TTSCapabilities(streaming=True))
        sample_rate = getattr(self._tts, '_sample_rate', 24000)
        num_channels = getattr(self._tts, '_num_channels', 1)

        # Initialize base class properly
        super().__init__(
            capabilities=caps,
            sample_rate=sample_rate,
            num_channels=num_channels
        )

    def switch_to(self, persona: str):
        """Switch TTS voice based on persona."""
        new_voice = AgentConfig.NIVORA_VOICE if persona == "nivora" else AgentConfig.INFIN_VOICE
        if new_voice != self._current_voice:
            self._current_voice = new_voice
            self._tts = edge_tts_plugin.TTS(voice=new_voice)
            # Update base class attributes from new TTS
            if hasattr(self._tts, 'capabilities'):
                self._capabilities = self._tts.capabilities
            if hasattr(self._tts, 'sample_rate'):
                self._sample_rate = self._tts.sample_rate
            elif hasattr(self._tts, '_sample_rate'):
                self._sample_rate = self._tts._sample_rate
            if hasattr(self._tts, 'num_channels'):
                self._num_channels = self._tts.num_channels
            elif hasattr(self._tts, '_num_channels'):
                self._num_channels = self._tts._num_channels
            logger.info(f"TTS voice switched to {persona}: {new_voice}")

    @property
    def sample_rate(self) -> int:
        return self._sample_rate

    @property
    def num_channels(self) -> int:
        return self._num_channels

    @property
    def model(self) -> str:
        return "edge-tts"

    # Delegate synthesize to internal TTS
    def synthesize(self, *args, **kwargs):
        return self._tts.synthesize(*args, **kwargs)

    # Delegate stream to internal TTS
    def stream(self, *, conn_options=None):
        """Return a streaming TTS context manager from the internal TTS."""
        return self._tts.stream(conn_options=conn_options)

    # Delegate aclose if needed
    async def aclose(self):
        if hasattr(self._tts, 'aclose'):
            await self._tts.aclose()


# ---------------------------------------------------------------------------
# Router Agent with Dynamic Switching
# ---------------------------------------------------------------------------

class RouterAgent(Agent):
    """
    Agent that dynamically switches between Nivora and Infin personas.
    Overrides chat() to intercept and redirect to appropriate persona.
    """

    def __init__(self, session: AgentSession, **kwargs):
        # Initialize with Infin as default
        self.session_ref = session
        self.current_persona = "infin"
        self.nivora_instruction = build_nivora_instruction()
        self.infin_instruction = build_infin_instruction()
        self.nivora_tools = AgentConfig.NIVORA_TOOLS
        self.infin_tools = AgentConfig.INFIN_TOOLS

        # Start with Infin config
        super().__init__(
            instructions=self.infin_instruction,
            tools=self.infin_tools,
            **kwargs
        )

    async def on_enter(self):
        """Automatically greet the user when entering the call."""
        # Get the appropriate greeting based on current persona
        greeting = "How may I assist you today?" if self.current_persona == "infin" else "I'm here. What are we looking at?"
        await self.session.generate_reply(instructions=greeting)
        logger.info(f"{self.current_persona.title()} greeted the user")

    @function_tool
    async def end_conversation(self):
        """Call this function when the user wants to end the conversation."""
        # Interrupt any ongoing speech
        if self.session:
            self.session.interrupt()

        # Say goodbye with the current persona
        goodbye_msg = "Goodbye. Have a wonderful day." if self.current_persona == "infin" else "Goodbye. I'll be here when you need me."
        await self.session.generate_reply(
            instructions=goodbye_msg,
            allow_interruptions=False
        )

        # End the room
        job_ctx = get_job_context()
        if job_ctx and job_ctx.room:
            await job_ctx.api.room.delete_room(api.DeleteRoomRequest(room=job_ctx.room.name))
            logger.info("Room deleted, conversation ended")

    def _classify_intent(self, user_input: str) -> str:
        """Classify user input into 'nivora' or 'infin'."""
        text = user_input.lower().strip()

        # Explicit switch commands (highest priority)
        # Check for persona names first as they override everything
        if any(kw in text for kw in ["switch to nivora", "use nivora", "activate nivora", "call nivora", "ask nivora", "nivora mode"]):
            return "nivora"
        if any(kw in text for kw in ["switch to infin", "use infin", "activate infin", "call infin", "ask infin", "infin mode"]):
            return "infin"
        if any(kw in text for kw in ["use jarvis", "activate jarvis", "call jarvis", "ask jarvis", "jarvis mode"]):
            return "infin"  # Jarvis is Infin

        # Keyword-based classification
        LIFE = {
            "email", "gmail", "send email", "read email", "calendar", "schedule",
            "meeting", "appointment", "event", "remind", "reminder", "note", "notes",
            "weather", "time", "date", "today", "tomorrow", "upcoming", "agenda",
            "todo", "task", "list", "organize", "plan", "primary", "free", "busy",
            "gmail", "inbox", "compose", "check email", "send mail",
            "schedule meeting", "book appointment", "set reminder", "take note",
            "google calendar", "availability", "am i free", "busy calendar",
        }
        STUDY = {
            "study", "learn", "research", "code", "python", "debug", "program",
            "develop", "algorithm", "project", "hackathon", "problem", "solution",
            "git", "github", "docker", "api", "database", "architecture", "fix",
            "error", "bug", "assignment", "homework", "thesis", "explain", "concept",
            "c++", "javascript", "java", "rust", "go", "sql", "machine learning",
            "ai", "artificial intelligence", "data science", "web dev", "app dev",
            "vscode", "terminal", "bash", "linux", "wsl", "coding", "software",
            "how does", "what is", "why does", "tutorial", "guide", "documentation",
            "optimization", "performance", "security", "networking", "infrastructure",
            "deploy", "server", "backend", "frontend", "fullstack", "microservices",
        }

        life_score = sum(1 for kw in LIFE if kw in text)
        study_score = sum(1 for kw in STUDY if kw in text)

        if life_score > 0 and study_score == 0:
            return "infin"
        if study_score > 0 and life_score == 0:
            return "nivora"
        return self.current_persona  # Keep current if ambiguous

    def _switch_persona(self, persona: str) -> bool:
        """Switch to a different persona if needed."""
        if persona == self.current_persona:
            return False

        old = self.current_persona
        self.current_persona = persona

        if persona == "nivora":
            self.instructions = self.nivora_instruction
            self.tools = self.nivora_tools
        else:
            self.instructions = self.infin_instruction
            self.tools = self.infin_tools

        # Switch TTS voice via session reference
        if self.session_ref and hasattr(self.session_ref, '_tts'):
            tts = self.session_ref._tts
            if isinstance(tts, DynamicVoiceTTS):
                tts.switch_to(persona)

        logger.info(f"Persona switched: {old} -> {persona}")
        return True

    async def chat(self, *args, **kwargs):
        """
        Override chat to add persona switching before each turn.
        The session calls agent.chat() internally for each user message.
        """
        # Get the user message from the chat context
        if self.chat_context and self.chat_context.messages:
            last_msg = self.chat_context.messages[-1]
            if hasattr(last_msg, 'content'):
                user_input = last_msg.content
                if isinstance(user_input, str) and user_input.strip():
                    # Classify and switch if needed
                    new_persona = self._classify_intent(user_input)
                    if self._switch_persona(new_persona):
                        logger.info(f"Active persona is now: {self.current_persona}")

        # Continue with normal agent processing
        return await super().chat(*args, **kwargs)


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
    aws_key = (os.getenv("AWS_ACCESS_KEY_ID") or "").strip()
    aws_secret = (os.getenv("AWS_SECRET_ACCESS_KEY") or "").strip()
    if not aws_key or not aws_secret:
        raise RuntimeError("AWS credentials missing in .env")
    logger.info(f"Using AWS Bedrock: {bedrock_model()}")


# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------

async def entrypoint(ctx: JobContext):
    logger.info("=== Multi-Agent Nivora/Infin Starting ===")
    logger.info("Room: %s", ctx.room.name if ctx.room else "N/A")

    await _validate_aws()
    await ctx.connect()
    logger.info("Connected to LiveKit")

    mcp_server = await _build_mcp_server()
    mcp_servers = [mcp_server] if mcp_server else []

    # Create dynamic TTS
    dynamic_tts = DynamicVoiceTTS()

    # Build AgentSession with Sarvam STT + FREE Edge TTS
    session = AgentSession(
        vad=silero.VAD.load(min_silence_duration=1.5),
        # Sarvam STT
        stt=sarvam.STT(language="en-IN", model="saaras:v3", mode="transcribe"),
        llm=aws.LLM(model=bedrock_model(), temperature=0.8, region=aws_region()),
        tts=dynamic_tts,  # Edge TTS (FREE)
        mcp_servers=mcp_servers,
    )

    # Create RouterAgent - will be passed session reference
    agent = RouterAgent(session=session)

    try:
        await session.start(
            room=ctx.room, 
            agent=agent,
            room_options=room_io.RoomOptions(
                video_input=True,  # Enable video input from user's camera
            ),
        )
        logger.info("Multi-agent session started successfully.")
    except Exception as e:
        logger.error("Session failed: %s", e, exc_info=True)
        raise


if __name__ == "__main__":
    agents.cli.run_app(agents.WorkerOptions(entrypoint_fnc=entrypoint))

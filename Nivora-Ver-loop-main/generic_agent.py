"""
Generic Agent Base Class
------------------------
Base class for all Nivora/Infin agents with shared functionality.
Implements smooth agent transfers with voice switching and context preservation.
Includes response filtering to prevent TTS errors from thinking tags.
"""

import logging
import re
from livekit.agents import Agent
from livekit.agents.llm import ChatContext, function_tool

logger = logging.getLogger(__name__)


def strip_thinking_tags(text: str) -> str:
    """
    Remove <thinking>, <reflection>, and other XML-like tags that TTS cannot speak.
    This is a safeguard in case the LLM ignores instructions.
    """
    if not text:
        return text
    
    # Remove thinking tags
    text = re.sub(r'<thinking>.*?</thinking>', '', text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r'<reflection>.*?</reflection>', '', text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r'<reasoning>.*?</reasoning>', '', text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r'<analysis>.*?</analysis>', '', text, flags=re.DOTALL | re.IGNORECASE)
    
    # Remove any other XML-like tags that might appear
    text = re.sub(r'<[^>]+>.*?</[^>]+>', '', text, flags=re.DOTALL)
    
    # Clean up extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text


class GenericAgent(Agent):
    """
    Base agent class with common functionality for Nivora agents.
    Handles chat context passing, session awareness, and provides shared tools.
    """
    
    # Class-level session reference for voice switching
    _session_ref = None
    
    def __init__(
        self,
        instructions: str,
        llm,
        chat_ctx: ChatContext = None,
        voice_id: str = None,
        agent_name: str = "Assistant",
        **kwargs
    ):
        # Store these as instance variables
        self.voice_id = voice_id
        self.agent_name = agent_name

        # Initialize the LiveKit Agent with chat context
        # The chat_ctx property will be managed by the LiveKit Agent base class
        super().__init__(
            instructions=instructions,
            llm=llm,
            chat_ctx=chat_ctx if chat_ctx else ChatContext(),
            **kwargs
        )
    
    @classmethod
    def set_session(cls, session):
        """Store session reference for voice switching during transfers."""
        cls._session_ref = session
    
    async def switch_voice(self):
        """
        Switch TTS voice when this agent becomes active.
        Called automatically during agent transfer.
        Uses Edge TTS (free Microsoft Neural voices).
        """
        if not self.voice_id or not self._session_ref:
            return

        try:
            import edge_tts_plugin

            # Map ElevenLabs voice ID to Edge TTS voice name
            edge_voice = edge_tts_plugin.get_voice_for_id(self.voice_id)

            # Create new TTS with this agent's voice
            new_tts = edge_tts_plugin.TTS(voice=edge_voice)

            # Update session TTS
            if hasattr(self._session_ref, '_tts'):
                self._session_ref._tts = new_tts
                logger.info(f"Voice switched to {self.agent_name}: {edge_voice}")
        except Exception as e:
            logger.warning(f"Failed to switch voice: {e}")
    
    @function_tool
    async def end_conversation(self):
        """
        Called when the user wants to end the conversation or says goodbye.
        """
        from livekit.agents.job import get_job_context
        from livekit import api
        
        # Personalized goodbye based on agent
        goodbye_msg = self._get_goodbye_message()
        
        # Interrupt any ongoing speech
        if self._session_ref:
            self._session_ref.interrupt()
        
        # Say goodbye
        await self._session_ref.generate_reply(
            instructions=goodbye_msg,
            allow_interruptions=False
        )
        
        # End the room
        job_ctx = get_job_context()
        if job_ctx and job_ctx.room:
            await job_ctx.api.room.delete_room(
                api.DeleteRoomRequest(room=job_ctx.room.name)
            )
            logger.info("Room deleted, conversation ended")
    
    def _get_goodbye_message(self) -> str:
        """Override in subclasses for personalized goodbyes."""
        return "Goodbye. Have a wonderful day."
    
    async def generate_reply(self, *args, **kwargs):
        """
        Override generate_reply to filter thinking tags from LLM responses.
        This prevents TTS errors when the LLM outputs <thinking> tags.
        """
        # Get the original response
        response = await super().generate_reply(*args, **kwargs)
        
        # If response has text content, filter it
        if response and hasattr(response, 'content'):
            if isinstance(response.content, str):
                filtered = strip_thinking_tags(response.content)
                if filtered != response.content:
                    logger.warning(f"Filtered thinking tags from response: {response.content[:100]}...")
                    response.content = filtered
        
        return response

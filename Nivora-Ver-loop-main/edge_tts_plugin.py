"""
Edge TTS Plugin for LiveKit Agents
----------------------------------
Free Microsoft Neural TTS voices using edge-tts package.
No API key required!

Available voices (examples):
- en-US-AriaNeural (female, natural, sweet)
- en-US-GuyNeural (male, friendly)
- en-US-JennyNeural (female, warm)
- en-GB-SoniaNeural (British female)
- en-IN-NeerjaNeural (Indian English female)

Full list: https://github.com/rany2/edge-tts
"""

import asyncio
import io
import logging
import re
from dataclasses import dataclass
from typing import AsyncIterator

import edge_tts
from livekit import rtc
from livekit.agents import tts, utils
from livekit.agents.types import DEFAULT_API_CONNECT_OPTIONS, APIConnectOptions

logger = logging.getLogger(__name__)

# Default sample rate for Edge TTS (24kHz)
EDGE_TTS_SAMPLE_RATE = 24000
EDGE_TTS_CHANNELS = 1


def strip_thinking_tags(text: str) -> str:
    """
    Remove <thinking>, <reflection>, and other XML-like tags that TTS cannot speak.
    This filters out AWS Nova Pro's internal reasoning that shouldn't be spoken.
    """
    if not text:
        return text

    # Remove thinking tags and their content
    text = re.sub(r'<thinking>.*?</thinking>', '', text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r'<reflection>.*?</reflection>', '', text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r'<reasoning>.*?</reasoning>', '', text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r'<analysis>.*?</analysis>', '', text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r'<internal>.*?</internal>', '', text, flags=re.DOTALL | re.IGNORECASE)

    # Remove any other XML-like tags that might appear
    text = re.sub(r'<[a-zA-Z_][^>]*>.*?</[a-zA-Z_][^>]*>', '', text, flags=re.DOTALL)

    # Remove standalone opening/closing tags
    text = re.sub(r'</?[a-zA-Z_][^>]*>', '', text)

    # Clean up extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()

    return text


@dataclass
class _TTSOptions:
    voice: str
    rate: str  # e.g., "+0%", "-10%", "+20%"
    volume: str  # e.g., "+0%", "-10%", "+20%"
    pitch: str  # e.g., "+0Hz", "-10Hz", "+20Hz"


class TTS(tts.TTS):
    """
    Edge TTS implementation for LiveKit Agents.
    Uses Microsoft's free neural TTS voices via edge-tts package.
    """

    def __init__(
        self,
        *,
        voice: str = "en-US-AriaNeural",
        rate: str = "+0%",
        volume: str = "+0%",
        pitch: str = "+0Hz",
    ) -> None:
        """
        Create a new Edge TTS instance.

        Args:
            voice: Voice name (e.g., "en-US-AriaNeural", "en-US-GuyNeural")
            rate: Speech rate adjustment (e.g., "+10%", "-20%")
            volume: Volume adjustment (e.g., "+10%", "-20%")
            pitch: Pitch adjustment (e.g., "+10Hz", "-20Hz")
        """
        super().__init__(
            capabilities=tts.TTSCapabilities(streaming=True, aligned_transcript=False),
            sample_rate=EDGE_TTS_SAMPLE_RATE,
            num_channels=EDGE_TTS_CHANNELS,
        )

        self._opts = _TTSOptions(
            voice=voice,
            rate=rate,
            volume=volume,
            pitch=pitch,
        )
        logger.info(f"Edge TTS initialized with voice: {voice}")

    @property
    def model(self) -> str:
        return "edge-tts"

    @property
    def provider(self) -> str:
        return "microsoft-edge"

    def update_options(
        self,
        *,
        voice: str | None = None,
        rate: str | None = None,
        volume: str | None = None,
        pitch: str | None = None,
    ) -> None:
        """Update TTS options dynamically (useful for voice switching)."""
        if voice is not None:
            self._opts.voice = voice
            logger.info(f"Edge TTS voice updated to: {voice}")
        if rate is not None:
            self._opts.rate = rate
        if volume is not None:
            self._opts.volume = volume
        if pitch is not None:
            self._opts.pitch = pitch

    def synthesize(
        self,
        text: str,
        *,
        conn_options: APIConnectOptions = DEFAULT_API_CONNECT_OPTIONS,
    ) -> "ChunkedStream":
        return ChunkedStream(
            tts=self,
            input_text=text,
            conn_options=conn_options,
            opts=self._opts,
        )

    def stream(
        self,
        *,
        conn_options: APIConnectOptions = DEFAULT_API_CONNECT_OPTIONS,
    ) -> "SynthesizeStream":
        return SynthesizeStream(
            tts=self,
            conn_options=conn_options,
            opts=self._opts,
        )


class ChunkedStream(tts.ChunkedStream):
    """Non-streaming synthesis that returns audio in chunks."""

    def __init__(
        self,
        *,
        tts: TTS,
        input_text: str,
        conn_options: APIConnectOptions,
        opts: _TTSOptions,
    ) -> None:
        # Filter out thinking tags before storing
        filtered_text = strip_thinking_tags(input_text)
        super().__init__(tts=tts, input_text=filtered_text, conn_options=conn_options)
        self._opts = opts

    async def _run(self, output_emitter: tts.AudioEmitter) -> None:
        """Generate audio using edge-tts."""
        # Double-check filtering
        text_to_speak = strip_thinking_tags(self._input_text)

        if not text_to_speak.strip():
            logger.warning("Edge TTS: No text to speak after filtering thinking tags")
            return

        try:
            # Create edge-tts communicate instance
            communicate = edge_tts.Communicate(
                text=text_to_speak,
                voice=self._opts.voice,
                rate=self._opts.rate,
                volume=self._opts.volume,
                pitch=self._opts.pitch,
            )

            # Collect all audio data
            audio_data = io.BytesIO()

            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    audio_data.write(chunk["data"])

            # Get the complete audio
            audio_bytes = audio_data.getvalue()

            if not audio_bytes:
                logger.warning("Edge TTS returned no audio data")
                return

            # Initialize the emitter with MP3 format (edge-tts outputs MP3)
            output_emitter.initialize(
                request_id=utils.shortuuid(),
                sample_rate=EDGE_TTS_SAMPLE_RATE,
                num_channels=EDGE_TTS_CHANNELS,
                mime_type="audio/mpeg",
                stream=False,
            )

            # Push the audio data
            output_emitter.push(audio_bytes)
            output_emitter.flush()

        except Exception as e:
            logger.error(f"Edge TTS synthesis error: {e}")
            raise


class SynthesizeStream(tts.SynthesizeStream):
    """Streaming synthesis that processes text incrementally."""

    def __init__(
        self,
        *,
        tts: TTS,
        conn_options: APIConnectOptions,
        opts: _TTSOptions,
    ) -> None:
        super().__init__(tts=tts, conn_options=conn_options)
        self._opts = opts
        self._segments_queue: asyncio.Queue[str | None] = asyncio.Queue()

    async def _run(self, output_emitter: tts.AudioEmitter) -> None:
        """Process text segments and generate audio."""

        output_emitter.initialize(
            request_id=utils.shortuuid(),
            sample_rate=EDGE_TTS_SAMPLE_RATE,
            num_channels=EDGE_TTS_CHANNELS,
            mime_type="audio/mpeg",
            stream=True,
        )

        segment_id = 0
        current_text = ""

        async for data in self._input_ch:
            if isinstance(data, str):
                current_text += data
            elif isinstance(data, self._FlushSentinel):
                # Filter out thinking tags before synthesis
                filtered_text = strip_thinking_tags(current_text)

                if filtered_text.strip():
                    # Generate audio for this segment
                    output_emitter.start_segment(segment_id=str(segment_id))

                    try:
                        communicate = edge_tts.Communicate(
                            text=filtered_text,  # Use filtered text!
                            voice=self._opts.voice,
                            rate=self._opts.rate,
                            volume=self._opts.volume,
                            pitch=self._opts.pitch,
                        )

                        async for chunk in communicate.stream():
                            if chunk["type"] == "audio":
                                output_emitter.push(chunk["data"])

                    except Exception as e:
                        logger.error(f"Edge TTS streaming error: {e}")
                        raise

                    output_emitter.end_segment()
                    segment_id += 1
                    current_text = ""


# Voice mapping for the two personas
VOICE_MAPPING = {
    # ElevenLabs voice IDs -> Edge TTS voices
    "iP95p4xoKVk53GoZ742B": "en-US-AriaNeural",   # Infin (Jarvis) - professional female
    "cgSgspJ2msm6clMCkdW9": "en-US-GuyNeural",    # Nivora - calm male technical
    "browser_jenny_neural": "en-US-JennyNeural",   # BrowserAgent - friendly female
}

# Alternative voice options
AVAILABLE_VOICES = {
    "en-US-AriaNeural": "Female, natural, sweet (recommended for Infin)",
    "en-US-JennyNeural": "Female, warm, conversational",
    "en-US-GuyNeural": "Male, friendly, casual (recommended for Nivora)",
    "en-US-DavisNeural": "Male, calm, professional",
    "en-US-JasonNeural": "Male, authoritative",
    "en-GB-SoniaNeural": "British female, elegant",
    "en-GB-RyanNeural": "British male, professional",
    "en-IN-NeerjaNeural": "Indian English female",
    "en-IN-PrabhatNeural": "Indian English male",
    "en-AU-NatashaNeural": "Australian female",
    "en-AU-WilliamNeural": "Australian male",
}


def get_voice_for_id(elevenlabs_id: str) -> str:
    """Map ElevenLabs voice ID to Edge TTS voice name."""
    return VOICE_MAPPING.get(elevenlabs_id, "en-US-AriaNeural")


async def list_voices() -> list[dict]:
    """List all available Edge TTS voices."""
    voices = await edge_tts.list_voices()
    return voices

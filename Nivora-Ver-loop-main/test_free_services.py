"""
Test script for FREE TTS/STT services
-------------------------------------
Run this to verify Edge TTS and Groq Whisper are working correctly.
"""

import asyncio
import os
import sys

async def test_edge_tts():
    """Test Edge TTS synthesis."""
    print("\n=== Testing Edge TTS ===")
    try:
        import edge_tts_plugin

        # Create TTS instance
        tts = edge_tts_plugin.TTS(voice="en-US-AriaNeural")
        print(f"OK - TTS created: model={tts.model}, voice=en-US-AriaNeural")
        print(f"     sample_rate={tts.sample_rate}, num_channels={tts.num_channels}")

        # Test synthesis
        print("Testing synthesis...")
        stream = tts.synthesize("Hello, this is a test of the Edge TTS system.")

        audio_chunks = []
        async for chunk in stream:
            audio_chunks.append(chunk)

        if audio_chunks:
            print(f"OK - Synthesis successful! Generated {len(audio_chunks)} audio chunks")
            total_duration = sum(c.frame.duration for c in audio_chunks)
            print(f"     Total audio duration: {total_duration:.2f} seconds")
        else:
            print("WARN - No audio chunks generated")

        return True

    except Exception as e:
        print(f"FAIL - Edge TTS error: {e}")
        return False


async def test_groq_stt():
    """Test Groq Whisper STT (requires GROQ_API_KEY)."""
    print("\n=== Testing Groq Whisper STT ===")

    groq_key = os.getenv("GROQ_API_KEY", "").strip()
    if not groq_key:
        print("SKIP - GROQ_API_KEY not set")
        print("       Get a free API key at: https://console.groq.com")
        return None

    try:
        from livekit.plugins import openai

        stt = openai.STT.with_groq(
            model="whisper-large-v3-turbo",
            language="en",
        )
        print(f"OK - Groq STT created: model={stt.model}")
        print("     (Full STT test requires audio input)")
        return True

    except Exception as e:
        print(f"FAIL - Groq STT error: {e}")
        return False


def test_voice_mapping():
    """Test voice ID to Edge TTS voice mapping."""
    print("\n=== Testing Voice Mapping ===")
    try:
        import edge_tts_plugin

        # Test mapping
        infin_voice = edge_tts_plugin.get_voice_for_id("iP95p4xoKVk53GoZ742B")
        nivora_voice = edge_tts_plugin.get_voice_for_id("cgSgspJ2msm6clMCkdW9")
        unknown_voice = edge_tts_plugin.get_voice_for_id("unknown-id")

        print(f"OK - Infin (Jarvis) voice: {infin_voice}")
        print(f"OK - Nivora voice: {nivora_voice}")
        print(f"OK - Unknown ID fallback: {unknown_voice}")

        return True

    except Exception as e:
        print(f"FAIL - Voice mapping error: {e}")
        return False


def test_available_voices():
    """List available Edge TTS voices."""
    print("\n=== Available Edge TTS Voices ===")
    try:
        import edge_tts_plugin

        print("English voices recommended for Nivora:")
        for voice, description in edge_tts_plugin.AVAILABLE_VOICES.items():
            print(f"  - {voice}: {description}")

        return True

    except Exception as e:
        print(f"FAIL - Error listing voices: {e}")
        return False


async def main():
    print("=" * 60)
    print("FREE TTS/STT Services Test")
    print("=" * 60)

    results = {}

    # Test Edge TTS
    results['edge_tts'] = await test_edge_tts()

    # Test Groq STT
    results['groq_stt'] = await test_groq_stt()

    # Test voice mapping
    results['voice_mapping'] = test_voice_mapping()

    # List available voices
    results['list_voices'] = test_available_voices()

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)

    all_ok = True
    for test, result in results.items():
        if result is None:
            status = "SKIPPED"
        elif result:
            status = "PASSED"
        else:
            status = "FAILED"
            all_ok = False
        print(f"  {test}: {status}")

    if all_ok:
        print("\nAll tests passed! Your FREE TTS/STT setup is ready.")
    else:
        print("\nSome tests failed. Check the output above for details.")

    return all_ok


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)

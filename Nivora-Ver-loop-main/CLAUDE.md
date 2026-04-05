# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Nivora** is a sophisticated multi-agent voice assistant powered by LiveKit, AWS Bedrock (Nova Pro), and **FREE** TTS/STT services. It features two distinct AI personas that can seamlessly transfer conversations between each other with automatic voice switching and real-time screen share vision capabilities.

### FREE Services Used
- **TTS**: Edge TTS (Microsoft Neural Voices) - No API key needed!
- **STT**: OpenAI Whisper via Groq - Free tier available with GROQ_API_KEY

### The Two Personas

1. **Infin (Jarvis)** - Life management assistant (default agent)
   - Voice: `en-US-AriaNeural` (Professional, natural female voice)
   - Handles: Email, calendar, notes, reminders, Google Sheets
   - Greeting: "How may I assist you today?"

2. **Nivora** - Technical/study companion
   - Voice: `en-US-GuyNeural` (Calm, friendly male voice)
   - Handles: Coding, debugging, research, Spotify/YouTube control
   - Greeting: "I'm here. What are we looking at?"

## Key Architecture Concepts

### Multi-Agent Transfer System

The system uses **explicit agent transfers** (not keyword-based switching). Each agent has a `@function_tool` that the LLM can call to transfer to the other agent:

- `InfinAgent` has `call_nivora_agent(topic: str)` - transfers to Nivora for technical topics
- `NivoraAgent` has `call_infin_agent()` - transfers back to Infin for life management

**Critical**: Transfers preserve full `ChatContext` and trigger automatic voice switching via `await agent.switch_voice()`.

### Voice Switching Mechanism

Voice switching happens at the `GenericAgent` level using Edge TTS:
1. Each agent class stores a `voice_id` attribute (mapped to Edge TTS voice names)
2. On transfer, `switch_voice()` creates a new `edge_tts_plugin.TTS` instance with the target voice
3. Updates `session._tts` to use the new voice
4. Session reference is stored via `GenericAgent.set_session(session)` in entrypoint

**Voice Mapping**:
- Infin: `en-US-AriaNeural` (professional female)
- Nivora: `en-US-GuyNeural` (calm male)

### Screen Share Vision

The system can analyze shared screens using AWS Nova Pro vision:
1. `screen_share.py` - Buffers the latest video frame from LiveKit screen share tracks
2. `start_frame_capture(track)` - Auto-triggered when user shares screen
3. `describe_screen_share` tool - Both agents can use this to analyze the latest frame
4. `computer_use.py` - Backend that sends frames to AWS Bedrock Nova vision API

Setup happens in entrypoint via `_setup_screen_share_tracking()` which registers LiveKit room event handlers.

## Common Commands

### Running the Agent

**Production (Multi-Agent with Transfers):**
```bash
python multi_agent_livekit.py
```

**Single Agent (Simple):**
```bash
python agent.py dev
```

**Legacy Multi-Agent (Keyword-based):**
```bash
python multi_agent.py
```

### Testing

No formal test suite exists. Testing is done by:
1. Running the agent and connecting via LiveKit client
2. Sharing screen to test vision capabilities
3. Triggering transfers by asking technical/life management questions

### Environment Setup

```bash
# Create and activate virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Unix

# Install dependencies
pip install -r requirements.txt
```

## Required Environment Variables

All secrets are stored in `.env` (not committed to repo):

```env
# AWS Credentials (required for LLM)
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_REGION=us-east-1
AWS_BEDROCK_MODEL=amazon.nova-pro-v1:0

# LiveKit (required)
LIVEKIT_URL=wss://your-project.livekit.cloud
LIVEKIT_API_KEY=
LIVEKIT_API_SECRET=

# FREE STT: Groq Whisper (required - get free key at console.groq.com)
GROQ_API_KEY=

# NOTE: ElevenLabs is NO LONGER required! Using FREE Edge TTS instead.
# ELEVENLABS_API_KEY= (not needed)

# AWS Services
AWS_S3_BUCKET=nivora-bucket
AWS_DYNAMODB_TABLE=nivora_habits
AWS_SES_SENDER_EMAIL=you@example.com
AWS_POLLY_VOICE=Matthew

# n8n MCP Server (optional - for extended tools)
N8N_MCP_URL=http://localhost:5678/webhook/mcp
N8N_BEARER_TOKEN=

# Spotify (optional)
SPOTIFY_CLIENT_ID=
SPOTIFY_CLIENT_SECRET=
SPOTIFY_REFRESH_TOKEN=

# Email (optional)
EMAIL_USER=
EMAIL_PASS=

# Google Services (optional)
GOOGLE_APPLICATION_CREDENTIALS=gcp-credentials.json
```

## File Structure & Responsibilities

### Core Agent Files

- **`multi_agent_livekit.py`** - Production entrypoint with explicit transfers (RECOMMENDED)
- **`agent.py`** - Simple single-agent implementation
- **`multi_agent.py`** - Legacy keyword-based switching (deprecated)
- **`generic_agent.py`** - Base class for all agents with voice switching and transfer logic
- **`edge_tts_plugin.py`** - Custom Edge TTS adapter for LiveKit (FREE TTS!)
- **`prompts.py`** - Nivora personality and instructions
- **`infin_prompts.py`** - Infin (Jarvis) personality and instructions

### Tool & Integration Files

- **`tools.py`** - 20+ function tools (email, calendar, Spotify, web search, notes, etc.)
- **`screen_share.py`** - Frame buffer for LiveKit screen share tracks
- **`computer_use.py`** - AWS Nova Pro vision backend for screen analysis
- **`spotify_api.py`** - Spotify Web API client
- **`spotify_control.py`** - Windows-native Spotify control (no API required)

### Configuration Files

- **`config.py`** - Loads all config from .env (n8n, LiveKit, GitHub, etc.)
- **`aws_config.py`** - Centralized AWS boto3 client factory
- **`bridge.py`** - MCP bridge utilities
- **`spotify_tool.py`** - Spotify MCP tool wrapper
- **`github_tool.py`** - GitHub MCP tool wrapper

### Utility Scripts

- **`get_spotify_token.py`** - One-time OAuth flow to get Spotify refresh token
- **`run_checks.py`** - Basic health checks
- **`validate_tools.py`** - Tool validation helper
- Individual Spotify control scripts (`play_track.py`, `next_track.py`, etc.)

## Critical Implementation Details

### Agent Transfer Pattern

When implementing transfers, follow this exact pattern:

```python
@function_tool
async def call_other_agent(self, topic: str = ""):
    """Transfer to other agent."""
    other_agent = OtherAgent(
        chat_ctx=self.chat_ctx,  # MUST pass context
        entry_topic=topic         # Optional: what triggered transfer
    )
    await other_agent.switch_voice()  # MUST call before return
    return other_agent, f"Transferring you to {other_agent.agent_name}..."
```

### Thinking Tag Filtering

Nova Pro sometimes outputs `<thinking>` tags which break TTS. `GenericAgent.generate_reply()` automatically strips these using `strip_thinking_tags()`. This is a safeguard since agents are instructed not to use these tags.

### Screen Share Setup

Screen share tracking must be registered BEFORE starting the session:

```python
await ctx.connect()  # Connect first
await _setup_screen_share_tracking(ctx)  # Setup handlers
# Then start session
```

The handlers listen for `track_subscribed` events and auto-start frame capture for screen share tracks.

### AWS Nova Vision Format

When calling AWS Bedrock Nova for vision:
- Image must be base64 encoded
- Format: PNG/JPEG
- Message structure: `messages[0].content = [{"image": {...}}, {"text": prompt}]`
- Response path: `output.message.content[0].text`
- Always strip markdown code fences from JSON responses

### Tool Registration

Tools are registered at agent initialization:
- Each agent class has a `tools` attribute (list of function_tool decorated functions)
- The agent can dynamically filter which tools to expose
- MCP tools are separate and configured via `mcp_servers` parameter

## Common Development Patterns

### Adding a New Tool

1. Add function in `tools.py` with `@function_tool()` decorator
2. Add tool to appropriate agent's tool list in `multi_agent_livekit.py`:
   - `AgentConfig.NIVORA_TOOLS` for technical tools
   - `AgentConfig.INFIN_TOOLS` for life management tools
3. Update agent instructions if tool requires specific guidance

### Changing Agent Personality

1. Edit `prompts.py` (Nivora) or `infin_prompts.py` (Infin)
2. Modify the `build_agent_instruction()` function
3. Adjust temperature in agent's LLM config (currently 0.7 for both)

### Modifying Transfer Logic

1. Edit transfer instructions in agent's `__init__` method
2. Adjust examples of what triggers transfers
3. Test by running agent and attempting various queries

### Adding New AWS Services

1. Add client factory in `aws_config.py` with `@lru_cache` decorator
2. Add environment variable handling
3. Create tool in `tools.py` that uses the new client
4. Update README.md with new env var requirements

## Important Notes

- **Windows-focused**: Many scripts use Windows-specific APIs (pycaw, winsdk) for media control
- **LiveKit session constraint**: Only one AgentSession per room - multi-agent uses single session with runtime persona switching
- **Context preservation**: ChatContext is passed between agents to maintain conversation history
- **Voice Names**: Edge TTS uses voice names like `en-US-AriaNeural` (see `edge_tts_plugin.py` for available voices)
- **MCP optional**: System works without n8n MCP server, it's for extended integrations
- **Screen share format**: LiveKit provides RGBA frames, converted to RGB PIL Images for vision API
- **FREE Services**: Edge TTS (no API key) + Groq Whisper (free tier with GROQ_API_KEY)

## Documentation Files

- **ARCHITECTURE.md** - Detailed system architecture with ASCII diagrams
- **COMPLETE_SUMMARY.md** - Comprehensive feature overview
- **TRANSFER_MECHANISM.md** - Deep dive on agent transfer implementation
- **SCREEN_SHARE_GUIDE.md** - Complete screen share documentation
- **MULTI_AGENT.md** - Original keyword-based approach documentation
- **README.md** - Basic setup and AWS services guide
- **README_MULTI_AGENT.md** - Multi-agent system overview

## Troubleshooting Common Issues

### Voice doesn't change on transfer
- Verify `GenericAgent.set_session(session)` is called in entrypoint
- Check `await agent.switch_voice()` is called before returning from transfer tool
- Confirm Edge TTS is properly installed (`pip install edge-tts`)

### TTS not working
- Edge TTS requires internet connection (uses Microsoft Edge's TTS API)
- Check console for any SSL/connection errors
- Try testing Edge TTS manually: `edge-tts --text "Hello" --write-media test.mp3`

### STT not working
- Verify GROQ_API_KEY is set in .env
- Check Groq API limits (free tier has rate limits)
- Alternative: Use `openai.STT(model="whisper-1")` with OPENAI_API_KEY

### Screen share not working
- Check that `_setup_screen_share_tracking()` is called after `ctx.connect()`
- Verify user has started screen share from LiveKit client
- Look for "Screen share detected" log messages

### AWS Bedrock errors
- Verify Nova Pro model is enabled in Bedrock console for your region
- Check IAM credentials have `bedrock:InvokeModel` permission
- Ensure `AWS_BEDROCK_MODEL=amazon.nova-pro-v1:0` in .env

### Transfers not happening
- Check agent instructions include clear transfer examples
- Verify function_tool is properly decorated
- Look for "transferring" in logs to confirm LLM is calling the tool

### TTS speaking thinking tags
- This should be auto-filtered by `GenericAgent.generate_reply()`
- If still happening, check if using GenericAgent base class
- Add more explicit "no thinking tags" to agent instructions

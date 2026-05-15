# Nivora Multi-Agent System 🤖

**Voice-powered AI assistant with dual personas, automatic agent transfers, and real-time screen share vision.**

[![LiveKit](https://img.shields.io/badge/LiveKit-Enabled-blue)](https://livekit.io)
[![AWS Bedrock](https://img.shields.io/badge/AWS-Nova%20Pro-orange)](https://aws.amazon.com/bedrock/)
[![ElevenLabs](https://img.shields.io/badge/ElevenLabs-Voice-green)](https://elevenlabs.io)

---

## 🎯 What Is This?

A sophisticated **multi-agent voice assistant** that seamlessly switches between two AI personas:

- **Infin (Jarvis)** - Your polished life management assistant
- **Nivora** - Your calm technical companion

Both agents can **see your screen** using AWS Nova Pro vision AI and **transfer conversations** to each other with automatic voice switching!

---

## ✨ Key Features

🎭 **Dual AI Personas**
- Infin handles email, calendar, notes, reminders
- Nivora handles coding, debugging, research, learning

🔄 **Intelligent Agent Transfers**
- LLM automatically detects when to switch agents
- Smooth handoffs with voice changes
- Full conversation context preserved

👁️ **Screen Share Vision**
- Both agents can see and analyze your shared screen
- Perfect for debugging code errors, reading documents
- Powered by AWS Nova Pro vision API

🎵 **Dynamic Voice Switching**
- Infin uses polished professional voice
- Nivora uses calm intellectual voice
- Voices change automatically on transfer

💬 **Natural Conversation**
- Maintains full chat history across transfers
- Agents remember previous context
- Seamless multi-turn interactions

---

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

Create `.env` with:

```env
# AWS Bedrock (for LLM and Vision)
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret
AWS_BEDROCK_MODEL=amazon.nova-pro-v1:0

# LiveKit
LIVEKIT_URL=wss://your-livekit-url
LIVEKIT_API_KEY=your_key
LIVEKIT_API_SECRET=your_secret

# ElevenLabs (for TTS)
ELEVENLABS_API_KEY=your_key

# Optional: n8n MCP Server
N8N_MCP_URL=http://localhost:5678/webhook/mcp
N8N_BEARER_TOKEN=your_token
```

### 3. Run the Multi-Agent System

```bash
python multi_agent_livekit.py
```

### 4. Connect & Test

Join the LiveKit room from your client and try:

```
You: "Check my calendar for tomorrow"
Infin: "You have 3 meetings scheduled..."

You: "Now help me debug this Python error"
Infin: "Transferring you to Nivora for debug Python error"
Nivora: "I'm here. Let me look at that error..."

You: [Share screen with VSCode]
Nivora: "I see a NameError on line 47..."
```

---

## 📁 Project Structure

### Core Files

```
multi_agent_livekit.py      # 🎯 Main entrypoint (NEW - LiveKit pattern)
generic_agent.py            # 🔧 Base agent class with voice switching
agent.py                    # Original single-agent implementation
multi_agent.py              # Original keyword-based switching

screen_share.py             # 📺 Frame buffer for screen sharing
tools.py                    # 🛠️ Agent tools (email, calendar, Spotify, etc)
computer_use.py             # 👁️ AWS Nova vision backend
prompts.py                  # 📝 Nivora personality & instructions
infin_prompts.py            # 📝 Infin (Jarvis) personality & instructions
```

### Documentation

```
COMPLETE_SUMMARY.md         # 📚 Everything in one place
TRANSFER_MECHANISM.md       # 🔄 How agent transfers work
SCREEN_SHARE_GUIDE.md       # 👁️ Screen share deep dive
SCREEN_SHARE_QUICKSTART.md  # 🚀 Quick testing guide
ARCHITECTURE.md             # 🏗️ System architecture diagrams
MULTI_AGENT.md              # Original multi-agent docs
```

---

## 🎭 The Two Personas

### Infin (Jarvis) - Life Management

**Default agent, starts first**

- **Voice:** Professional, polished, elegantly witty
- **Tools:** Email, Calendar, Notes, Sheets, Reminders
- **Best for:** Productivity, scheduling, organization
- **Greeting:** "How may I assist you today?"

**Example use cases:**
- "Check my email"
- "What meetings do I have tomorrow?"
- "Set a reminder for 3 PM"
- "Take a note about this idea"

### Nivora - Technical Companion

**Transfers from Infin for technical topics**

- **Voice:** Calm, intellectual, darkly witty
- **Tools:** Spotify, YouTube, Web Search, System Control
- **Best for:** Coding, debugging, research, learning
- **Greeting:** "I'm here. What are we looking at?"

**Example use cases:**
- "Debug this Python error"
- "Explain how neural networks work"
- "Help me understand this code"
- "Research React best practices"

---

## 🔄 How Transfers Work

### Automatic LLM-Driven Transfers

The agents use **function tools** to transfer conversations:

```python
# Infin detects technical topic
@function_tool
async def call_nivora_agent(topic: str):
    nivora = NivoraAgent(chat_ctx=self.chat_ctx, entry_topic=topic)
    await nivora.switch_voice()  # Voice changes here!
    return nivora, f"Transferring you to Nivora for {topic}"

# Nivora detects life management topic
@function_tool
async def call_infin_agent():
    infin = InfinAgent(chat_ctx=self.chat_ctx, returning=True)
    await infin.switch_voice()
    return infin, "Transferring you back to Infin"
```

### What Triggers a Transfer?

**To Nivora (Technical):**
- Keywords: code, debug, explain, how does, learn, error, fix
- Examples: "Debug this", "Explain Docker", "Help me code"

**To Infin (Life Management):**
- Keywords: email, calendar, reminder, meeting, note, schedule
- Examples: "Check email", "Set reminder", "What meetings"

**The LLM decides intelligently** - not just keyword matching!

---

## 👁️ Screen Share Vision

### How It Works

1. **User shares screen** from LiveKit client
2. **System automatically detects** screen share track
3. **Frames captured** in real-time (30 FPS)
4. **Latest frame stored** in buffer
5. **Agent analyzes** using `describe_screen_share` tool
6. **AWS Nova Pro vision** returns description

### Use Cases

**Debugging (Nivora):**
```
User: [Shares VSCode with error]
You: "What's this error?"
Nivora: [Uses vision] "I see a NameError on line 47: 
        'database_url' is not defined..."
```

**Calendar Review (Infin):**
```
User: [Shares Google Calendar]
You: "What's on my calendar tomorrow?"
Infin: [Uses vision] "You have meetings at 10 AM, 2 PM, and 4 PM"
```

**Code Review (Nivora):**
```
User: [Shares React component]
You: "Review this component"
Nivora: [Uses vision] "This component uses useState correctly,
        but you're missing useEffect cleanup..."
```

---

## 🛠️ Technology Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **LLM** | AWS Bedrock Nova Pro | Reasoning & function calling |
| **Vision** | AWS Bedrock Nova Pro | Screen share analysis |
| **STT** | Sarvam (saaras:v3) | Speech-to-text (Indian English) |
| **TTS** | ElevenLabs | Voice synthesis (2 voices) |
| **VAD** | Silero | Voice activity detection |
| **Framework** | LiveKit Agents | Real-time voice infrastructure |
| **MCP** | n8n (optional) | Extended tool integrations |

---

## 📊 Architecture Overview

```
User (LiveKit Client)
     ↓
┌────────────────────────────┐
│   LiveKit Room             │
│  ┌──────────────────────┐  │
│  │  AgentSession        │  │
│  │  ┌────────────────┐  │  │
│  │  │ InfinAgent     │  │  │
│  │  │ (Default)      │  │  │
│  │  │ Voice: Infin   │  │  │
│  │  │ Tools: Email+  │  │  │
│  │  └────────┬───────┘  │  │
│  │           │ Transfer │  │
│  │  ┌────────▼───────┐  │  │
│  │  │ NivoraAgent    │  │  │
│  │  │ Voice: Nivora  │  │  │
│  │  │ Tools: Code+   │  │  │
│  │  └────────────────┘  │  │
│  └──────────────────────┘  │
└────────────────────────────┘
         ↓           ↓
   AWS Bedrock   Screen Share
   (LLM+Vision)  Frame Buffer
```

See [ARCHITECTURE.md](ARCHITECTURE.md) for detailed diagrams.

---

## 📚 Documentation

| Document | Description |
|----------|-------------|
| [COMPLETE_SUMMARY.md](COMPLETE_SUMMARY.md) | Everything you need to know |
| [TRANSFER_MECHANISM.md](TRANSFER_MECHANISM.md) | Deep dive on agent transfers |
| [SCREEN_SHARE_GUIDE.md](SCREEN_SHARE_GUIDE.md) | Complete screen share docs |
| [SCREEN_SHARE_QUICKSTART.md](SCREEN_SHARE_QUICKSTART.md) | Quick testing guide |
| [ARCHITECTURE.md](ARCHITECTURE.md) | System architecture & diagrams |
| [MULTI_AGENT.md](MULTI_AGENT.md) | Original keyword-based approach |

---

## 🎯 Comparison: Old vs New

| Feature | `multi_agent.py` (Old) | `multi_agent_livekit.py` (New) |
|---------|------------------------|--------------------------------|
| **Pattern** | Keyword-based switching | Explicit agent transfers |
| **Transfer** | Automatic (keywords) | LLM function call |
| **Voice** | Manual switch | Automatic on transfer |
| **Screen Share** | ❌ Not integrated | ✅ Automatic tracking |
| **Clarity** | Silent switch | "Transferring to..." |
| **Context** | Preserved | Preserved + entry_topic |

**Recommendation:** Use `multi_agent_livekit.py` (LiveKit pattern) for production.

---

## 🧪 Testing

### Basic Test
```bash
python multi_agent_livekit.py
# Join room, say: "Check my calendar"
```

### Transfer Test
```
You: "Check my calendar"
Infin: "You have 3 meetings..."
You: "Now explain how Docker works"
Infin: "Transferring you to Nivora..."
Nivora: "Docker is a containerization platform..."
```

### Screen Share Test
```
[Share VSCode with code error]
You: "What error do you see?"
Nivora: "I see a NameError on line 47..."
```

---

## 🐛 Troubleshooting

### Voice doesn't change on transfer
- Check `GenericAgent.set_session(session)` is called
- Verify `await agent.switch_voice()` before returning

### Screen share not working
- Start screen share from LiveKit client
- Check logs for "Screen share detected"
- Test with `get_latest_frame()` in console

### Transfers don't happen
- Check agent instructions include transfer examples
- LLM might not recognize trigger - add clearer phrases

See [COMPLETE_SUMMARY.md](COMPLETE_SUMMARY.md) for more troubleshooting.

---

## 🎉 Features Summary

✅ **Dual AI personas** (Infin & Nivora)
✅ **Intelligent agent transfers** (LLM-driven)
✅ **Automatic voice switching** (seamless)
✅ **Real-time screen share vision** (AWS Nova Pro)
✅ **Full context preservation** (chat history maintained)
✅ **Production-ready** (built on LiveKit best practices)

---

## 📝 License

MIT License - See LICENSE file for details

---

## 🙏 Credits

- Built on [LiveKit Agents SDK](https://github.com/livekit/agents)
- Powered by [AWS Bedrock Nova](https://aws.amazon.com/bedrock/)
- Voice by [ElevenLabs](https://elevenlabs.io)
- Inspired by LiveKit's multi-agent examples

---

**Ready to go? Run `python multi_agent_livekit.py` and start talking!** 🚀

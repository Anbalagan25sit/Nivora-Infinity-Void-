# Nivora Multi-Agent + Screen Share - Complete Summary

## 🎯 What You Now Have

A **LiveKit-powered multi-agent voice assistant** with:

1. ✅ **Two distinct AI personas** (Infin & Nivora)
2. ✅ **Explicit agent transfers** (LLM-driven handoffs)
3. ✅ **Automatic voice switching** (different ElevenLabs voices)
4. ✅ **Real-time screen share analysis** (AWS Nova Pro vision)
5. ✅ **Full context preservation** (chat history flows through transfers)

---

## 📁 File Structure

```
multi_agent_livekit.py      # Main entrypoint with screen share tracking
generic_agent.py            # Base class with voice switching & shared tools
screen_share.py             # Frame buffer (already existed)
tools.py                    # describe_screen_share tool (already existed)
computer_use.py             # AWS Nova vision backend (already existed)

TRANSFER_MECHANISM.md       # Deep dive on agent transfers
SCREEN_SHARE_GUIDE.md       # Complete screen share documentation
SCREEN_SHARE_QUICKSTART.md  # Quick testing guide
```

---

## 🎭 Agent Comparison

| Feature | **Infin (Jarvis)** | **Nivora** |
|---------|-------------------|-----------|
| **Role** | Life management | Technical/study |
| **Voice** | `iP95p4xoKVk53GoZ742B` | `cgSgspJ2msm6clMCkdW9` |
| **Tone** | Polished, professional | Calm, witty, intellectual |
| **Tools** | Email, calendar, notes, sheets | Spotify, YouTube, web search |
| **Screen Share Use** | Calendar, documents, general | Code debugging, error analysis |
| **Transfer To** | Nivora (technical topics) | Infin (life management) |
| **Default** | ✅ Starts first | Transfers from Infin |

---

## 🔄 Transfer Flow

```
User joins room
     ↓
Infin greets: "How may I assist you today?"
     ↓
User: "Check my calendar"
     ↓
Infin: [Uses google_calendar_list or screen share]
       "You have 3 meetings tomorrow"
     ↓
User: "Now help me debug this Python error"
     ↓
Infin: [Detects technical topic]
       [Calls call_nivora_agent(topic="debug Python error")]
     ↓
System: [Creates NivoraAgent]
        [Switches voice to Nivora]
        [Says: "Transferring you to Nivora"]
     ↓
Nivora: [Receives entry_topic + full chat history]
        "I'm here. Let me look at that error."
        [Uses describe_screen_share if screen shared]
        "I see a NameError on line 47..."
     ↓
User: "Thanks! Send an email about this fix"
     ↓
Nivora: [Detects life management topic]
        [Calls call_infin_agent()]
     ↓
System: [Creates InfinAgent with returning=True]
        [Switches voice back to Infin]
        [Says: "Transferring back to Infin"]
     ↓
Infin: "Welcome back. I'll send that email now."
       [Uses send_email tool]
```

---

## 🎥 Screen Share Integration

### How It Works

```python
# 1. Room monitors for screen share tracks
@ctx.room.on("track_subscribed")
def on_track_subscribed(track, publication, participant):
    if track.source == rtc.TrackSource.SOURCE_SCREEN_SHARE:
        asyncio.create_task(start_frame_capture(track))

# 2. Frame capture runs in background
async def start_frame_capture(track):
    async for event in video_stream:
        frame = event.frame
        img = Image.frombytes("RGBA", (width, height), frame.data)
        set_latest_frame(img.convert("RGB"))

# 3. Agent uses vision tool
@function_tool
async def describe_screen_share(question: str) -> str:
    img = get_latest_frame()
    result = analyze_screen(question, img)  # AWS Nova Pro
    return result["description"]
```

### Capabilities

Both agents can:
- ✅ See what's on your shared screen
- ✅ Read text, code, error messages
- ✅ Analyze UI, documents, calendars
- ✅ Answer questions about visible content

**Nivora** is especially good at:
- 🐛 Debugging code errors
- 📝 Analyzing code structure
- ⚠️ Reading stack traces
- 🏗️ Reviewing architecture diagrams

**Infin** is especially good at:
- 📅 Reading calendars
- 📧 Analyzing email interfaces
- 📊 Reading spreadsheets
- 📄 Scanning documents

---

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

Ensure `.env` has:
```env
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret
AWS_BEDROCK_MODEL=amazon.nova-pro-v1:0
LIVEKIT_URL=wss://your-livekit-url
LIVEKIT_API_KEY=your_key
LIVEKIT_API_SECRET=your_secret
```

### 3. Run the Agent

```bash
python multi_agent_livekit.py
```

### 4. Join from Client & Test

**Screen share test:**
```
You: [Start screen sharing VSCode with code]
You: "Nivora, what error do you see?"
Nivora: "I see a NameError on line 47..."
```

**Transfer test:**
```
You: "Check my calendar"
Infin: "You have 3 meetings..."
You: "Now explain how Docker works"
Infin: "Transferring you to Nivora for explain how Docker works"
Nivora: "Docker is a containerization platform..."
```

---

## 🎯 Key Innovations

### 1. LiveKit Transfer Pattern (vs Keyword Switching)

**Before:** Single agent with dynamic persona
```python
if "email" in user_input:
    switch_to_infin()
elif "code" in user_input:
    switch_to_nivora()
```

**After:** Explicit agent handoff
```python
@function_tool
async def call_nivora_agent(topic: str):
    nivora = NivoraAgent(chat_ctx=self.chat_ctx, entry_topic=topic)
    await nivora.switch_voice()
    return nivora, f"Transferring to Nivora for {topic}"
```

**Benefits:**
- ✅ LLM decides when to transfer (smarter than keywords)
- ✅ Clear handoff messages
- ✅ Automatic voice switching
- ✅ Entry topic awareness

### 2. Session-Aware Voice Switching

```python
class GenericAgent(Agent):
    _session_ref = None  # Class-level session
    
    async def switch_voice(self):
        new_tts = elevenlabs.TTS(voice_id=self.voice_id)
        self._session_ref._tts = new_tts  # Runtime replacement
```

**Why it works:**
- Session TTS updated before new agent speaks
- No audio gap or wrong voice
- Seamless transition

### 3. Automatic Screen Share Tracking

```python
@ctx.room.on("track_subscribed")
def on_track_subscribed(track, publication, participant):
    if track.source == rtc.TrackSource.SOURCE_SCREEN_SHARE:
        asyncio.create_task(start_frame_capture(track))
```

**Why it works:**
- Zero configuration needed
- Works across agent transfers
- Latest frame always available
- Low memory (single frame buffer)

---

## 📊 Comparison Table

| Feature | Old (multi_agent.py) | New (multi_agent_livekit.py) |
|---------|---------------------|------------------------------|
| **Architecture** | Single agent with keyword switching | Multiple agents with explicit transfers |
| **Voice Switch** | Manual TTS recreation | Automatic on transfer |
| **Transfer Trigger** | Keyword detection | LLM function call |
| **Context** | Preserved | Preserved + entry_topic |
| **Clarity** | Silent switch | "Transferring to..." message |
| **Screen Share** | ❌ Not integrated | ✅ Automatic tracking |
| **User Control** | Passive | Active (LLM proposes transfer) |

---

## 🐛 Troubleshooting

### Voice doesn't change on transfer

**Check:**
```python
# In multi_agent_livekit.py
GenericAgent.set_session(session)  # Before session.start()

# In transfer function
await new_agent.switch_voice()  # Before returning agent
```

### Screen share not working

**Check logs for:**
```
Screen share detected from <user>. Starting frame capture.
```

**If not appearing:**
1. Verify screen share is started in client
2. Check track source is `SOURCE_SCREEN_SHARE`
3. Test with `get_latest_frame()` in Python console

### Transfer doesn't happen

**LLM might not recognize trigger. Add clearer instructions:**
```python
instructions = """
If user says ANY of these exact phrases, call call_nivora_agent:
- "debug"
- "code"
- "explain how"
- "help me learn"
"""
```

---

## 📚 Documentation

- `TRANSFER_MECHANISM.md` - How transfers work technically
- `SCREEN_SHARE_GUIDE.md` - Complete screen share docs
- `SCREEN_SHARE_QUICKSTART.md` - Quick testing guide
- `MULTI_AGENT.md` - Original keyword-based approach (for comparison)

---

## 🎯 Summary

You now have:

✅ **Infin** - Life management (default, polished voice)
✅ **Nivora** - Technical companion (calm, witty voice)
✅ **Seamless transfers** - Voice switches automatically
✅ **Screen share vision** - Both agents can see your screen
✅ **Context preservation** - Full conversation history maintained
✅ **Production-ready** - Built on LiveKit best practices

Run `python multi_agent_livekit.py` and say:
- "Check my calendar" → Infin responds
- "Now debug this code" → Transfers to Nivora
- "Look at my screen" → Uses vision AI

**It just works!** 🎉

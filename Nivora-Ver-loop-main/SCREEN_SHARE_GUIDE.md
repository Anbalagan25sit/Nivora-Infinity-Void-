# LiveKit Screen Share Integration Guide

## 🎯 Overview

Nivora/Infin now has **real-time screen share analysis** powered by AWS Nova Pro vision AI. Both agents can see and analyze what you share on your screen!

---

## 🚀 How It Works

### Architecture

```
User Shares Screen
       ↓
LiveKit Room Emits "track_subscribed" Event
       ↓
Screen Share Tracker Detects Video Track (SOURCE_SCREEN_SHARE)
       ↓
Frame Capture Task Starts (async loop)
       ↓
Latest Frame Stored in Buffer (screen_share.py)
       ↓
Agent Calls describe_screen_share Tool
       ↓
AWS Nova Pro Vision Analyzes Frame
       ↓
Agent Responds with Analysis
```

---

## 📋 Files Involved

### 1. `screen_share.py` - Frame Buffer Module
```python
# Stores the latest screen share frame
_latest_frame: Optional[Image.Image] = None

def set_latest_frame(img: Image.Image)  # Store frame
def get_latest_frame() -> Optional[Image.Image]  # Retrieve frame
async def start_frame_capture(track)  # Async capture loop
```

**What it does:**
- Receives video frames from LiveKit track
- Converts RGBA frames to RGB PIL Images
- Stores only the LATEST frame (not a buffer of frames)
- Runs asynchronously in background

### 2. `multi_agent_livekit.py` - Screen Share Tracking
```python
async def _setup_screen_share_tracking(ctx: JobContext):
    @ctx.room.on("track_subscribed")
    def on_track_subscribed(track, publication, participant):
        if track.source == rtc.TrackSource.SOURCE_SCREEN_SHARE:
            asyncio.create_task(start_frame_capture(track))
```

**What it does:**
- Monitors LiveKit room for new tracks
- Detects when a participant starts screen sharing
- Automatically starts frame capture
- Logs screen share start/stop events

### 3. `tools.py` - Vision Analysis Tool
```python
async def describe_screen_share(
    context: RunContext,
    question: str = "Describe what you see on the shared screen in detail."
) -> str:
    img = get_latest_frame()
    result = analyze_screen(question, img)
    return result["description"]
```

**What it does:**
- Retrieves latest frame from buffer
- Sends to AWS Nova Pro with user's question
- Returns natural language description

### 4. `computer_use.py` - Vision Backend
```python
def analyze_screen_aws(prompt: str, img: Image.Image) -> dict:
    # Send to AWS Bedrock Nova Pro
    # Returns JSON with "description" key
```

**What it does:**
- Converts image to base64
- Calls AWS Bedrock Nova Pro vision API
- Parses JSON response

---

## 🎬 Usage Examples

### Example 1: Debugging Code Errors

```
User: [Shares screen showing VSCode with Python error]
User: "Nivora, look at this error"

Nivora: [Calls describe_screen_share("What error message is shown?")]
        "I see a NameError on line 47: 'database_url' is not defined.
        You're missing the import for your config module."
```

### Example 2: Calendar Review

```
User: [Shares screen showing Google Calendar]
User: "Infin, what meetings do I have tomorrow?"

Infin: [Calls describe_screen_share("What events are on the calendar for tomorrow?")]
       "Tomorrow you have three meetings: Design review at 10 AM,
       Team standup at 2 PM, and Client call at 4 PM."
```

### Example 3: Code Review

```
User: [Shares screen showing React component]
User: "Nivora, review this component structure"

Nivora: [Calls describe_screen_share("Analyze this React component code")]
        "This component is using useState for local state. I notice
        you're missing useEffect cleanup for the event listener,
        which could cause memory leaks."
```

### Example 4: Reading Documentation

```
User: [Shares screen showing research paper PDF]
User: "Nivora, what's the main point of this section?"

Nivora: [Calls describe_screen_share("Summarize the main points in this text")]
        "This section discusses transformer architectures. The key
        innovation is the self-attention mechanism that processes
        sequences in parallel rather than sequentially."
```

---

## 🔧 Technical Deep Dive

### Track Detection Logic

```python
if (track.kind == rtc.TrackKind.KIND_VIDEO and 
    track.source == rtc.TrackSource.SOURCE_SCREEN_SHARE):
    # This is a screen share track!
```

**Key Points:**
- Only captures **video** tracks (not audio)
- Only captures **screen share** source (not camera)
- Ignores camera tracks even if user has webcam on

### Frame Capture Loop

```python
async for event in video_stream:
    frame = event.frame
    img = Image.frombytes("RGBA", (frame.width, frame.height), bytes(frame.data))
    img = img.convert("RGB")
    set_latest_frame(img)
```

**Key Points:**
- Runs in async loop until track ends
- Converts each frame to PIL Image
- Overwrites previous frame (not stored in list)
- RGBA → RGB conversion (AWS Nova expects RGB)

### Why Only Latest Frame?

Instead of storing all frames:
```python
# ❌ Bad - memory intensive
_frame_buffer = []  # Could grow to thousands of frames

# ✅ Good - constant memory
_latest_frame = None  # Always just one frame
```

**Reasoning:**
- Screen share typically 30 FPS = 1800 frames/minute
- Storing all frames = massive memory usage
- Agent only needs current view, not history
- Latest frame is always most relevant

---

## 🎤 How Agents Use Screen Share

### Proactive Usage

Agents are instructed to **proactively offer** screen analysis:

**Infin's instructions:**
```
Use describe_screen_share when:
- User asks you to "look at my screen", "what do you see", "read this"
- User shares an error message, document, or interface they want help with
- User asks about something visible on their screen
```

**Nivora's instructions:**
```
This is EXTREMELY useful for:
- Debugging code errors (user shares IDE with error messages)
- Reading stack traces and error logs
- Analyzing UI/UX issues in applications
- When user shares screen, proactively offer to look at it
```

### Trigger Phrases

| User Says | Agent Action |
|-----------|--------------|
| "Look at this error" | Calls `describe_screen_share("What error is shown?")` |
| "What do you see?" | Calls `describe_screen_share("Describe in detail")` |
| "Read this for me" | Calls `describe_screen_share("What text is visible?")` |
| "Is this code correct?" | Calls `describe_screen_share("Analyze this code")` |
| "Help me with this" | Calls `describe_screen_share("What is the user looking at?")` |

---

## 🧠 Vision AI Prompting

### The Tool Function

```python
async def describe_screen_share(
    context: RunContext,
    question: str = "Describe what you see..."
) -> str
```

**The `question` parameter** is what the LLM sends to vision AI.

### Good vs Bad Questions

| ❌ Bad | ✅ Good |
|--------|---------|
| "Look at screen" | "What error message is displayed in the terminal?" |
| "See this?" | "Which files are open in the VSCode editor?" |
| "Help" | "Describe the structure of this React component code" |
| "What is this?" | "What appointment times are shown in this calendar?" |

### LLM's Prompting Strategy

The agent (Nova Pro LLM) generates the question to ask the vision AI (also Nova Pro):

```
User: "What's wrong with this code?"
  ↓
Agent LLM thinks: "User likely shared screen with code error"
  ↓
Agent calls: describe_screen_share(
    question="Identify any errors, warnings, or issues in the code visible on screen"
)
  ↓
Vision AI responds: "Line 47 has NameError: variable 'x' not defined"
  ↓
Agent says: "I see the issue - you're missing..."
```

---

## 🎯 Best Practices

### For Users

1. **Share the relevant window only** (not entire screen for privacy)
2. **Make text large enough** for vision AI to read clearly
3. **Keep screen static** while agent analyzes (don't scroll rapidly)
4. **Describe what you want** clearly:
   - ✅ "Look at this error message"
   - ❌ "Help me"

### For Developers

1. **Call describe_screen_share with specific questions**
2. **Handle "No frame" gracefully** - user might not be sharing yet
3. **Don't spam the tool** - vision API has rate limits
4. **Combine vision with context** - use chat history + screen analysis

---

## 🔒 Privacy & Security

### What Gets Captured

- ✅ Latest screen share frame only
- ✅ Stored in memory (not saved to disk)
- ✅ Automatically cleared when screen share stops

### What Doesn't Get Captured

- ❌ Webcam video (only screen share)
- ❌ Audio tracks
- ❌ Frame history (only current frame)
- ❌ Any data when user isn't sharing

### AWS Nova Pro Processing

- Images sent to AWS Bedrock (secure)
- Not stored permanently by AWS (ephemeral)
- Uses existing AWS credentials from `.env`
- Same security as text LLM calls

---

## 🐛 Troubleshooting

### "No screen-share frame received yet"

**Cause:** User hasn't started screen sharing
**Fix:** Start screen share from your LiveKit client

### Vision returns empty/wrong results

**Cause:** Frame quality too low or text too small
**Fix:** 
1. Share specific window (not full screen)
2. Zoom in or increase font size
3. Ensure good lighting if sharing physical documents

### Capture task crashes

**Cause:** Track ended unexpectedly
**Fix:** Normal - happens when user stops sharing. Tracker will restart on next share.

### High latency on vision calls

**Cause:** AWS Bedrock API response time
**Fix:** This is expected (1-3s). Consider caching repeated queries.

---

## 📊 Performance Metrics

| Metric | Value |
|--------|-------|
| Frame capture rate | ~30 FPS (LiveKit default) |
| Memory per frame | ~2-5 MB (depends on resolution) |
| Vision API latency | 1-3 seconds |
| Frame buffer size | 1 frame (constant memory) |

---

## 🔮 Advanced Features

### Custom Vision Prompts

Developers can create specialized tools:

```python
@function_tool
async def debug_screen_error() -> str:
    """Specialized tool for debugging visible errors"""
    img = get_latest_frame()
    if not img:
        return "No screen shared"
    
    prompt = """
    Analyze this screenshot for programming errors:
    1. Identify error messages and their line numbers
    2. Determine the error type (syntax, runtime, logic)
    3. Suggest the likely cause
    4. Recommend a fix
    
    Return JSON: {"error_type": "...", "line": "...", "fix": "..."}
    """
    result = analyze_screen(prompt, img)
    return result
```

### Multi-Frame Analysis

For comparing states:

```python
# Store previous frame manually
prev_frame = get_latest_frame()
await asyncio.sleep(2)  # Wait for change
curr_frame = get_latest_frame()

# Send both to vision AI
result = analyze_screen(
    "What changed between these two screenshots?",
    [prev_frame, curr_frame]
)
```

### OCR-Specific Analysis

```python
question = "Extract all visible text using OCR and return as plain text"
result = describe_screen_share(context, question)
# Result will be raw text from screen
```

---

## 🎯 Summary

LiveKit screen share integration provides:

- ✅ **Automatic detection** - no manual setup required
- ✅ **Real-time capture** - always latest frame available  
- ✅ **Vision AI analysis** - AWS Nova Pro understands screens
- ✅ **Low memory** - only stores current frame
- ✅ **Secure** - no persistent storage
- ✅ **Both agents** - Nivora & Infin can both see screens

Perfect for debugging, document reading, UI review, and visual assistance!

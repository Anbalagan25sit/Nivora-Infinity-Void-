# Quick Start: Testing Screen Share

## 🚀 Run the Agent

```bash
python multi_agent_livekit.py
```

You should see:
```
Multi-agent session started with Infin (Jarvis) as default agent.
Voice switching enabled - agents will change voice on transfer.
Screen share analysis ready - share your screen to enable vision tools.
```

---

## 🎬 Test Scenarios

### 1. Basic Screen Share Test

**Setup:**
1. Join the LiveKit room from your client
2. Start screen sharing (share a specific window)
3. Open a text editor or browser

**Test:**
```
You: "Infin, what do you see on my screen?"
Infin: [Calls describe_screen_share]
      "I see a text editor window with..."
```

### 2. Code Debugging Test (Nivora)

**Setup:**
1. Share VSCode or IDE with code that has an error
2. Make sure error message is visible

**Test:**
```
You: "Help me debug this Python error"
Infin: [Transfers to Nivora]
      "Transferring you to Nivora for debug Python error"

Nivora: "I'm here. Let me look at that error."
        [Calls describe_screen_share("What error is shown?")]
        "I see a NameError on line 47..."
```

### 3. Calendar Review Test (Infin)

**Setup:**
1. Share browser with Google Calendar open
2. Have some events visible

**Test:**
```
You: "Infin, what's on my calendar tomorrow?"
Infin: [Calls describe_screen_share("What events are on calendar for tomorrow?")]
       "Tomorrow you have meetings at..."
```

### 4. Transfer + Screen Share Test

**Setup:**
1. Share screen with calendar
2. Then switch to code with error

**Test:**
```
You: "Check my calendar"
Infin: [Uses screen share to read calendar]
       "You have 3 meetings..."

You: "Now help me debug this code"
Infin: [Transfers to Nivora]

Nivora: [Uses screen share to see code]
        "I see the error - you're missing..."
```

---

## 🔍 Debug Commands

### Check if screen share is detected

Look for this log:
```
Screen share detected from <participant>. Starting frame capture.
```

### Check if frame is captured

In Python console or tool:
```python
from screen_share import get_latest_frame
frame = get_latest_frame()
print(f"Frame available: {frame is not None}")
if frame:
    print(f"Frame size: {frame.size}")
```

### Test vision AI directly

```python
from screen_share import get_latest_frame
from computer_use import analyze_screen

frame = get_latest_frame()
result = analyze_screen("What do you see?", frame)
print(result)
```

---

## 📋 Expected Behavior

### When Working Correctly

1. **Screen share starts:** Log shows "Screen share detected"
2. **User asks about screen:** Agent calls `describe_screen_share`
3. **Vision analysis:** 1-3 second delay while AWS processes
4. **Agent responds:** Natural language description of screen

### Common Issues

| Issue | Cause | Fix |
|-------|-------|-----|
| "No screen-share frame" | User not sharing | Start screen share |
| Empty response | Text too small | Zoom in or share specific window |
| High latency | AWS API delay | Normal, wait 2-3 seconds |
| Wrong content | Stale frame | Wait a moment, frame updates at 30 FPS |

---

## 🎯 Quick Test Script

Save as `test_screen_share.py`:

```python
import asyncio
from screen_share import get_latest_frame
from computer_use import analyze_screen

async def test():
    print("Testing screen share...")
    
    # Get frame
    frame = get_latest_frame()
    if not frame:
        print("❌ No frame captured - is screen share active?")
        return
    
    print(f"✅ Frame captured: {frame.size}")
    
    # Test vision
    result = analyze_screen("What do you see on this screen?", frame)
    print(f"✅ Vision result: {result}")

if __name__ == "__main__":
    asyncio.run(test())
```

Run:
```bash
python test_screen_share.py
```

---

## 🎤 Voice Commands to Try

### General
- "Look at my screen"
- "What do you see?"
- "Describe what's on my screen"

### Specific
- "What error is showing?" (for debugging)
- "Read this document for me" (for papers/articles)
- "What's the title of this page?" (for web browsing)
- "What files are open?" (for IDE/file explorer)

### With Context
- "I'm seeing an error, can you help?" (agent will look)
- "Does this code look right?" (agent analyzes code)
- "What meetings do I have?" (while showing calendar)

---

## 🏆 Success Criteria

Screen share is working if:
- ✅ Logs show "Screen share detected"
- ✅ `get_latest_frame()` returns non-None image
- ✅ Agent responds to "what do you see" with accurate description
- ✅ Vision analysis completes in 1-3 seconds
- ✅ Transfers work while screen sharing (context preserved)

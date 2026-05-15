# Quick Reference Card - Nivora Multi-Agent

## 🚀 Start Command
```bash
python multi_agent_livekit.py
```

---

## 🎭 Which Agent Does What?

### Infin (Jarvis) - Default
| Action | Voice Command |
|--------|---------------|
| Check email | "Check my email" |
| Calendar | "What meetings do I have?" |
| Set reminder | "Remind me at 3 PM to..." |
| Take note | "Take a note about..." |
| Weather | "What's the weather?" |
| Screen share | "Look at my calendar" |

### Nivora - Technical
| Action | Voice Command |
|--------|---------------|
| Debug code | "Help me debug this error" |
| Explain concept | "Explain how Docker works" |
| Code review | "Review this React component" |
| Learn topic | "Teach me about neural networks" |
| Play music | "Play Spotify" |
| Screen share | "Look at this error message" |

---

## 🔄 Transfer Commands

| From | To | Trigger Phrases |
|------|----| ---------------|
| Infin → Nivora | Technical | "debug", "code", "explain how", "learn", "error" |
| Nivora → Infin | Life | "email", "calendar", "reminder", "meeting", "note" |

---

## 👁️ Screen Share Commands

### Start Screen Share First (from LiveKit client)

| Situation | Command | Agent |
|-----------|---------|-------|
| Code error visible | "What error do you see?" | Nivora |
| Calendar open | "What meetings tomorrow?" | Infin |
| Document open | "Read this for me" | Either |
| Code review | "Review this code" | Nivora |

---

## 🎵 Voice IDs (ElevenLabs)

```python
INFIN_VOICE_ID = "iP95p4xoKVk53GoZ742B"   # Polished
NIVORA_VOICE_ID = "cgSgspJ2msm6clMCkdW9"  # Calm
```

---

## 🔧 Quick Debug

### Check if screen share working
```python
from screen_share import get_latest_frame
frame = get_latest_frame()
print(f"Frame available: {frame is not None}")
```

### Check voice switching
Look for logs:
```
Voice switched to Nivora: cgSgspJ2msm6clMCkdW9
```

### Check transfers
Look for logs:
```
Infin transferring to Nivora with topic: debug Python error
```

---

## 📁 Key Files

| File | Purpose |
|------|---------|
| `multi_agent_livekit.py` | ⭐ Main entrypoint |
| `generic_agent.py` | Base class |
| `tools.py` | Agent tools |
| `screen_share.py` | Frame buffer |

---

## 🐛 Common Issues

| Problem | Solution |
|---------|----------|
| Voice doesn't change | Check `GenericAgent.set_session(session)` |
| No screen share | Start sharing from client first |
| Transfer doesn't work | Check agent instructions |
| Vision returns empty | Make text larger on screen |

---

## 🎯 Test Sequence

1. ✅ **Start agent:** `python multi_agent_livekit.py`
2. ✅ **Join room:** From LiveKit client
3. ✅ **Test Infin:** "Check my calendar"
4. ✅ **Test transfer:** "Now debug this code"
5. ✅ **Test screen share:** Share screen → "What do you see?"
6. ✅ **Test transfer back:** "Send an email about this"

---

## 📚 Full Documentation

- [COMPLETE_SUMMARY.md](COMPLETE_SUMMARY.md) - Everything
- [TRANSFER_MECHANISM.md](TRANSFER_MECHANISM.md) - How transfers work
- [SCREEN_SHARE_GUIDE.md](SCREEN_SHARE_GUIDE.md) - Screen share details
- [ARCHITECTURE.md](ARCHITECTURE.md) - System diagrams

---

## ⚙️ Environment Variables

```env
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...
AWS_BEDROCK_MODEL=amazon.nova-pro-v1:0
LIVEKIT_URL=...
LIVEKIT_API_KEY=...
ELEVENLABS_API_KEY=...
```

---

**Quick tip:** Say "Look at my screen" to enable vision! 👁️

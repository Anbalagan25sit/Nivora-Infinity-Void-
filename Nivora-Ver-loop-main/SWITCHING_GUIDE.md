# Agent Switching Guide

## How Nivora & Infin Switch Automatically

The multi-agent system uses **three layers** of intent detection:

### 1. Explicit Commands (Highest Priority)

**Force switch to Infin/Jarvis:**
- "Switch to Infin"
- "Use Jarvis"
- "Activate Infin mode"
- "Call Infin"
- "Ask Jarvis"
- "Infin, help me"

**Force switch to Nivora:**
- "Switch to Nivora"
- "Activate study mode"
- "Call Nivora"
- "Ask Nivora"
- "Nivora, explain this"

These override everything else.

---

### 2. Automatic Keyword Detection

If no explicit command, the system scans for keywords:

**Life Keywords → Infin:**
```
email, calendar, schedule, meeting, appointment,
reminder, note, weather, today, tomorrow, agenda,
todo, task, gmail, inbox, free, busy
```

**Study Keywords → Nivora:**
```
code, python, debug, explain, research, study,
algorithm, project, git, github, machine learning,
ai, data science, database, api, architecture
```

---

### 3. Context Preservation

When no clear intent:
- **Keeps current persona** (maintains conversation flow)
- Example: "Actually, help me with that" → continues with current agent

---

## Technical Flow

```
User: "Check my calendar"
  ↓
RouterAgent.chat() intercepts
  ↓
_classify_intent("check my calendar")
  ↓ Detects "calendar" in LIFE keywords
  ↓
_switch_persona("infin")
  ├─ Update agent.instructions (to Infin prompt)
  ├─ Update agent.tools (to life tools: email, calendar, notes)
  ├─ Notify TTS: dynamic_tts.switch_to("infin")
  │   └─ Recreate elevenlabs.TTS with voice iP95p4xoKVk53GoZ742B
  ↓
LLM generates response with Infin persona
  ↓
TTS speaks with Jarvis voice
```

---

## Examples

| User Input | Detected Agent | Reason |
|------------|----------------|--------|
| "Send email to boss" | Infin | "email" keyword |
| "Explain Python decorators" | Nivora | "explain" + "python" |
| "What's on my calendar?" | Infin | "calendar" keyword |
| "Switch to Jarvis" | Infin | explicit command |
| "Debug this error" | Nivora | "debug" keyword |
| "Remind me at 5pm" | Infin | "remind" keyword |
| "How does blockchain work?" | Nivora | "how does" + study context |
| "Tell me about yourself" | Current | ambiguous → keep current |

---

## Implementation Details

```python
# In RouterAgent._classify_intent()
def _classify_intent(self, user_input: str) -> str:
    text = user_input.lower().strip()

    # 1. Check explicit commands
    if any(kw in text for kw in ["switch to nivora", "use jarvis", ...]):
        return target_persona

    # 2. Score keywords
    life_score = count(LIFE keywords in text)
    study_score = count(STUDY keywords in text)

    if life_score > 0 and study_score == 0:
        return "infin"
    if study_score > 0 and life_score == 0:
        return "nivora"

    # 3. Keep current
    return self.current_persona
```

---

## Testing Your Setup

Run this to test classification:

```bash
python -c "from multi_agent import RouterAgent; ...test cases..."
```

Or just speak naturally:
- **Life tasks** → Infin responds (Jarvis voice)
- **Study/tech** → Nivora responds (Nivora voice)
- **"Switch to X"** → Forces that persona

---

**Key Innovation**: Single AgentSession, dynamic persona mutation before each reply.

---

## Additional Features

### Auto-Greeting
When the agent joins the call, it automatically greets you with the appropriate persona:
- **Infin**: "How may I assist you today?"
- **Nivora**: "I'm here. What are we looking at?"

### End Conversation
The agent can gracefully end the call:
- User can say "end call", "goodbye", or "that's all"
- Agent says a persona-appropriate farewell
- Room is deleted cleanly

This is implemented via `end_conversation()` tool, which both personas have access to.

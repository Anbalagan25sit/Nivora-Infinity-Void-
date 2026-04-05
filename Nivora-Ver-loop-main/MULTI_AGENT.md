# Nivora Multi-Agent System

## Overview

Nivora now operates as a **multi-persona system** with two distinct AI companions, both powered by **AWS Nova Pro** via Amazon Bedrock:

1. **Nivora** - Study/Technical companion
2. **Infin (Jarvis)** - Life management assistant

Both personas share a single AgentSession but dynamically switch:
- **Voice**: ElevenLabs voice changes on-the-fly
- **Instructions**: Different system prompts per persona
- **Tools**: Only relevant tools for the current persona are exposed

---

## 🚀 Quick Start

### Running the Multi-Agent System

```bash
python multi_agent.py
```

The system will:
- Start with **Infin** (Jarvis) as the default persona
- Automatically detect intent from user speech
- Switch between Nivora and Infin seamlessly
- Change voices instantly when switching

### Configuration

Ensure your `.env` includes:

```env
AWS_BEDROCK_MODEL=amazon.nova-pro-v1:0
```

---

## 🎭 The Two Personas

### Nivora (Study/Technical)

**Voice ID:** `cgSgspJ2msm6clMCkdW9`

**Personality:**
- Calm, intellectual, darkly witty, deeply loyal
- Acts as a refined study companion and technical advisor

**Best for:**
- Programming help (Python, C++, JavaScript, etc.)
- System design and architecture
- Research and learning
- Debugging and problem-solving

**Tool Set:**
- Web search, weather, system control
- Spotify and YouTube media control
- Screen sharing (vision analysis)
- Universal website navigation

---

### Infin (Jarvis) - Life Management

**Voice ID:** `iP95p4xoKVk53GoZ742B`

**Personality:**
- Polished, professional, elegantly witty
- World-class butler-like competence

**Best for:**
- Email management (send, read)
- Calendar scheduling and events
- Notes and reminders
- Google Sheets integration

**Tool Set:**
- Email: `send_email`, `read_emails`
- Calendar: `google_calendar_list`
- Google Sheets: `google_sheets_read`, `google_sheets_write`
- Notes: `take_note`, `read_notes`
- Reminders: `set_reminder`
- Web search, weather, website navigation

---

## 🔄 How Switching Works

### Automatic Keyword-Based Switching

Before each reply, the system analyzes your message and switches personas if needed:

**→ Infin (Jarvis) triggers:**
```
email, gmail, send email, read email, calendar, schedule,
meeting, appointment, event, reminder, remind, note, notes,
weather, time, date, today, tomorrow, upcoming, agenda,
todo, task, list, organize, plan, check email, inbox,
compose, send mail, availability, free/busy
```

**→ Nivora triggers:**
```
study, learn, research, code, python, debug, program,
algorithm, project, hackathon, git, github, docker,
api, database, architecture, fix, error, bug, assignment,
how does, what is, explain, concept, c++, javascript,
machine learning, ai, data science, web dev, vscode,
terminal, linux, wsl, coding, software, tutorial
```

### Explicit Manual Switches (Highest Priority)

You can **force a switch** at any time with commands like:

**To switch to Infin/Jarvis:**
- "Switch to Infin"
- "Use Jarvis"
- "Activate Infin mode"
- "Call Infin"
- "Ask Jarvis"

**To switch to Nivora:**
- "Switch to Nivora"
- "Activate study mode"
- "Call Nivora"
- "Ask Nivora"

These explicit commands override keyword detection and immediately switch the persona and voice.

### Context Preservation

When the persona switches:
- ✅ **Conversation history** is preserved (both agents remember previous messages)
- ✅ **Voice changes instantly** (ElevenLabs TTS switches voice ID)
- ✅ **Tools change dynamically** (only relevant tools for the persona are exposed)
- ✅ **LLM stays the same** (AWS Nova Pro powers both)

### Examples in Action

```
User: "Check my calendar for tomorrow"
       ↓ (life keywords detected)
Infin: "You have a meeting at 2 PM and a dentist appointment at 4."

User: "Explain how neural networks work"
       ↓ (study keywords detected)
Nivora: "Neural networks are computational models inspired by biological neurons..."

User: "Send that email, then explain backpropagation"
       ↓ Starts with Infin (email), switches to Nivora (explain)
Infin: "Email sent."
Nivora: "Backpropagation is..."

User: "Switch to Jarvis"
       ↓ (explicit command)
Infin: "How may I assist you today?"

User: "Actually, switch to Nivora"
       ↓ (explicit command)
Nivora: "I'm here. What are we looking at?"
```

---

## 🏗️ Architecture

```
User speaks → STT → LiveKit Room → AgentSession
                                         ↓
                                RouterAgent (unified)
                                         ↓
                    _process_transcript hook:
                    - Classify intent
                    - Switch instructions if needed
                    - Switch TTS voice if needed
                    - Filter tools to persona set
                                         ↓
                               LLM (AWS Nova Pro)
                                         ↓
                               TTS (Dynamic Voice)
                                         ↓
                              Audio → LiveKit → User
```

**Key Components:**

| Component | Purpose |
|-----------|---------|
| `DynamicVoiceTTS` | Wrapper that can switch ElevenLabs voices at runtime |
| `RouterAgent` | Single Agent instance with all tools, dynamic instructions |
| `_process_transcript` | Hook that runs before each reply to detect persona |
| `AgentConfig` | Central config for voices and tool sets |

---

## 📝 Technical Details

### Single Session, Multiple Personas

Unlike the initial design (multiple sessions), this implementation uses **one AgentSession** with a custom `RouterAgent`. The agent:

1. Holds **all tools** from both personas
2. Stores both instruction sets
3. Intercepts each transcript via `_process_transcript()`
4. Mutates its own `instructions` and `tools` before generating a reply
5. Notifies TTS to switch voice

**Advantages:**
- ✅ Conversation history preserved automatically
- ✅ No session switching overhead
- ✅ Seamless transitions (no audio gaps)
- ✅ Works within LiveKit's single-session constraint

### Voice Switching

The `DynamicVoiceTTS` wrapper recreates the ElevenLabs TTS engine when the persona changes:

```python
def switch_to(self, persona: str):
    new_voice = NIVORA_VOICE_ID if persona == "nivora" else INFIN_VOICE_ID
    self._tts = elevenlabs.TTS(model="eleven_turbo_v2_5", voice_id=new_voice, language="en")
```

---

## 🛠️ Customization

### Adding Keywords

Edit the `LIFE` and `STUDY` sets in `multi_agent.py`:

```python
LIFE = {"email", "calendar", ..., "your_keyword"}
STUDY = {"code", "python", ..., "your_keyword"}
```

### Changing Voices

Update `AgentConfig`:

```python
class AgentConfig:
    NIVORA_VOICE_ID = "new_voice_id"
    INFIN_VOICE_ID = "new_voice_id"
```

### Adjusting Tool Access

Modify `NIVORA_TOOLS` and `INFIN_TOOLS` lists. The agent dynamically swaps its `tools` attribute when switching personas.

---

## 📊 Comparison Table

| Feature | Nivora | Infin (Jarvis) |
|---------|--------|----------------|
| **LLM** | AWS Nova Pro | AWS Nova Pro |
| **Voice** | cgSgspJ2msm6clMCkdW9 | iP95p4xoKVk53GoZ742B |
| **Tone** | Calm, witty, intellectual | Polished, professional, elegant |
| **Role** | Study/Technical companion | Life management assistant |
| **Tools** | Media, search, screen share | Email, calendar, notes, sheets |
| **Greeting** | "I'm here. What are we looking at?" | "How may I assist you today?" |

---

## 🐛 Troubleshooting

### Personas not switching
- **Check**: Keyword matching in `_process_with_switching`
- **Log**: Look for `"Switched:` messages in console

### Wrong voice
- **Check**: `AgentConfig.VOICE_ID` values
- **Verify**: ElevenLabs voice IDs are valid and active

### AWS Bedrock errors
- **Check**: `.env` has `AWS_BEDROCK_MODEL=amazon.nova-pro-v1:0`
- **Verify**: IAM credentials have Bedrock access

### MCP tools unavailable
- **Check**: `N8N_MCP_URL` and `N8N_BEARER_TOKEN` in `.env`
- **Verify**: n8n MCP server is running

---

## 🎯 Usage Examples

```
User: "Check my calendar for tomorrow"
→ Infin (life tools, Jarvis voice)

User: "Explain how neural networks work"
→ Nivora (study persona, Nivora voice)

User: "Send an email to John, then help me debug this Python error"
→ Starts with Infin (email), switches to Nivora (code help)

User: "What's the weather and can you explain quantum computing?"
→ Infin for weather (first keyword), Nivora for quantum (follow-up)
```

**Note**: The system switches personas based on EACH user message, not the whole conversation. This allows fluid topic changes.

---

## 🎯 Special Features

### Auto-Greeting
When the agent joins the room, it automatically greets the user with the appropriate persona:
- **Infin**: "How may I assist you today?"
- **Nivora**: "I'm here. What are we looking at?"

### End Conversation
Users can end the call naturally. The agent will:
1. Interrupt any ongoing speech
2. Say a persona-appropriate goodbye
3. Delete the room to cleanly end the session

**Example**: User says "end call" or "goodbye" → Agent says goodbye → Room closes

---

## 🔮 How It's Different

| Approach | Sessions | Context | Voice Switching | Feasibility |
|----------|----------|---------|----------------|-------------|
| Multiple sessions | 2+ | Manual transfer | Easy | ❌ LiveKit doesn't support |
| Single unified agent | 1 | Automatic | Runtime | ✅ Implemented |
| LLM classifier | 1 | Automatic | Runtime | Possible future upgrade |

Current implementation: **Single session with runtime persona mutation**

---

**Powered by**: LiveKit, AWS Nova Pro, ElevenLabs, Sarvam STT, Silero VAD

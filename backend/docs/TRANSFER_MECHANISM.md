# Agent Transfer Mechanism - Deep Dive

## 🔄 How the LiveKit Transfer Pattern Works

### The Core Concept

Unlike keyword-based switching (single agent changing behavior), the LiveKit pattern uses **explicit agent handoff** where:
1. Each agent is a **separate instance** with its own personality, tools, and voice
2. Agents **return other agents** via function tools
3. Chat context is **preserved across transfers**
4. Voice **switches automatically** during transfer

---

## 📊 Comparison: Old vs New Approach

| Feature | Keyword Switching (Old) | LiveKit Pattern (New) |
|---------|------------------------|----------------------|
| **Architecture** | 1 agent, dynamic instructions | Multiple agent instances |
| **Transfer Trigger** | Automatic keyword detection | Explicit function call |
| **User Control** | Passive (system decides) | Active (agent proposes, LLM decides) |
| **Voice Switching** | Manual TTS recreation | Automatic on transfer |
| **Context** | Single chat history | Shared chat context |
| **Tools** | Filtered dynamically | Each agent has its own set |
| **Clarity** | User may not know who's "speaking" | Clear handoff messages |

---

## 🎯 Transfer Flow Breakdown

### Example 1: Infin → Nivora (Technical Help)

```
User: "Check my calendar for tomorrow"
  ↓
Infin: [Uses google_calendar_list tool]
       "You have a meeting at 2 PM and a dentist appointment at 4."
  ↓
User: "Thanks! Now help me debug this Python error"
  ↓
Infin: [Detects technical topic via LLM reasoning]
       [Calls call_nivora_agent(topic="debug Python error")]
  ↓
System: [Creates NivoraAgent with shared chat_ctx]
        [Switches voice to Nivora's ElevenLabs voice]
        [Says: "Transferring you to Nivora for debug Python error."]
  ↓
Nivora: [Receives chat history + entry_topic]
        [Instructions include: "Address this immediately: debug Python error"]
        "I'm here. Let's look at that error."
```

### Example 2: Nivora → Infin (Life Management)

```
User: "Explain how neural networks work"
  ↓
Nivora: [Provides technical explanation]
        "Neural networks are computational models inspired by..."
  ↓
User: "Great! Can you send an email about this to my professor?"
  ↓
Nivora: [Detects life management topic]
        [Calls call_infin_agent()]
  ↓
System: [Creates InfinAgent with returning=True]
        [Switches voice to Infin's ElevenLabs voice]
        [Says: "Transferring you back to Infin for life management."]
  ↓
Infin: [Sees returning=True flag]
       "Welcome back. I'll send that email now."
       [Uses send_email tool]
```

---

## 🔧 Technical Implementation

### 1. GenericAgent Base Class

```python
class GenericAgent(Agent):
    # Shared session reference (class-level)
    _session_ref = None
    
    def __init__(self, voice_id, agent_name, ...):
        self.voice_id = voice_id
        self.agent_name = agent_name
    
    async def switch_voice(self):
        # Creates new ElevenLabs TTS with agent's voice_id
        # Updates session._tts at runtime
```

**Key Innovation**: Class-level session reference allows agents to modify TTS after instantiation.

### 2. Transfer Function Pattern

```python
@function_tool
async def call_nivora_agent(self, topic: str):
    # 1. Create new agent with shared context
    nivora = NivoraAgent(chat_ctx=self.chat_ctx, entry_topic=topic)
    
    # 2. Switch voice BEFORE transfer
    await nivora.switch_voice()
    
    # 3. Return tuple: (agent, handoff_message)
    return nivora, f"Transferring you to Nivora for {topic}."
```

**Key Innovation**: Voice switches **before** the new agent speaks, ensuring seamless audio transition.

### 3. Context Preservation

```python
# Infin creates Nivora
nivora_agent = NivoraAgent(
    chat_ctx=self.chat_ctx,  # ← Same ChatContext object
    entry_topic=topic
)
```

**Key Innovation**: Passing `chat_ctx` means Nivora sees the entire conversation history, including what Infin said.

### 4. Entry Context Awareness

```python
class NivoraAgent(GenericAgent):
    def __init__(self, entry_topic: str = None):
        topic_context = f"""
IMPORTANT: The user was transferred to you for: {entry_topic}
Address this immediately.
"""
```

**Key Innovation**: New agent knows **why** they were called, not just what was said.

---

## 🎤 Voice Switching Deep Dive

### How Voice Changes Work

```python
# Step 1: Session starts with Infin's voice
session = AgentSession(
    tts=elevenlabs.TTS(voice_id="iP95p4xoKVk53GoZ742B")  # Infin
)

# Step 2: During transfer, Nivora calls switch_voice()
async def switch_voice(self):
    new_tts = elevenlabs.TTS(voice_id="cgSgspJ2msm6clMCkdW9")  # Nivora
    self._session_ref._tts = new_tts  # ← Runtime replacement

# Step 3: Next synthesis uses new voice automatically
```

### Timing is Critical

```
❌ Wrong Order:
1. Return new agent
2. New agent speaks
3. Voice switches
   → User hears Nivora with Infin's voice!

✅ Correct Order:
1. Create new agent
2. Call switch_voice()  ← BEFORE returning
3. Return agent
   → User hears Nivora with Nivora's voice
```

---

## 🧠 How the LLM Decides to Transfer

### Infin's Transfer Instructions

```
If the user needs help with:
- coding, debugging, learning, research
- technical problems, study topics
- questions like "how does X work" or "explain Y concept"
→ call call_nivora_agent(topic="...")
```

### Examples That Trigger Transfer

| User Says | LLM Reasoning | Transfer? |
|-----------|---------------|-----------|
| "Check my email" | Life management topic | ❌ Stay with Infin |
| "Debug this Python code" | Technical + coding keyword | ✅ Call Nivora |
| "Explain neural networks" | Explain concept (study) | ✅ Call Nivora |
| "Set a reminder to study" | Reminder (life management) | ❌ Stay with Infin |
| "How does Docker work?" | Technical explanation | ✅ Call Nivora |

### The LLM's Decision Process

```
1. Read user message
2. Check transfer instructions in system prompt
3. Match keywords/patterns
4. Decide: Handle myself OR call transfer function
5. If transfer: Extract topic and call function_tool
```

---

## 🎭 State Management

### What Gets Preserved

✅ **Chat History**: Full conversation (all messages from both agents)
✅ **User Preferences**: If stored in chat context
✅ **Conversation Flow**: Natural continuation

### What Resets

🔄 **Agent Personality**: New instructions, new tone
🔄 **Available Tools**: Each agent has different toolset
🔄 **Voice**: Changes to new agent's voice_id

### Returning vs New Transfer

```python
# First time to Nivora
NivoraAgent(chat_ctx=ctx, entry_topic="debug code")

# Returning to Infin
InfinAgent(chat_ctx=ctx, returning=True)  # ← Flag changes greeting
```

---

## 🚀 Advantages Over Keyword Switching

### 1. **Explicit vs Implicit**
- **Keyword**: System silently changes behavior
- **LiveKit**: Agent explicitly says "Transferring you to..."

### 2. **LLM-Driven Intelligence**
- **Keyword**: Rule-based (if "email" in text → Infin)
- **LiveKit**: LLM reasons about intent ("Can you send that paper to my advisor?" → needs email → Infin)

### 3. **Clear Responsibility**
- **Keyword**: Ambiguous who's "speaking"
- **LiveKit**: Each agent is distinct entity

### 4. **Better Error Handling**
- **Keyword**: If switch fails, state corrupted
- **LiveKit**: If transfer fails, old agent still works

### 5. **Easier Testing**
- **Keyword**: Must test all persona combos
- **LiveKit**: Test each agent independently

---

## 🔮 Advanced Patterns

### Multi-Step Transfers

```python
User → Infin → Nivora → Infin → End
```

Chat context flows through all transfers:
```python
chat_ctx.messages = [
    "User: Check my calendar",
    "Infin: You have a 2PM meeting",
    "User: Debug this code",
    "Infin: Transferring to Nivora",
    "Nivora: I'm here. Let's look at it.",
    # ← All preserved
]
```

### Conditional Greetings

```python
# Nivora checks if this is first contact
if not self.chat_ctx.messages:
    greeting = "I'm here. What are we looking at?"
else:
    greeting = "Back to work. What's next?"
```

### Topic Injection

```python
# User asks Infin about code
Infin: call_nivora_agent(topic="debug Python error")

# Nivora's instructions include:
"User was transferred for: debug Python error
Address this IMMEDIATELY."

# Nivora prioritizes this over generic greeting
```

---

## 📝 Best Practices

### ✅ DO

1. **Always call `switch_voice()` before returning agent**
2. **Pass `chat_ctx` to preserve history**
3. **Use descriptive `topic` parameters** ("debug Python error" not just "help")
4. **Add transfer instructions to system prompts** (tell LLM when to transfer)
5. **Log transfers** for debugging

### ❌ DON'T

1. **Don't switch voice after returning** (too late)
2. **Don't create new ChatContext** (loses history)
3. **Don't use vague topics** ("help" tells new agent nothing)
4. **Don't assume transfers happen** (LLM might not call the tool)
5. **Don't transfer unnecessarily** (adds latency)

---

## 🐛 Troubleshooting

### Voice Doesn't Change

**Cause**: `switch_voice()` not called before transfer
**Fix**: Add `await new_agent.switch_voice()` before returning

### Agent Doesn't Know Why They Were Called

**Cause**: Missing `entry_topic` parameter
**Fix**: Pass topic to constructor and add to instructions

### Chat History Lost

**Cause**: New `ChatContext()` created instead of passing existing
**Fix**: Always pass `chat_ctx=self.chat_ctx`

### Transfer Doesn't Happen

**Cause**: LLM doesn't recognize trigger
**Fix**: Add clearer examples in transfer instructions

---

## 🎯 Summary

The LiveKit transfer pattern provides:

- **Clear agent identity** (users know who's helping)
- **Intelligent routing** (LLM decides when to transfer)
- **Seamless voice switching** (automatic on transfer)
- **Full context preservation** (no information loss)
- **Better debugging** (explicit transfer logs)

It's more sophisticated than keyword switching but provides a better user experience and clearer architecture.

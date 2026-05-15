# 🎓 From Bro Code Python to Understanding Nivora

## You Watched This: [Python Full Course - Bro Code (4 hours)](https://www.youtube.com/watch?v=m67-bOpOoPU)

**That's awesome!** Now let's connect what you learned to YOUR Nivora project.

---

## Section 1: Python Basics → Nivora Code

### ✅ What You Learned: Variables & Functions

**From video:**
```python
# Variables
name = "Anbu"
age = 20

# Functions
def greet(name):
    return f"Hello {name}"
```

**In YOUR Nivora code (agent.py):**
```python
# Line 77-78 in agent.py
AWS_REGION = os.getenv("AWS_REGION", "us-east-1").strip()
AWS_BEDROCK_MODEL = os.getenv("AWS_BEDROCK_MODEL", "amazon.nova-pro-v1:0").strip()
# ↑ Variables that store AWS settings

# Line 268 in agent.py
async def entrypoint(ctx: JobContext):
    logger.info("Agent entrypoint starting — room: %s", ctx.room.name)
    # ↑ This is a function that starts Nivora
```

**Understanding Check:**
- ✅ Can you find where `AWS_REGION` is used later in the file?
- ✅ What does `entrypoint` function do? (Hint: It's the main starting point!)

---

### ✅ What You Learned: Async/Await

**From video (probably covered briefly):**
```python
async def fetch_data():
    await something()  # Wait for this to finish
    return result
```

**Why Nivora uses async EVERYWHERE:**
```python
# Line 268 in agent.py
async def entrypoint(ctx: JobContext):  # ← "async" means it can wait for things
    await ctx.connect()  # ← "await" means WAIT for connection
    # Then continue...
```

**Why?** Voice agents need to:
- Wait for user to speak
- Wait for STT to convert audio
- Wait for LLM to think
- Wait for TTS to generate audio

**All at the same time without blocking!**

**Real Example:**
```python
# Without async (SLOW):
speech = convert_audio()      # Wait 1 second
response = get_llm_response() # Wait 1 second
audio = generate_tts()        # Wait 1 second
# Total: 3 seconds

# With async (FAST):
speech, response, audio = await asyncio.gather(
    convert_audio(),
    get_llm_response(),
    generate_tts()
)
# Total: 1 second (all run in parallel!)
```

**Understanding Check:**
- ✅ Find 5 functions in `agent.py` that use `async def`
- ✅ Find 5 places where `await` is used

---

### ✅ What You Learned: Imports

**From video:**
```python
import math
from datetime import datetime
```

**In YOUR Nivora code (agent.py, lines 48-58):**
```python
from livekit import agents                    # LiveKit voice platform
from livekit.agents import Agent, JobContext  # Voice agent classes
from livekit.plugins import silero, sarvam    # VAD & STT
import edge_tts_plugin                        # FREE TTS voices

from tools import ALL_TOOLS  # ← Imports ALL 111 tools from tools.py!
```

**Understanding Check:**
- ✅ Open `tools.py` - can you find where `ALL_TOOLS` is defined? (Hint: near the end)
- ✅ What does `from livekit.agents import Agent` mean? (Importing specific class)

---

### ✅ What You Learned: Classes & Objects

**From video:**
```python
class Car:
    def __init__(self, brand):
        self.brand = brand

    def drive(self):
        print(f"{self.brand} is driving")

my_car = Car("Toyota")
my_car.drive()  # "Toyota is driving"
```

**In YOUR Nivora code (agent.py, lines 162-191):**
```python
class NivoraAgent(Agent):  # ← Inherits from Agent class
    def __init__(self, *args, **kwargs):  # ← Constructor
        super().__init__(*args, **kwargs)  # ← Call parent constructor
        # Custom initialization here...

    async def on_message(self, message):  # ← Method
        # Handle messages...
```

**What this means:**
- `NivoraAgent` is a **custom voice agent** class
- It **inherits** from LiveKit's `Agent` class (gets all its features)
- We **override** `on_message` to add our own behavior

**Understanding Check:**
- ✅ What does `super().__init__()` do? (Calls parent class constructor)
- ✅ Find the `on_message` method - what does it do? (Hint: filters thinking tags)

---

### ✅ What You Learned: Dictionaries

**From video:**
```python
person = {
    "name": "Anbu",
    "age": 20,
    "city": "Chennai"
}
print(person["name"])  # "Anbu"
```

**In YOUR Nivora code (multi_agent_livekit.py, lines 117-142):**
```python
class AgentConfig:
    NIVORA_TOOLS = [          # ← List of tool functions
        web_search,
        spotify_play,
        open_website,
        # ... 111 total tools
    ]
```

**Understanding Check:**
- ✅ How many tools are in `NIVORA_TOOLS`?
- ✅ Add a print statement: `print(len(NIVORA_TOOLS))` to count them

---

## Section 2: Understanding The Voice Agent Flow

### The Journey of ONE Voice Command

Let's trace: **"Hey Nivora, play some music"**

#### Step 1: VAD (Voice Activity Detection)
**Code (agent.py, line 284-288):**
```python
vad=silero.VAD.load(
    min_silence_duration=0.3,  # Detect 300ms of silence
    activation_threshold=0.45,  # How sensitive to voice
)
```

**What happens:**
- Your microphone captures audio
- VAD listens for voice
- When you stop talking (300ms silence), VAD says: "User finished!"

**Exercise:** Change `min_silence_duration=0.3` to `0.1` - what happens? (Faster detection!)

---

#### Step 2: STT (Speech-to-Text)
**Code (agent.py, line 290-293):**
```python
stt=sarvam.STT(
    language="en-IN",
    model="saaras:v3",
)
```

**What happens:**
- Takes your audio: "Hey Nivora, play some music"
- Converts to text: `"Hey Nivora, play some music"`

---

#### Step 3: LLM (Large Language Model)
**Code (agent.py, line 296-299):**
```python
llm=aws.LLM(
    model=AWS_BEDROCK_MODEL,  # amazon.nova-pro-v1:0
    temperature=0.6,
)
```

**What happens:**
- LLM receives: `"Hey Nivora, play some music"`
- LLM has access to: `ALL_TOOLS` (111 functions)
- LLM thinks: "User wants music → I'll call `spotify_play()` tool"
- LLM calls: `spotify_play("random")`

**Exercise:** Open `tools.py` and find the `spotify_play()` function. What does it do?

---

#### Step 4: Tool Execution
**Code (tools.py, around line 1000):**
```python
@function_tool()
async def spotify_play(query: str = "random") -> str:
    """Play music on Spotify"""
    # Opens Spotify and plays music
    return "Playing music on Spotify!"
```

**What happens:**
- Function executes
- Spotify opens
- Music plays
- Returns: `"Playing music on Spotify!"`

---

#### Step 5: TTS (Text-to-Speech)
**Code (agent.py, line 301-304):**
```python
tts=edge_tts_plugin.TTS(
    voice="en-US-AriaNeural",
    rate="+5%",  # Slightly faster
)
```

**What happens:**
- Takes LLM response: `"Playing music on Spotify!"`
- Converts to audio (Aria's voice)
- Streams audio to your speakers

---

#### Step 6: You Hear It!
**Output:**
- 🔊 "Playing music on Spotify!" (in Aria's voice)
- 🎵 Spotify opens and plays music

---

### The Complete Flow (Visual)

```
1. You speak: "Hey Nivora, play some music"
           ↓
2. VAD detects: "User finished speaking"
           ↓
3. STT converts: Audio → "Hey Nivora, play some music"
           ↓
4. LLM thinks: "User wants music"
           ↓
5. LLM calls: spotify_play("random")
           ↓
6. Tool executes: Opens Spotify, plays music
           ↓
7. Tool returns: "Playing music on Spotify!"
           ↓
8. TTS converts: Text → Audio
           ↓
9. You hear: 🔊 "Playing music on Spotify!"
```

**Exercise:** Trace a different command through this flow:
- "Hey Nivora, what's the weather?"
- Which tool would it call? (Hint: `get_weather()`)

---

## Section 3: Understanding Tools

### What Are Tools?

**Simple explanation:**
Tools are just **Python functions** that the LLM can call!

**Anatomy of a Tool (tools.py):**
```python
@function_tool()  # ← This decorator tells LLM: "You can call this!"
async def open_website(url: str) -> str:  # ← Function signature
    """Opens a website in the default browser"""  # ← Description for LLM

    # The actual code
    import webbrowser
    webbrowser.open(url)

    return f"Opened {url}"  # ← Response back to LLM
```

**How LLM sees it:**
```
Tool: open_website
Description: Opens a website in the default browser
Parameters:
  - url (string): The website URL to open
Returns: Confirmation message
```

**When user says:** "Open YouTube"
**LLM thinks:** "I'll use open_website tool"
**LLM calls:** `open_website("https://youtube.com")`

---

### Your Challenge: Add a Simple Tool

Let's add a tool that tells you a joke!

**Step 1: Open `tools.py`**

**Step 2: Find a good place (around line 2300)**

**Step 3: Add this code:**
```python
@function_tool()
async def tell_joke() -> str:
    """Tells a random programming joke"""
    jokes = [
        "Why do programmers prefer dark mode? Because light attracts bugs!",
        "How many programmers does it take to change a light bulb? None, that's a hardware problem!",
        "Why do Python programmers wear glasses? Because they can't C#!"
    ]
    import random
    return random.choice(jokes)
```

**Step 4: Add to ALL_TOOLS list (around line 2493)**
```python
ALL_TOOLS = [
    # ... existing tools
    tell_joke,  # ← Add this line!
] + ALL_SPOTIFY_TOOLS + ...
```

**Step 5: Test it!**
```bash
python agent.py dev
```

Say: **"Tell me a joke"**

Nivora should call your tool and tell you a joke!

---

## Section 4: Understanding Prompts

### What Are Prompts?

**Prompts are instructions that shape Nivora's personality and behavior.**

**Open `prompts.py` (line 45):**
```python
max_sentences: str = "1 to 2 SHORT sentences for simple responses."
```

**This tells Nivora:** "Keep your answers short!"

**Change it to:**
```python
max_sentences: str = "5 to 10 long detailed sentences."
```

**Now Nivora will give LONG answers!**

---

### Your Challenge: Change Nivora's Personality

**Open `prompts.py` (line 19-21):**
```python
@dataclass
class IdentityConfig:
    name: str = "Nivora"
    creator: str = "Anbalagan, a curious engineer"
```

**Try changing:**
```python
name: str = "Friday"  # Like Iron Man's AI!
```

**Now run agent and say "Who are you?"**

Nivora will say: "I'm Friday!"

---

## Section 5: Practice Exercises

### Exercise 1: Find & Understand Code
1. ✅ Open `agent.py`
2. ✅ Find the `entrypoint` function
3. ✅ Read line by line
4. ✅ Ask yourself: "What does this line do?"

### Exercise 2: Modify a Tool
1. ✅ Open `tools.py`
2. ✅ Find `web_search()` function
3. ✅ Add a print statement: `print(f"Searching for: {query}")`
4. ✅ Test it!

### Exercise 3: Change TTS Voice
1. ✅ Open `agent.py` (line 302)
2. ✅ Change voice from `"en-US-AriaNeural"` to `"en-US-GuyNeural"`
3. ✅ Now Nivora is a male voice!

### Exercise 4: Add Your Own Tool
1. ✅ Copy the `tell_joke()` example above
2. ✅ Create `get_current_time()` tool that returns current time
3. ✅ Add to ALL_TOOLS
4. ✅ Test: "What time is it?"

---

## Section 6: Understanding Multi-Agent System

### Two Agents: Nivora & Infin

**File:** `multi_agent_livekit.py`

**Simple explanation:**
```
Infin (Default Agent):
- Female voice (Aria)
- Life management: Email, Calendar, Notes
- Can call Nivora for technical stuff

Nivora (Technical Agent):
- Male voice (Guy)
- Technical: Coding, Spotify, E-Box automation
- Can call Infin back for life stuff
```

**How Transfer Works (multi_agent_livekit.py, line 380):**
```python
@function_tool
async def call_nivora_agent(self, topic: str = ""):
    """Transfer conversation to Nivora for technical questions"""
    # Create Nivora agent with same chat history
    nivora = NivoraAgent(chat_ctx=self.chat_ctx, entry_topic=topic)
    # Switch voice to male
    await nivora.switch_voice()
    return nivora, "Transferring to Nivora..."
```

**What happens:**
1. User talking to Infin: "Help me with coding"
2. Infin thinks: "This is technical → call Nivora"
3. Infin executes: `call_nivora_agent("coding help")`
4. Voice switches: Aria → Guy
5. Now talking to Nivora!

---

## Section 7: Understanding LangGraph (Advanced)

**File:** `browser_use_langgraph.py`

**Simple explanation:**
LangGraph = GPS for your agent

**Without LangGraph:**
```
"Solve E-Box course"
[Agent tries everything at once, gets confused]
```

**With LangGraph:**
```
Phase 1: Initialize browser ✓
Phase 2: Login to E-Box ✓
Phase 3: Navigate to course ✓
Phase 4: Solve problems ✓
Phase 5: Verify completion ✓
Phase 6: Clean up ✓
```

**Code structure (browser_use_langgraph.py, line 60):**
```python
def _build_graph(self):
    workflow = StateGraph(AgentState)

    # Add phases
    workflow.add_node("initialize", self._initialize_node)
    workflow.add_node("login", self._login_node)
    workflow.add_node("solve", self._solve_node)

    # Connect phases
    workflow.add_edge("initialize", "login")  # After init → login
    workflow.add_edge("login", "solve")       # After login → solve
```

---

## Key Concepts Summary

### 1. **Async/Await**
- Used for things that take time (API calls, file operations)
- Lets Nivora do multiple things "at once"
- Every function that waits uses `async` and `await`

### 2. **Tools**
- Python functions the LLM can call
- Decorated with `@function_tool()`
- Added to `ALL_TOOLS` list
- LLM decides which tool to call based on user request

### 3. **Voice Flow**
- VAD → STT → LLM → Tool → TTS → Speaker
- Each step is async
- Prompt shapes LLM behavior

### 4. **Classes**
- `NivoraAgent` inherits from `Agent`
- Adds custom behavior (filtering thinking tags)
- Each agent has tools, voice, and personality

### 5. **Multi-Agent**
- Two agents can transfer conversations
- Each has different voice and tools
- Share same chat history

---

## Your Next Steps

### Today:
1. ✅ Read `agent.py` line by line (even if you don't understand everything)
2. ✅ Add the `tell_joke()` tool and test it
3. ✅ Change Nivora's voice to `en-US-GuyNeural`

### This Week:
1. ✅ Trace 3 different voice commands through the flow
2. ✅ Add 2 more simple tools (e.g., `flip_coin()`, `roll_dice()`)
3. ✅ Modify prompts to change personality

### Next Week:
1. ✅ Read `tools.py` and understand 10 different tools
2. ✅ Understand how multi-agent transfer works
3. ✅ Add a tool that integrates with a new API (e.g., weather, news)

---

## Questions to Test Your Understanding

### Level 1 (Basic):
1. What does `async def` mean?
2. What is VAD?
3. Where are all tools defined?
4. How do you change Nivora's voice?

### Level 2 (Intermediate):
1. Trace the flow of "open YouTube" command
2. How does LLM know which tool to call?
3. What's the difference between Nivora and Infin agents?
4. How do you add a new tool?

### Level 3 (Advanced):
1. Why do we use `await ctx.connect()`?
2. How does agent transfer preserve chat history?
3. What is LangGraph's role in browser automation?
4. How does streaming TTS work vs buffered TTS?

---

## Resources You Now Have

1. **Bro Code Video** - Python fundamentals ✓
2. **YOUR Codebase** - Real working examples ✓
3. **Documentation Files** - ARCHITECTURE.md, CLAUDE.md, etc. ✓
4. **This Guide** - Bridges video → your project ✓

---

## My Promise

**You watched Bro Code's Python tutorial.** That's 80% of what you need!

**Now spend 1-2 hours/day for 2 weeks:**
- Read code with this guide
- Do the exercises
- Ask questions when stuck

**After 2 weeks:**
- ✅ You'll understand YOUR codebase
- ✅ You can add simple features yourself
- ✅ You'll know where to look when debugging
- ✅ You'll feel CONFIDENT, not lost

---

**Ready to start?** Pick ONE exercise from Section 5 and do it RIGHT NOW! 🚀

Which one will you try first?

# SKILL.md — OpenDesk Desktop AI Agent
## Claude Code Skill: LiveKit Voice Agent + n8n Workflow Automation

---

## 🧠 OVERVIEW

This skill teaches Claude Code to build **OpenDesk** — a desktop AI agent that beats
Claude Cowork and Comet Agent on features & capabilities.

Core stack:
- **LiveKit** — real-time voice/video/data transport (sub-200ms latency)
- **n8n** — visual workflow automation engine (self-hosted, 400+ integrations)
- **Python FastAPI** — agent orchestration backend
- **Ollama** — local LLM for offline/privacy mode
- **Playwright** — browser automation
- **Chroma** — local vector memory

---

## 📁 PROJECT STRUCTURE
```
opendesk/
├── agent/
│   ├── main.py              # Entry point — starts LiveKit agent
│   ├── voice.py             # LiveKit voice pipeline (STT → LLM → TTS)
│   ├── router.py            # Multi-LLM router (Claude/GPT/Ollama/Groq)
│   ├── memory.py            # Chroma vector memory
│   ├── tools/
│   │   ├── filesystem.py    # File read/write/search
│   │   ├── browser.py       # Playwright web automation
│   │   ├── screen.py        # Screenshot + OCR + vision
│   │   ├── n8n_trigger.py   # Trigger n8n workflows via webhook
│   │   └── code_exec.py     # Sandboxed Python execution
├── n8n/
│   ├── workflows/           # Pre-built n8n workflow JSON exports
│   │   ├── email_summary.json
│   │   ├── file_watcher.json
│   │   └── daily_briefing.json
│   └── docker-compose.yml   # Self-hosted n8n setup
├── ui/
│   └── tray.py              # System tray app (pystray)
├── requirements.txt
└── .env
```

---

## ⚙️ ENVIRONMENT SETUP

### 1. Install dependencies
```bash
pip install livekit-agents livekit-plugins-openai livekit-plugins-silero \
  fastapi uvicorn chromadb playwright anthropic openai python-dotenv \
  pystray pillow pytesseract pyautogui
playwright install chromium
```

### 2. .env file
```env
LIVEKIT_URL=wss://your-livekit-server.com
LIVEKIT_API_KEY=your_api_key
LIVEKIT_API_SECRET=your_api_secret
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...
GROQ_API_KEY=gsk_...
N8N_WEBHOOK_BASE=http://localhost:5678/webhook
OLLAMA_BASE_URL=http://localhost:11434
```

### 3. Start n8n locally
```bash
cd n8n/
docker-compose up -d
# Access at http://localhost:5678
```

---

## 🎙️ LIVEKIT VOICE AGENT

### Pattern: Always use this pipeline structure
```python
# agent/voice.py
from livekit.agents import AutoSubscribe, JobContext, WorkerOptions, cli, llm
from livekit.agents.voice_assistant import VoiceAssistant
from livekit.plugins import openai, silero

async def entrypoint(ctx: JobContext):
    await ctx.connect(auto_subscribe=AutoSubscribe.AUDIO_ONLY)
    
    initial_ctx = llm.ChatContext().append(
        role="system",
        text="""You are OpenDesk, a powerful desktop AI agent. 
        You can control files, browse the web, run code, 
        trigger workflows, and remember past conversations.
        Be concise in voice responses. Use tools proactively."""
    )
    
    assistant = VoiceAssistant(
        vad=silero.VAD.load(),
        stt=openai.STT(),                    # Whisper
        llm=openai.LLM(model="gpt-4o"),      # or use router
        tts=openai.TTS(voice="nova"),         # ElevenLabs alternative
        chat_ctx=initial_ctx,
        fnc_ctx=build_tool_context(),         # Attach all tools
    )
    
    assistant.start(ctx.room)
    await asyncio.sleep(1)
    await assistant.say("OpenDesk ready. How can I help?", allow_interruptions=True)
```

### Key LiveKit rules:
- ALWAYS use `allow_interruptions=True` — users should be able to interrupt
- Use `silero.VAD` for voice activity detection (best accuracy)
- Keep TTS responses under 3 sentences for voice — use `[VOICE_BRIEF]` marker
- For long responses, speak summary and offer to show full text in UI

---

## 🔧 TOOL DEFINITIONS

### Pattern: Register tools as LiveKit function context
```python
# agent/tools/filesystem.py
from livekit.agents import llm
import os, glob, shutil

def build_filesystem_tools() -> llm.FunctionContext:
    fnc_ctx = llm.FunctionContext()
    
    @fnc_ctx.ai_callable(description="Read a file and return its contents")
    async def read_file(path: str) -> str:
        with open(os.path.expanduser(path), 'r') as f:
            return f.read()
    
    @fnc_ctx.ai_callable(description="Write content to a file")
    async def write_file(path: str, content: str) -> str:
        with open(os.path.expanduser(path), 'w') as f:
            f.write(content)
        return f"Written to {path}"
    
    @fnc_ctx.ai_callable(description="Search for files by name or pattern")
    async def search_files(pattern: str, directory: str = "~") -> str:
        results = glob.glob(
            os.path.join(os.path.expanduser(directory), "**", pattern), 
            recursive=True
        )
        return "\n".join(results[:20])
    
    return fnc_ctx
```

### All tools to build (in order of priority):
1. `filesystem.py` — read, write, search, move, delete files
2. `n8n_trigger.py` — POST to n8n webhooks to run workflows
3. `browser.py` — Playwright: open URL, click, type, extract text
4. `screen.py` — screenshot, OCR with pytesseract, find UI elements
5. `code_exec.py` — run Python in subprocess sandbox, return output
6. `memory.py` — store/retrieve from Chroma vector DB

---

## 🔗 N8N INTEGRATION

### Pattern: Trigger n8n workflows from the agent
```python
# agent/tools/n8n_trigger.py
import httpx
from livekit.agents import llm

N8N_BASE = "http://localhost:5678/webhook"

fnc_ctx = llm.FunctionContext()

@fnc_ctx.ai_callable(
    description="Trigger an n8n automation workflow by name. "
                "Available workflows: email_summary, file_watcher, daily_briefing, send_email"
)
async def trigger_workflow(workflow_name: str, data: dict = {}) -> str:
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{N8N_BASE}/{workflow_name}",
            json=data,
            timeout=30
        )
        return resp.text
```

### Pre-built n8n workflow templates to create:

**1. email_summary** — triggered every morning at 8am OR on demand
- Node 1: Gmail trigger / Webhook
- Node 2: Get last 24h emails
- Node 3: Claude API — summarize emails
- Node 4: Send summary to Slack / display in UI

**2. file_watcher** — monitors a folder for new files
- Node 1: File system watch trigger
- Node 2: Read file content
- Node 3: AI classify/process file
- Node 4: Move to correct folder or send to Notion

**3. send_email** — agent can send emails via voice command
- Node 1: Webhook (receives to, subject, body from agent)
- Node 2: Gmail send node
- Node 3: Return confirmation

**4. daily_briefing** — runs at 9am daily
- Node 1: Schedule trigger
- Node 2: Get calendar events (Google Calendar node)
- Node 3: Get top 5 news (RSS or Perplexity API)
- Node 4: Get pending tasks (Notion node)
- Node 5: Compile briefing → TTS → play via LiveKit

---

## 🧠 MULTI-LLM ROUTER

### Pattern: Route tasks to the right model
```python
# agent/router.py
from enum import Enum

class TaskType(Enum):
    FAST = "fast"           # Groq — <100ms
    REASONING = "reasoning" # Claude Sonnet — complex tasks
    VISION = "vision"       # GPT-4o — screen understanding
    PRIVATE = "private"     # Ollama — sensitive/offline tasks
    SEARCH = "search"       # Perplexity API — web research

def route_llm(task: str) -> tuple[str, str]:
    """Returns (provider, model) based on task keywords."""
    task_lower = task.lower()
    
    if any(k in task_lower for k in ["private", "confidential", "offline"]):
        return ("ollama", "llama3.2")
    
    if any(k in task_lower for k in ["search", "research", "find online", "latest"]):
        return ("perplexity", "sonar-pro")
    
    if any(k in task_lower for k in ["screen", "image", "see", "look at"]):
        return ("openai", "gpt-4o")
    
    if any(k in task_lower for k in ["quick", "yes/no", "simple"]):
        return ("groq", "llama-3.1-8b-instant")
    
    # Default: Claude for complex reasoning
    return ("anthropic", "claude-sonnet-4-6")
```

---

## 💾 PERSISTENT MEMORY

### Pattern: Store and retrieve semantic memories
```python
# agent/memory.py
import chromadb
from chromadb.utils import embedding_functions

client = chromadb.PersistentClient(path="~/.opendesk/memory")
ef = embedding_functions.OpenAIEmbeddingFunction(model_name="text-embedding-3-small")
collection = client.get_or_create_collection("memories", embedding_function=ef)

def remember(content: str, metadata: dict = {}):
    """Store a memory."""
    import uuid, datetime
    collection.add(
        documents=[content],
        metadatas=[{"timestamp": str(datetime.datetime.now()), **metadata}],
        ids=[str(uuid.uuid4())]
    )

def recall(query: str, n: int = 5) -> list[str]:
    """Retrieve relevant memories."""
    results = collection.query(query_texts=[query], n_results=n)
    return results["documents"][0] if results["documents"] else []
```

### What to store in memory:
- User preferences ("I prefer dark mode", "I use Python 3.11")
- Completed tasks and outcomes
- Frequently accessed file paths
- Custom workflow triggers user has defined
- Names of people user works with

---

## 🖥️ SCREEN UNDERSTANDING

### Pattern: Capture and analyze screen
```python
# agent/tools/screen.py
import pyautogui
import pytesseract
from PIL import Image
import base64, io

async def take_screenshot() -> str:
    """Take screenshot, return as base64."""
    screenshot = pyautogui.screenshot()
    buffer = io.BytesIO()
    screenshot.save(buffer, format="PNG")
    return base64.b64encode(buffer.getvalue()).decode()

async def read_screen_text() -> str:
    """OCR the current screen."""
    screenshot = pyautogui.screenshot()
    return pytesseract.image_to_string(screenshot)

async def click_on_text(text: str):
    """Find text on screen and click it."""
    screenshot = pyautogui.screenshot()
    data = pytesseract.image_to_data(screenshot, output_type=pytesseract.Output.DICT)
    for i, word in enumerate(data['text']):
        if text.lower() in word.lower():
            x = data['left'][i] + data['width'][i] // 2
            y = data['top'][i] + data['height'][i] // 2
            pyautogui.click(x, y)
            return f"Clicked '{text}' at ({x}, {y})"
    return f"Text '{text}' not found on screen"
```

---

## 🚀 STARTUP SEQUENCE

### Pattern: How to launch OpenDesk
```python
# agent/main.py
from livekit.agents import WorkerOptions, cli
from voice import entrypoint
from ui.tray import start_tray
import threading

if __name__ == "__main__":
    # Start system tray in background thread
    tray_thread = threading.Thread(target=start_tray, daemon=True)
    tray_thread.start()
    
    # Start LiveKit agent worker
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))
```

### Run commands:
```bash
# Start n8n
docker-compose -f n8n/docker-compose.yml up -d

# Start Ollama (for local LLM)
ollama serve &
ollama pull llama3.2

# Start OpenDesk agent
python agent/main.py dev
```

---

## ⚠️ CRITICAL RULES

1. **NEVER** store API keys in code — always use `.env`
2. **ALWAYS** sandbox code execution — use `subprocess` with timeout
3. **ALWAYS** confirm before deleting files — ask user first
4. **NEVER** send data to cloud LLM if user said "private"
5. **ALWAYS** log every action to `~/.opendesk/audit.log`
6. **NEVER** run pyautogui clicks without user confirmation for destructive actions
7. **ALWAYS** handle LiveKit disconnection gracefully — reconnect automatically
8. **NEVER** block the voice pipeline — all tools must be async

---

## 🧪 TESTING CHECKLIST

- [ ] Voice activation works (say "Hey OpenDesk")
- [ ] File read/write via voice command
- [ ] n8n email summary workflow triggers on demand
- [ ] Browser opens and navigates to URL
- [ ] Screen OCR reads text correctly
- [ ] Memory recalls past conversations
- [ ] Offline mode switches to Ollama automatically
- [ ] System tray shows agent status
- [ ] Audit log records all actions
- [ ] Interruptions work during TTS playback

---

## 📦 COMPETITIVE ADVANTAGES OVER COWORK & COMET

| Gap in Competitors | OpenDesk Solution |
|---|---|
| No voice interface | LiveKit real-time voice |
| No workflow automation | n8n with 400+ integrations |
| No offline/private mode | Ollama local LLM |
| No task scheduling | n8n cron triggers |
| No screen understanding | pytesseract + GPT-4V |
| No persistent memory | Chroma vector DB |
| No code execution | Sandboxed subprocess |
| Closed ecosystem | Plugin system via n8n |
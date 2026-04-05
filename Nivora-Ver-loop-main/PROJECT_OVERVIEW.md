# Nivora Project - How It Works

## 🎯 Overview

**Nivora** is an AI voice agent built on LiveKit that acts as your intelligent, calm, and witty companion. It can control your computer, search the web, manage Spotify playback, and much more — all through natural conversation.

**Key Features**:
- Voice-enabled AI assistant (real-time audio)
- **FREE Speech-to-Text**: OpenAI Whisper (open source, no API key)
- **FREE Text-to-Speech**: Microsoft Edge TTS (en-US-AriaNeural - natural female voice)
- Windows system control (Spotify, volume, keyboard shortcuts)
- Web search and website navigation
- Spotify control without API (using Windows-specific methods)
- **Gmail integration** (send, read, search, reply with OAuth2)
- **Notion integration** (create pages, search, log agent output)
- **Google Sheets** (read, write, append rows for tracking/logging)
- Tool calling with silent execution (agent doesn't announce tool use)
- Customizable personality (calm, intellectual, darkly witty)
- **100% Free Stack** - No API keys for TTS/STT, no subscriptions

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         User                                │
│  "Hey Nivora, play Bohemian Rhapsody by Queen"           │
└────────────────────────────┬──────────────────────────────┘
                             │ (Audio stream)
                             ▼
┌─────────────────────────────────────────────────────────────┐
│                 LiveKit Agent Framework                    │
│  - Handles WebSocket connections                         │
│  - Real-time audio streaming                             │
│  - Manages conversation state                             │
└────────────────────────────┬──────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│              Speech Pipeline (FREE)                        │
│  STT: OpenAI Whisper (free, no API key)                   │
│  TTS: Microsoft Edge TTS (en-US-AriaNeural, free)         │
└────────────────────────────┬──────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│                    Nivora Agent                           │
│  (agent.py + prompts.py + tools.py)                      │
│                                                            │
│  • Personality & instructions (prompts.py)                │
│  • Tool definitions (tools.py)                            │
│  • Agent loop & orchestration (agent.py)                  │
└────────────────────────────┬──────────────────────────────┘
                             │
              ┌──────────────┴──────────────┐
              │ Tool Calling (function calling) │
              ▼                               ▼
    ┌──────────────────┐        ┌──────────────────────┐
    │   Spotify Tools  │        │   Other Tools        │
    │  • play_media    │        │  • web_search        │
    │  • playback      │        │  • open_website      │
    │  • volume        │        │  • gmail (NEW)       │
    │  • shuffle       │        │  • notion (NEW)      │
    │  • repeat        │        │  • sheets (NEW)      │
    └────────┬─────────┘        └──────────┬───────────┘
             │                            │
             ▼                            ▼
    ┌──────────────────┐        ┌──────────────────────┐
    │ spotify_control  │        │ Various APIs &       │
    │     .py          │        │ System calls         │
    │ (Windows APIs)   │        │                      │
    └──────────────────┘        └──────────────────────┘
```

---

## 📁 Project Structure

```
Nivora-Ver-loop-main/
│
├── agent.py                    # Main LiveKit agent (Nivora's brain)
├── prompts.py                  # Persona, instructions, behavior rules
├── tools.py                    # Tool definitions & implementations
│
├── spotify_control.py          # Spotify control (no API)
│   ├── search                 #   - Search & play songs
│   ├── now-playing            #   - Get current track
│   ├── playback               #   - play/pause/next/previous
│   ├── shuffle                #   - Toggle shuffle
│   ├── repeat                 #   - Cycle repeat modes
│   ├── volume                 #   - Volume control (pycaw/nircmd)
│   └── stop                   #   - Pause/quit/kill
│
├── agent/tools/               # NEW: Modular tool implementations
│   ├── __init__.py           #   - Package init
│   ├── gmail_tool.py         #   - Gmail API integration (OAuth2)
│   ├── notion_tool.py        #   - Notion API integration
│   ├── sheets_tool.py        #   - Google Sheets API v4
│   ├── setup_gmail.py        #   - Gmail OAuth setup script
│   ├── setup_notion.py       #   - Notion API connection test
│   ├── setup_sheets.py       #   - Sheets OAuth scope updater
│   ├── test_gmail.py         #   - Gmail tool test suite
│   ├── test_notion.py        #   - Notion tool test suite
│   ├── GMAIL_SETUP.md        #   - Gmail setup guide
│   ├── NOTION_SETUP.md       #   - Notion setup guide
│   └── SHEETS_SETUP.md       #   - Sheets setup guide
│
├── spotify_api.py              # OLD: Spotify Web API (deprecated)
├── spotify_tool.py             # Older Spotify tools wrapper
│
├── computer_use.py             # Computer automation (browser, etc.)
│
├── .env                        # API keys & configuration
├── credentials.json            # Google OAuth credentials
├── requirements.txt            # Python dependencies
├── tools.bat                   # Windows batch wrapper
│
└── docs/
    ├── PROJECT_OVERVIEW.md     # This file
    ├── INTEGRATION_SUMMARY.md  # Spotify integration details
    └── AUTOPLAY_FIX_SUMMARY.md # Autoplay fix documentation
```

---

## 🔄 How a Conversation Flows

### Example: User says "Play Blinding Lights by The Weeknd"

1. **Audio Input**:
   - User's voice is captured → sent to LiveKit server
   - LiveKit forwards audio stream to `agent.py`

2. **Speech-to-Text** (Whisper - FREE):
   - LiveKit captures audio stream
   - OpenAI Whisper transcribes audio (runs locally or via API)
   - No API key needed if running locally
   - Text: `"Play Blinding Lights by The Weeknd"`

3. **LLM Processing** (agent.py):
   - Text sent to LLM (AWS Bedrock Nova)
   - LLM has the `prompts.py` system prompt loaded
   - LLM recognizes intent: "User wants to play music"
   - LLM decides to use tool: `spotify_play_media(query="Blinding Lights", media_type="track")`
   - LLM returns tool call request (no narration because prompt forbids it)

4. **Tool Execution** (tools.py):
   - `agent.py` receives tool call request
   - Looks up `spotify_play_media` function in `tools.py`
   - Function runs:
     ```python
     uri = f"spotify:search:track:Blinding+Lights"
     subprocess.run(['python', 'spotify_control.py', 'search', '--uri', uri, '--autoplay'])
     ```
   - `spotify_control.py` opens Spotify and auto-plays first result

5. **Tool Result**:
   - `spotify_play_media` returns: `"Opened Spotify and started the top result for 'Blinding Lights' (type: track)."`
   - Returns to LLM

6. **LLM Response**:
   - LLM sees success message
   - Generates concise response: *"Playing Blinding Lights now."*
   - (Or says nothing if playback started visibly)

7. **Text-to-Speech** (Edge TTS - FREE):
   - Response text sent to Microsoft Edge TTS engine
   - Uses en-US-AriaNeural voice (natural, sweet female voice)
   - Completely free, no API key required
   - Audio generated and streamed back through LiveKit
   - User hears: *"Playing Blinding Lights now."*

---

## 🧠 How Nivora's Personality Works

### Prompts System (`prompts.py`)

The `prompts.py` file defines Nivora's entire personality through dataclasses:

#### 1. IdentityConfig
- `name`: "Nivora"
- `creator`: Who created the agent
- `purpose`: Mission statement

#### 2. CommunicationConfig
- `max_sentences`: "1 to 3 short, precise sentences"
- `tone`: "serene, intellectual, darkly witty, subtly warm"
- `avoid`: "being loud, overly cheerful, corporate. No emojis."
- `prefer_action`: "Speak with quiet confidence. Let silences mean something."

#### 3. BehaviorConfig
Defines personality modes:
- **Scholar Mode**: Knowledge with quiet authority
- **Dry Wit Mode**: Deadpan humor
- **Quietly Devoted Mode**: Loyalty through actions
- **Protective Mode**: Steady presence when stressed
- **Analytical Mode**: Logical, emotionless breakdown

Also includes the **CRITICAL BEHAVIOR** about tool use:
- Never announce tools
- No "let me check" phrases
- Just execute silently and respond with result

#### 4. LLMConfig
- `tool_rules`: How to use tools correctly
- One tool at a time
- Wait for result before next action
- Never invent tool names

### Building the Prompt

`build_agent_instruction()` combines all configs into a single system prompt:

```python
prompt = f"""[IDENTITY] You are {i.name}. Created by {i.creator}. Purpose: {i.purpose}

About the user: {u.description}

How you speak:
- {comm.max_sentences}
- Tone: {comm.tone}
- Avoid: {comm.avoid}
...

Behavioral Guidelines:
{behavior_rules}

CRITICAL BEHAVIOR - TOOL USE:
- NEVER announce tool usage...
...

Media routing:
- Spotify play → spotify_play_media(query, media_type)
- Spotify pause → spotify_control_playback(action)
...
"""
```

This massive prompt (4594 characters) is sent as the **system message** to the LLM.

---

## 🔧 Tool System

### Declaring Tools (`tools.py`)

Tools are defined using the `@function_tool` decorator from LiveKit:

```python
@function_tool(
    description="Play music on Spotify without API"
)
async def spotify_play_media(
    context: RunContext,
    query: Annotated[str, "The search term"],
    media_type: Annotated[str, "track, artist, album, playlist, or all"] = "all",
) -> str:
    """Implementation"""
    # Call spotify_control.py
    result = subprocess.run(['python', SPOTIFY_CONTROL_SCRIPT, ...])
    return result.stdout
```

### Tool Parameters

Parameters are annotated with `Annotated[type, "description"]`:
- The LLM uses the description to understand the parameter
- Type hints ensure correct data passed

### Tool Discovery

When the agent starts:
1. All `@function_tool` decorated functions are collected
2. Their schemas (name, description, parameters) extracted
3. Sent to LLM in initial system prompt via `tool_reference` or automatically detected

### Tool Execution Flow

1. LLM decides to call a tool → returns JSON: `{ "tool": "spotify_play_media", "args": { "query": "Bohemian Rhapsody", "media_type": "track" } }`
2. `agent.py` receives this → looks up function in registry
3. Calls function with `RunContext` and arguments
4. Function executes (may call subprocess, APIs, etc.)
5. Return value captured → sent back to LLM as tool result
6. LLM generates final response

---

## 🎵 Spotify Control Deep Dive

### No-API Approach

The original `spotify_api.py` required OAuth tokens and Web API access. The new `spotify_control.py` uses **Windows-native methods**:

#### Method 1: URI Protocol (`spotify:`)
- `spotify:search:query` opens Spotify app directly
- `spotify:track:<id>` plays specific track
- Uses `os.startfile()` → calls Windows ShellExecute

#### Method 2: Web URL Fallback
- `https://open.spotify.com/search/query`
- Opens in browser, which redirects to desktop app

#### Window Title Reading
- Spotify's window title is "Artist - Song" while playing
- PowerShell: `(Get-Process Spotify).MainWindowTitle`
- Parsed to extract track info

#### Keyboard Simulation
Uses Windows API `keybd_event()`:
- `VK_MEDIA_PLAY_PAUSE` (0xB3) - Play/Pause
- `VK_CONTROL + VK_S` (0x11 + 0x53) - Shuffle
- `VK_CONTROL + VK_R` (0x11 + 0x52) - Repeat
- `VK_RETURN` (0x0D) - Enter (to select search results)
- `VK_ESCAPE` (0x1B) - Dismiss ads

#### Volume Control
Two methods:
1. **pycaw** (default) - Python library for Windows Audio Session API
   - Finds Spotify audio session by process name
   - Adjusts per-application volume
2. **nircmd** - External tool from NirSoft
   - System-level volume control

#### Process Management
- `taskkill /IM Spotify.exe /F` to quit
- Kills helper processes: `SpotifyCrashService.exe`, `SpotifyWebHelper.exe`

---

## 🔄 Integration Points

### How Tools.py Uses spotify_control.py

```python
# In tools.py

SPOTIFY_CONTROL_SCRIPT = os.path.join(os.path.dirname(__file__), 'spotify_control.py')

async def spotify_play_media(context, query, media_type="all") -> str:
    # Build search URI
    uri = f"spotify:search:{urllib.parse.quote(query)}"
    # Call spotify_control with --autoplay flag
    result = subprocess.run(
        [sys.executable, SPOTIFY_CONTROL_SCRIPT, 'search', '--uri', uri, '--autoplay'],
        capture_output=True, text=True
    )
    return result.stdout
```

The `--autoplay` flag triggers the sophisticated keyboard/mouse automation to actually play the song.

---

## 📧 Productivity Tools Deep Dive

### Gmail Integration (`agent/tools/gmail_tool.py`)

**OAuth2 Authentication**:
- Uses Desktop app OAuth credentials
- Token cached in `~/.nivora/gmail_token.json`
- Auto-refreshes when expired
- Secure, no password storage

**Functions**:
1. **send_email** - Send emails via Gmail API
2. **read_emails** - Read inbox with query filters (is:unread, from:sender)
3. **search_emails** - Full Gmail query syntax support
4. **reply_to_email** - Reply with thread context preservation
5. **get_email_summary** - Morning briefing (unread count, important emails)

**Voice Commands**:
```
"Send email to john@example.com about meeting"
"Read my unread emails"
"Search emails from professor"
"Reply to that saying thanks"
"Give me my email summary"
```

**Setup**: Requires Google Cloud Console OAuth app, scopes: gmail.send, gmail.readonly, gmail.modify

---

### Notion Integration (`agent/tools/notion_tool.py`)

**API Authentication**:
- Uses Notion Internal Integration token
- Token in .env as `NOTION_API_KEY`
- Pages must be explicitly shared with integration

**Functions**:
1. **create_notion_page** - Create pages with markdown content
2. **search_notion** - Search all accessible pages/databases
3. **read_notion_page** - Read full page content
4. **add_to_notion_database** - Add entries to databases
5. **update_notion_page** - Append content to pages
6. **save_agent_output** - Auto-log with timestamps to "Nivora Notes"

**Voice Commands**:
```
"Create a Notion page about project ideas"
"Search Notion for my meeting notes"
"Read my Notion page about API docs"
"Add task to my Notion database"
"Save this to Notion"
```

**Markdown Support**:
- Headers: `# H1`, `## H2`, `### H3`
- Bullets: `- item`, numbered: `1. item`
- Checkboxes: `[ ]` unchecked, `[x]` checked
- Dividers: `---`

---

### Google Sheets Integration (`agent/tools/sheets_tool.py`)

**OAuth2 Authentication**:
- **Reuses Gmail OAuth token** - same token for both APIs!
- Adds `spreadsheets` scope to existing token
- Token refresh preserved

**Functions**:
1. **read_sheet** - Read data from spreadsheets (A1 notation)
2. **write_to_sheet** - Write to specific cells/ranges
3. **append_row** - Add rows at bottom (perfect for logging)
4. **search_sheet** - Search across all cells
5. **create_spreadsheet** - Create new spreadsheets
6. **get_sheet_summary** - Get row counts, headers, sheet names

**Voice Commands**:
```
"Read my expenses sheet"
"Add a row to my tracker: today, exercise, done"
"Search my sheet for Nivora"
"Create a spreadsheet called Project Tracker"
"How many rows are in my sheet?"
```

**Use Cases**:
- Habit tracking (daily logging)
- Expense tracking (append_row for quick entry)
- Project management (task sheets)
- Meeting notes logger
- Daily journal

**Range Notation Examples**:
- `Sheet1!A1` - Single cell
- `Sheet1!A1:B10` - Rectangle
- `Sheet1!A:C` - Columns A-C
- `Sheet1!1:1` - First row (headers)

---

## 🎙️ LiveKit Agent Framework

### agent.py Responsibilities

1. **Connection Management**:
   - Connect to LiveKit room
   - Subscribe to audio track from user
   - Publish audio track to room

2. **Audio Pipeline** (FREE Stack):
   - Receive audio frames → VAD (voice activity detection)
   - Send audio to **OpenAI Whisper** (free STT, no API key)
   - Get transcript → send to LLM
   - Receive LLM response → send to **Microsoft Edge TTS** (free, en-US-AriaNeural)
   - Stream TTS audio back

3. **Tool Calling**:
   - Parse LLM responses for tool calls
   - Execute tools from `tools.py`
   - Feed results back to LLM

4. **State Management**:
   - Maintain conversation context
   - Handle interruptions
   - Track user identity

---

## 🛠️ Technical Stack

| Layer | Technology |
|-------|------------|
| **Agent Framework** | LiveKit Agents SDK |
| **LLM** | AWS Bedrock (Nova model) |
| **STT/TTS** | LiveKit's built-in (Deepgram/ElevenLabs) |
| **Python Version** | 3.13+ |
| **OS** | Windows 10/11 (for Spotify tools) |
| **Spotify Control** | `ctypes` (Windows API), `subprocess`, PowerShell |
| **Optional Dependencies** | `pycaw` (volume control), `nircmd` (volume fallback) |
| **Gmail/Sheets** | Google API Client, OAuth2 (gmail.send, gmail.readonly, spreadsheets) |
| **Notion** | Notion API Client (Internal Integration token) |
| **Other APIs** | DuckDuckGo (web search), YouTube |

---

## 🎛️ Configuration

### Environment Variables (.env)

```bash
# LiveKit Connection
LIVEKIT_API_KEY="..."
LIVEKIT_API_SECRET="..."
LIVEKIT_URL="wss://..."

# Gmail & Google Sheets (OAuth2 via credentials.json)
# Token auto-saved to ~/.nivora/gmail_token.json

# Notion API
NOTION_API_KEY="secret_xxxxx"
NOTION_DEFAULT_DATABASE_ID="abc123..."  # Optional
NOTION_NOTES_PAGE_ID="def456..."        # Optional

# Google Sheets (optional - for quick reference)
HABITS_SHEET_ID="1abc123..."
EXPENSES_SHEET_ID="1def456..."
```

**Authentication Files**:
- `credentials.json` - Google OAuth Desktop app credentials (for Gmail + Sheets)
- `~/.nivora/gmail_token.json` - Cached OAuth token (auto-generated)

Optional:
- Spotify API credentials (if using Web API instead of local control)
- Other service API keys

### Customizing Nivora

Edit `prompts.py`:
- Change `IdentityConfig.name` → changes agent's name
- Modify `CommunicationConfig.tone` → adjust speaking style
- Add/remove `BehaviorConfig.rules` → customize personality
- Update `TechnicalScopeConfig.domains` → change expertise areas

---

## 🔍 Debugging & Testing

### Test Spotify Control Directly

```bash
# Test search
python spotify_control.py search --song "Test" --artist "Band" --autoplay

# Test now-playing
python spotify_control.py now-playing

# Test volume
python spotify_control.py volume --set 50

# Test playback
python spotify_control.py playback next
```

### Test Tool Integration

```python
# Quick Python test
from tools import spotify_play_media
result = await spotify_play_media(None, "Blinding Lights", "track")
print(result)
```

### Agent Logs

The agent logs to console with levels:
- `[LocalMedia]` - Spotify operations
- `[INFO]` - General info
- `[ERROR]` - Failures

Check LiveKit logs for connection issues.

---

## 🚀 How to Run

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Install Spotify** (desktop app required for control)

3. **Set up .env** with LiveKit credentials

4. **Run the agent**:
   ```bash
   python agent.py
   ```

5. **Connect a client**:
   - Use LiveKit CLI or browser demo
   - Join the room
   - Start talking!

---

## 📊 Data Flow Summary

```
Voice → STT → Text → LLM (with tools) → Decision
         ↓
    Tool Call? → Yes → Execute tool → Return result → LLM → Response
               ↓ No
          Direct response
         ↓
    TTS → Audio → User
```

---

## 🎯 Key Design Decisions

### Why No Spotify API?
- No OAuth tokens needed
- Works with Spotify Free
- No rate limits
- Fully local (privacy)

### Why Windows APIs?
- Direct system control
- No external dependencies (except pycaw optional)
- Reliable for desktop app

### Why Silent Tool Execution?
- Feels more natural, like talking to a human
- No robotic "one moment please"
- Immersive conversation

---

## 🔮 Future Enhancements

- [ ] Image recognition for ad detection (cv2)
- [ ] Machine learning to predict best autoplay strategy
- [ ] Voice command shortcuts ("next track", "louder")
- [ ] Playlist management (create, add to, etc.)
- [ ] Spotify recommendation integration
- [ ] Cross-platform support (macOS/Linux)
- [ ] Multi-user conversation memory

---

## 📚 Summary

**Nivora** is a sophisticated voice agent that:
- Listens and responds naturally
- Controls Spotify locally without API
- **Manages Gmail** (send, read, search, reply via OAuth2)
- **Integrates with Notion** (create pages, search, knowledge management)
- **Controls Google Sheets** (read, write, append for tracking/logging)
- Uses intelligent fallback strategies for reliability
- Maintains a consistent, calm, intellectual personality
- Integrates seamlessly with Windows desktop

The project demonstrates:
- **Tool calling** with LLMs
- **Windows automation** via Python
- **Real-time audio** processing
- **Modular architecture** (separate prompts, tools, agent)
- **OAuth2 authentication** (Gmail + Sheets token reuse)
- **API integrations** (Notion, Google services)
- **Robust error handling** and fallbacks

**Total Lines of Code**: ~8,000+ lines across 50+ files

**New Productivity Tools** (3):
- Gmail (5 functions) - ~500 lines
- Notion (6 functions) - ~550 lines
- Google Sheets (6 functions) - ~500 lines

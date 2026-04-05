# System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         USER (LiveKit Client)                            │
│                                                                          │
│  🎤 Voice Input    📺 Screen Share    🔊 Voice Output                   │
└─────────────────┬────────────────────────────┬────────────────────────┬─┘
                  │                            │                        │
                  ▼                            ▼                        ▼
         ┌────────────────┐          ┌─────────────────┐      ┌──────────────┐
         │  Sarvam STT    │          │  Screen Track   │      │ ElevenLabs   │
         │  (en-IN)       │          │  (Video Stream) │      │  TTS         │
         └────────┬───────┘          └────────┬────────┘      └──────▲───────┘
                  │                           │                      │
                  │                           │                      │
         ┌────────▼───────────────────────────▼──────────────────────┴───────┐
         │                     LIVEKIT ROOM                                   │
         │  ┌──────────────────────────────────────────────────────────────┐ │
         │  │              AGENT SESSION (Single Session)                   │ │
         │  │  ┌────────────────────────────────────────────────────────┐  │ │
         │  │  │           AWS Nova Pro LLM (Shared)                     │  │ │
         │  │  └────────────────────────────────────────────────────────┘  │ │
         │  │                                                               │ │
         │  │  ┌──────────────────────┐      ┌──────────────────────┐     │ │
         │  │  │   InfinAgent         │      │   NivoraAgent        │     │ │
         │  │  │   (Default)          │◄────►│   (Transferred)      │     │ │
         │  │  │                      │      │                      │     │ │
         │  │  │ 🎵 Infin Voice       │      │ 🎵 Nivora Voice      │     │ │
         │  │  │ 📧 Email             │      │ 💻 Spotify           │     │ │
         │  │  │ 📅 Calendar          │      │ 🎥 YouTube           │     │ │
         │  │  │ 📝 Notes             │      │ 🌐 Web Search        │     │ │
         │  │  │ 👁️ Screen Vision     │      │ 👁️ Screen Vision     │     │ │
         │  │  │                      │      │                      │     │ │
         │  │  │ @function_tool       │      │ @function_tool       │     │ │
         │  │  │ call_nivora_agent()  │      │ call_infin_agent()   │     │ │
         │  │  └──────────────────────┘      └──────────────────────┘     │ │
         │  │                                                               │ │
         │  │  ┌────────────────────────────────────────────────────────┐  │ │
         │  │  │           SHARED CHAT CONTEXT                           │  │ │
         │  │  │  [User msg] [Infin reply] [User msg] [Nivora reply]    │  │ │
         │  │  └────────────────────────────────────────────────────────┘  │ │
         │  └───────────────────────────────────────────────────────────────┘ │
         └────────────────────────────────────────────────────────────────────┘
                                      │
                    ┌─────────────────┼─────────────────┐
                    │                 │                 │
                    ▼                 ▼                 ▼
         ┌──────────────────┐ ┌─────────────┐ ┌───────────────────┐
         │ MCP Server (n8n) │ │ Screen Share│ │ AWS Bedrock Nova  │
         │                  │ │ Frame Buffer│ │ (Vision API)      │
         │ • Spotify        │ │             │ │                   │
         │ • YouTube        │ │ Latest Frame│ │ Analyzes screens  │
         │ • GitHub         │ │ (RGBA→RGB)  │ │ Returns JSON      │
         └──────────────────┘ └─────────────┘ └───────────────────┘
```

---

## Transfer Flow Sequence

```
┌──────┐                ┌──────────┐              ┌──────────┐
│ User │                │  Infin   │              │  Nivora  │
└──┬───┘                └────┬─────┘              └────┬─────┘
   │                         │                         │
   │ "Check my calendar"     │                         │
   ├────────────────────────►│                         │
   │                         │                         │
   │                         │ [Uses calendar tool]    │
   │◄────────────────────────┤                         │
   │ "3 meetings tomorrow"   │                         │
   │                         │                         │
   │ "Debug this Python code"│                         │
   ├────────────────────────►│                         │
   │                         │                         │
   │                         │ [Detects technical]     │
   │                         │ call_nivora_agent()     │
   │                         │ [Switch voice]          │
   │                         ├────────────────────────►│
   │                         │                         │
   │                         │ "Transferring..."       │
   │◄────────────────────────┴────────────────────────┤
   │                                                   │
   │                         [Context transferred]    │
   │                         [entry_topic: "debug"]   │
   │                                                   │
   │                         "I'm here. Let me look"  │
   │◄──────────────────────────────────────────────────┤
   │                                                   │
   │ "Thanks! Send email"                              │
   ├──────────────────────────────────────────────────►│
   │                                                   │
   │                         [Detects life topic]     │
   │                         call_infin_agent()       │
   │◄──────────────────┬─────────────────────────────┤
   │                   │     [Switch voice]           │
   │                   │                              │
   │ "Welcome back"    │                              │
   │◄──────────────────┘                              │
   │                                                   │
```

---

## Screen Share Vision Flow

```
┌────────────┐     ┌──────────────┐     ┌────────────┐     ┌──────────┐
│ User Shares│     │ LiveKit Room │     │Frame Buffer│     │  Agent   │
│   Screen   │     │   Monitor    │     │(screen_share│     │  (Tool)  │
└─────┬──────┘     └──────┬───────┘     │    .py)    │     └────┬─────┘
      │                   │              └─────┬──────┘          │
      │ Start Share       │                    │                 │
      ├──────────────────►│                    │                 │
      │                   │                    │                 │
      │                   │ track_subscribed   │                 │
      │                   ├───────────────────►│                 │
      │                   │                    │                 │
      │                   │ start_frame_       │                 │
      │                   │    capture(track)  │                 │
      │                   ├───────────────────►│                 │
      │                   │                    │                 │
      │ Video Frames      │                    │                 │
      ├──────────────────►│───────────────────►│                 │
      │ (30 FPS)          │                    │ [Store latest]  │
      │                   │                    │                 │
      │                                        │                 │
      │                                        │                 │
User: "What do you see?"                       │                 │
      ├────────────────────────────────────────┴────────────────►│
      │                                                          │
      │                                        get_latest_frame()│
      │                                        ◄─────────────────┤
      │                                                          │
      │                          ┌──────────────────────────┐   │
      │                          │  AWS Nova Pro Vision     │   │
      │                          │  analyze_screen()        │   │
      │                          │  - Base64 encode image   │   │
      │                          │  - Send to Bedrock API   │   │
      │                          │  - Parse JSON response   │◄──┤
      │                          └──────────────┬───────────┘   │
      │                                         │               │
      │◄────────────────────────────────────────┴───────────────┤
      │ "I see VSCode with a NameError on line 47..."           │
      │                                                          │
```

---

## Voice Switching Mechanism

```
┌─────────────────────────────────────────────────────────────┐
│                    AgentSession                              │
│                                                              │
│  session._tts = elevenlabs.TTS(voice_id="infin_voice")      │
│                                  ▲                           │
│                                  │                           │
│  ┌────────────────────────────┐  │  ┌────────────────────┐  │
│  │  InfinAgent                │  │  │  NivoraAgent       │  │
│  │  voice_id = "infin_voice"  │  │  │  voice_id = "niv"  │  │
│  │                            │  │  │                    │  │
│  │  @function_tool            │  │  │                    │  │
│  │  call_nivora_agent():      │  │  │                    │  │
│  │    nivora = NivoraAgent()  │  │  │                    │  │
│  │    await nivora.switch_    │  │  │                    │  │
│  │          voice() ──────────┼──┼──┼────┐               │  │
│  │    return nivora           │  │  │    │               │  │
│  └────────────────────────────┘  │  └────┴───────────────┘  │
│                                  │       │                  │
│                                  │       │                  │
│    GenericAgent.switch_voice():  │       │                  │
│      new_tts = elevenlabs.TTS(   │       │                  │
│        voice_id=self.voice_id    │       │                  │
│      )                            │       │                  │
│      session._tts = new_tts ─────┴───────┘                  │
│                                                              │
│  Now session uses Nivora's voice for next synthesis!        │
└──────────────────────────────────────────────────────────────┘
```

---

## Complete Data Flow

```
    USER INPUT (Voice)
           ↓
    [Sarvam STT]
           ↓
    "Check my calendar"
           ↓
    ┌──────────────┐
    │ Chat Context │
    └──────┬───────┘
           ↓
    ┌──────────────┐
    │  Infin Agent │
    │  LLM decides │
    └──────┬───────┘
           ↓
    ┌──────────────────────┐
    │ google_calendar_list │
    │      (tool)          │
    └──────┬───────────────┘
           ↓
    [Tool executes]
           ↓
    "3 meetings tomorrow"
           ↓
    ┌──────────────┐
    │ Chat Context │
    │ + tool result│
    └──────┬───────┘
           ↓
    [Infin LLM generates]
           ↓
    "You have 3 meetings..."
           ↓
    [ElevenLabs TTS - Infin voice]
           ↓
    USER HEARS RESPONSE

───────────────────────────

    USER INPUT (Voice)
           ↓
    [Sarvam STT]
           ↓
    "Debug this Python error"
           ↓
    ┌──────────────┐
    │ Chat Context │
    └──────┬───────┘
           ↓
    ┌──────────────┐
    │  Infin Agent │
    │  LLM decides │
    └──────┬───────┘
           ↓
    ┌──────────────────────┐
    │ call_nivora_agent()  │
    │ topic="debug Python" │
    └──────┬───────────────┘
           ↓
    ┌──────────────────┐
    │ Create Nivora    │
    │ Switch voice     │
    │ Pass chat_ctx    │
    └──────┬───────────┘
           ↓
    ┌──────────────┐
    │ Nivora Agent │
    │ entry_topic  │
    └──────┬───────┘
           ↓
    ┌──────────────────────┐
    │ describe_screen_share│
    │ "What error shown?"  │
    └──────┬───────────────┘
           ↓
    [Screen Share Buffer]
           ↓
    [AWS Nova Vision API]
           ↓
    "NameError on line 47"
           ↓
    ┌──────────────┐
    │ Chat Context │
    │ + vision res │
    └──────┬───────┘
           ↓
    [Nivora LLM generates]
           ↓
    "I see the error..."
           ↓
    [ElevenLabs TTS - Nivora voice]
           ↓
    USER HEARS RESPONSE
```

---

## Key Components Summary

| Component | Purpose | Location |
|-----------|---------|----------|
| `InfinAgent` | Life management persona | multi_agent_livekit.py |
| `NivoraAgent` | Technical persona | multi_agent_livekit.py |
| `GenericAgent` | Base class with voice switching | generic_agent.py |
| `start_frame_capture()` | Captures screen frames | screen_share.py |
| `describe_screen_share()` | Vision tool | tools.py |
| `analyze_screen()` | AWS Nova vision | computer_use.py |
| `_setup_screen_share_tracking()` | Auto-detect shares | multi_agent_livekit.py |
| `ChatContext` | Shared conversation history | LiveKit Agents SDK |
| `elevenlabs.TTS` | Voice synthesis | LiveKit ElevenLabs plugin |

---

**The system is complete and production-ready!** 🎉

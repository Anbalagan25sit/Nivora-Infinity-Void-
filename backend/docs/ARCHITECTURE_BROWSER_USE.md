# Browser-Use Agent System Architecture

## High-Level Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│                        USER (Voice Command)                          │
│   "Solve my differential equations course"                          │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     NIVORA VOICE AGENT                               │
│  (multi_agent_livekit.py)                                           │
│  - Receives voice via LiveKit                                       │
│  - Transcribes with Groq Whisper                                    │
│  - Routes to NivoraAgent                                            │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                   NIVORA AGENT (Technical)                           │
│  - LLM: AWS Bedrock Nova Pro                                        │
│  - Recognizes intent: "E-Box problem solving"                       │
│  - Calls tool: solve_ebox_differential_equations()                  │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│              BROWSER-USE TOOL (browser_use_tools.py)                 │
│  @function_tool                                                      │
│  async def solve_ebox_differential_equations(...):                   │
│      - Validates parameters                                          │
│      - Creates EBoxConfig                                            │
│      - Initializes EBoxBrowserAgent                                  │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│          BROWSER-USE AGENT (browser_use_agent.py)                    │
│  class EBoxBrowserAgent:                                             │
│      - Initialize Browser (Playwright/Chromium)                      │
│      - Initialize LLM (Claude/GPT-4)                                 │
│      - Build comprehensive task description                          │
│      - Create browser-use Agent instance                             │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│              BROWSER-USE LIBRARY (Autonomous Loop)                   │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │ OBSERVE → REASON → ACT → VALIDATE → REPEAT                     │ │
│  └────────────────────────────────────────────────────────────────┘ │
│                                                                      │
│  Step 1: OBSERVE                                                     │
│    - Take screenshot                                                 │
│    - Read DOM structure                                              │
│    - Extract visible text                                            │
│                                                                      │
│  Step 2: REASON (LLM)                                                │
│    - Analyze current state                                           │
│    - Understand task progress                                        │
│    - Decide next action                                              │
│    - Plan multi-step sequence if needed                              │
│                                                                      │
│  Step 3: ACT (Playwright)                                            │
│    - Click elements                                                  │
│    - Type text                                                       │
│    - Navigate pages                                                  │
│    - Submit forms                                                    │
│                                                                      │
│  Step 4: VALIDATE                                                    │
│    - Check action succeeded                                          │
│    - Verify expected outcome                                         │
│    - Detect errors                                                   │
│    - Adjust if needed                                                │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    E-BOX PLATFORM INTERACTION                        │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │ 1. Login                                                      │  │
│  │    - Navigate to pro.e-box.co.in/login                       │  │
│  │    - Fill username: SIT25CS170                               │  │
│  │    - Fill password: SIT25CS170                               │  │
│  │    - Click submit                                             │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                             ↓                                        │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │ 2. Navigate to Course                                         │  │
│  │    - Find "Differential Equations..." link                    │  │
│  │    - Click course link                                        │  │
│  │    - Wait for course page to load                             │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                             ↓                                        │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │ 3. Process i-Learn Section                                    │  │
│  │    - Click "i-Learn" tab                                      │  │
│  │    - For each Topic in sidebar:                               │  │
│  │      • Click topic name                                       │  │
│  │      • Read problem description                               │  │
│  │      • Apply differential equation theory                     │  │
│  │      • Generate/select solution                               │  │
│  │      • Submit answer                                          │  │
│  │      • Move to next problem                                   │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                             ↓                                        │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │ 4. Process i-Analyse Section                                  │  │
│  │    - Click "i-Analyse" tab                                    │  │
│  │    - Repeat problem-solving process                           │  │
│  │    - Handle more complex analytical problems                  │  │
│  └──────────────────────────────────────────────────────────────┘  │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                  DIFFERENTIAL EQUATION SOLVING                       │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │ First-Order ODEs                                              │  │
│  │   y' + P(x)y = Q(x)                                           │  │
│  │   → Integrating factor: μ(x) = e^(∫P(x)dx)                   │  │
│  │   → Solution: y = (1/μ) * ∫μQ(x)dx + C                       │  │
│  └──────────────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │ Second-Order ODEs                                             │  │
│  │   y'' + py' + qy = 0                                          │  │
│  │   → Characteristic equation: r² + pr + q = 0                  │  │
│  │   → Solve for roots, construct solution:                      │  │
│  │     • Real distinct: y = c₁e^(r₁x) + c₂e^(r₂x)               │  │
│  │     • Repeated: y = (c₁ + c₂x)e^(rx)                          │  │
│  │     • Complex: y = e^(αx)(c₁cos(βx) + c₂sin(βx))             │  │
│  └──────────────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │ Partial Differential Equations                                │  │
│  │   → Separation of variables                                   │  │
│  │   → Apply boundary conditions                                 │  │
│  │   → Construct series solution if needed                       │  │
│  └──────────────────────────────────────────────────────────────┘  │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    RESULT AGGREGATION                                │
│  - Total problems attempted                                          │
│  - Total problems solved                                             │
│  - Accuracy percentage                                               │
│  - Time taken                                                        │
│  - Sections completed                                                │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    RESPONSE TO USER                                  │
│  Nivora: "✅ Completed! Solved 45 problems in i-Learn and           │
│          i-Analyse. Accuracy: 92%. The agent autonomously            │
│          navigated E-Box and applied differential equation           │
│          theory to solve ODEs, PDEs, and complex analysis."          │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Component Details

### 1. Browser-Use Agent Loop (Detailed)

```
┌────────────────────────────────────────────────────────────────┐
│                    AUTONOMOUS AGENT LOOP                        │
│                                                                 │
│  ┌──────────┐                                                  │
│  │  START   │                                                  │
│  └────┬─────┘                                                  │
│       │                                                         │
│       ▼                                                         │
│  ┌──────────────────────────────────────┐                      │
│  │ OBSERVE PAGE                         │                      │
│  │ • Screenshot (visual)                │                      │
│  │ • DOM tree (structure)               │                      │
│  │ • Visible text (content)             │                      │
│  │ • Interactive elements (buttons, etc)│                      │
│  └──────────┬───────────────────────────┘                      │
│             │                                                   │
│             ▼                                                   │
│  ┌──────────────────────────────────────┐                      │
│  │ REASON WITH LLM                      │                      │
│  │ Prompt:                              │                      │
│  │ "Current page: [description]          │                      │
│  │  Task: Solve differential equations   │                      │
│  │  Progress: [what's been done]         │                      │
│  │  What should I do next?"              │                      │
│  │                                       │                      │
│  │ LLM Response:                         │                      │
│  │ "Click the 'i-Learn' tab to access   │                      │
│  │  the problems section"                │                      │
│  └──────────┬───────────────────────────┘                      │
│             │                                                   │
│             ▼                                                   │
│  ┌──────────────────────────────────────┐                      │
│  │ EXECUTE ACTION                       │                      │
│  │ • Parse LLM decision                 │                      │
│  │ • Find target element                │                      │
│  │ • Perform action (click/type/etc)    │                      │
│  │ • Wait for page to update            │                      │
│  └──────────┬───────────────────────────┘                      │
│             │                                                   │
│             ▼                                                   │
│  ┌──────────────────────────────────────┐                      │
│  │ VALIDATE                             │                      │
│  │ • Did action succeed?                │                      │
│  │ • Is page in expected state?         │                      │
│  │ • Any errors?                        │                      │
│  └──────────┬───────────────────────────┘                      │
│             │                                                   │
│             ▼                                                   │
│       ┌─────────────┐                                          │
│       │ Task Done?  │─── No ───┐                               │
│       └─────┬───────┘          │                               │
│             │ Yes              │                               │
│             ▼                  │                               │
│        ┌─────────┐             │                               │
│        │ RETURN  │             │                               │
│        │ RESULT  │             │                               │
│        └─────────┘             │                               │
│             ▲                  │                               │
│             │                  │                               │
│             └──────────────────┘                               │
│                (Loop back to OBSERVE)                          │
└────────────────────────────────────────────────────────────────┘
```

---

## Data Flow: Voice Command to Solution

```
 1. User speaks: "Solve my differential equations course"
    └─> Audio captured by LiveKit client
        └─> Sent to Nivora agent

 2. Nivora transcribes with Groq Whisper (FREE STT)
    └─> Text: "Solve my differential equations course"
        └─> Sent to AWS Bedrock Nova Pro (LLM)

 3. Nova Pro recognizes intent
    └─> Tool call: solve_ebox_differential_equations(sections="i-Learn,i-Analyse")
        └─> Executes browser_use_tools.py function

 4. Browser-use tool initializes agent
    └─> Creates EBoxBrowserAgent with config
        └─> Starts autonomous browser-use agent

 5. Agent observes E-Box login page
    └─> LLM: "I see a login form. Enter credentials."
        └─> Action: Fill username/password, click submit

 6. Agent observes dashboard
    └─> LLM: "I see course list. Find Differential Equations."
        └─> Action: Click "Differential Equations..." link

 7. Agent observes course page
    └─> LLM: "I see sections. Click i-Learn tab."
        └─> Action: Click "i-Learn" tab

 8. Agent observes problem 1: "Solve dy/dx + 2y = x"
    └─> LLM: "This is first-order ODE. Use integrating factor."
        └─> Calculates: μ(x) = e^(2x)
            └─> Solution: y = (x/2 - 1/4) + Ce^(-2x)
                └─> Action: Enter solution, click submit

 9. Agent repeats for all problems in i-Learn
    └─> Then switches to i-Analyse
        └─> Solves more complex problems
            └─> Continues until all done

10. Agent returns result
    └─> browser_use_tools.py formats response
        └─> Returns to Nivora agent
            └─> Nova Pro generates voice response
                └─> Edge TTS (FREE) synthesizes speech
                    └─> User hears: "Completed! Solved 45 problems..."
```

---

## System Components Hierarchy

```
┌─────────────────────────────────────────────────────────────────┐
│                    NIVORA PROJECT ROOT                          │
└─────────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼──────────────────────┐
        ▼                     ▼                      ▼
┌──────────────┐    ┌──────────────────┐    ┌──────────────┐
│  Frontend    │    │     Backend      │    │ Browser-Use  │
│  (Next.js)   │    │   (LiveKit)      │    │   Agent      │
└──────────────┘    └──────────────────┘    └──────────────┘
                              │                      │
                    ┌─────────┴─────────┐           │
                    ▼                   ▼           ▼
            ┌───────────────┐  ┌───────────────────────┐
            │ Multi-Agent   │  │  browser_use_agent.py │
            │ System        │  │  browser_use_tools.py │
            └───────────────┘  └───────────────────────┘
                    │                      │
        ┌───────────┼────────┐            │
        ▼           ▼        ▼            ▼
┌────────────┐ ┌────────┐ ┌─────┐  ┌──────────────┐
│ InfinAgent │ │ Nivora │ │Tools│  │ browser-use  │
│  (Jarvis)  │ │ Agent  │ │ ... │  │   library    │
└────────────┘ └────────┘ └─────┘  └──────────────┘
                    │                      │
                    └──────────┬───────────┘
                               ▼
                    ┌──────────────────┐
                    │   E-Box Platform │
                    │ pro.e-box.co.in  │
                    └──────────────────┘
```

---

## File Dependencies

```
multi_agent_livekit.py
    ├── browser_use_tools.py
    │   └── browser_use_agent.py
    │       ├── browser_use (library)
    │       ├── langchain
    │       ├── langchain_anthropic
    │       ├── langchain_openai
    │       └── playwright
    │
    ├── tools.py (existing tools)
    ├── prompts.py
    ├── infin_prompts.py
    └── generic_agent.py
```

---

This visual architecture shows how browser-use transforms complex web automation into simple autonomous agent tasks!

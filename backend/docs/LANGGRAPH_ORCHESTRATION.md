# LangGraph Orchestration for Browser-Use Agent

## Overview

This integration adds **LangGraph orchestration** to Nivora's browser-use automation agent, providing:

✅ **Better state management** - Track automation progress through defined phases
✅ **Conditional routing** - Smart retry logic and error handling
✅ **Checkpoints** - Resume long-running tasks if interrupted
✅ **Visibility** - Clear logging of each workflow step
✅ **Claude API integration** - Uses your $100 Anthropic credit efficiently

## Architecture

### LangGraph Workflow Phases

```
START → Initialize → Login → Navigate → Solve → Verify → Finalize → END
           ↓           ↓        ↓         ↓        ↓
        [Retry] ← [Error Handler] ← (conditional routing)
```

**Phase Details:**

1. **Initialize** - Create browser and browser-use agent
2. **Login** - Authenticate to E-Box platform
3. **Navigate** - Find and open the course
4. **Solve** - Autonomously solve differential equation problems
5. **Verify** - Check completion status
6. **Finalize** - Clean up and return results

### State Management

LangGraph tracks this state throughout execution:

```python
{
    "task_phase": "login|navigate|solve|verify|complete",
    "problems_solved": int,
    "problems_failed": int,
    "current_section": "i-Learn|i-Analyse",
    "errors": list,
    "success_messages": list,
    "retry_count": int
}
```

### Conditional Routing

The workflow makes intelligent decisions:

- **After Login/Navigate/Solve**: Retry on error (up to 3 times) or continue
- **After Verify**: Move to next section or finalize if all complete
- **On Error**: Route to error handler, then finalize

## Files Added

### 1. `browser_use_langgraph.py`
Main LangGraph workflow implementation:
- `EBoxLangGraphAgent` - Orchestrated agent class
- `AgentState` - TypedDict for state schema
- `_build_graph()` - Constructs LangGraph workflow
- Node functions for each phase

### 2. `browser_use_langgraph_tools.py`
LiveKit integration tools:
- `solve_ebox_course_langgraph()` - Full course automation
- `solve_ebox_section_langgraph()` - Specific section automation

### 3. Updated Files
- `.env` - Added `ANTHROPIC_API_KEY` with documentation
- `requirements.txt` - Added `langgraph>=0.2.0` and `langgraph-checkpoint>=2.0.0`
- `multi_agent_livekit.py` - Integrated LangGraph tools into Nivora

## Setup

### 1. Install Dependencies

```bash
cd "Nivora-Ver-loop-main"
pip install langgraph langgraph-checkpoint langchain-anthropic
```

### 2. Verify API Key

Check `.env` file has:

```env
# ── Anthropic Claude API ──────────────────────────────────────────────────
# Used by browser-use agent for autonomous E-Box automation
# Get free $100 credit at console.anthropic.com
# Model: Claude 3.5 Sonnet (best for reasoning & web automation)
ANTHROPIC_API_KEY=sk-ant-api03-xxxxx
```

### 3. Test Standalone

```bash
python browser_use_langgraph.py
```

Expected output:
```
[LangGraph] 🚀 Starting orchestrated E-Box automation
[LangGraph] 📋 PHASE: Initialize
[LangGraph] ✅ Initialization complete
[LangGraph] 🔐 PHASE: Login
[LangGraph] ✅ Login complete
[LangGraph] 🧭 PHASE: Navigate to Differential Equations...
[LangGraph] ✅ Navigation complete
[LangGraph] 🧮 PHASE: Solve problems in i-Learn
[LangGraph] ✅ Solved problems in i-Learn
...
```

## Voice Commands

Once integrated into Nivora, use these voice commands:

### Full Course Automation (LangGraph)
- "Solve my differential equations course using LangGraph"
- "Use orchestration to complete E-Box"
- "Run the advanced agent on my course"

### Section-Specific (LangGraph)
- "Solve i-Learn section with LangGraph"
- "Use orchestration to complete i-Analyse"

### Compare to Original Browser-Use
- "Solve my differential equations course" (uses original browser-use)
- "Complete unit 3" (uses original browser-use)

## Advantages Over Original Browser-Use

| Feature | Original Browser-Use | LangGraph Orchestration |
|---------|---------------------|------------------------|
| **State Tracking** | Implicit | Explicit phases |
| **Error Handling** | Basic try/catch | Conditional retry logic |
| **Visibility** | Agent actions only | Phase-by-phase logging |
| **Resume** | Not supported | Checkpoint support |
| **Control Flow** | Linear | Conditional routing |
| **Debugging** | Hard to trace | Clear state inspection |

## Cost Tracking

### Using Claude API ($100 credit)

**Estimated costs per E-Box session:**
- Login + Navigate: ~2K tokens ($0.006)
- Solve i-Learn: ~15K tokens ($0.045)
- Solve i-Analyse: ~15K tokens ($0.045)
- **Total per session: ~$0.10**

**Your $100 credit = ~1000 E-Box sessions!**

### Token Optimization

LangGraph reduces token usage by:
- Breaking tasks into smaller prompts (login, navigate, solve separately)
- Only retrying failed phases (not entire workflow)
- Reusing context across phases

## Logging & Monitoring

### Log Levels

```python
[LangGraph] 📋 PHASE: Initialize  # Phase start
[LangGraph] ✅ Login complete      # Success
[LangGraph] 🔄 Retrying... (1/3)   # Retry
[LangGraph] ❌ Max retries exceeded # Failure
[LangGraph] 🏁 PHASE: Finalize     # Cleanup
```

### State Inspection

Access current state at any time:

```python
async for state in agent.graph.astream(initial_state, config):
    print(state["task_phase"])
    print(state["problems_solved"])
    print(state["errors"])
```

## Checkpointing (Advanced)

LangGraph includes checkpoint support for resuming interrupted workflows:

```python
# The workflow auto-saves checkpoints to MemorySaver
config = {"configurable": {"thread_id": "ebox_session_1"}}

# If interrupted, resume with same thread_id:
result = await agent.graph.astream(state, config)
```

For persistent checkpoints, replace `MemorySaver` with `SqliteSaver`:

```python
from langgraph.checkpoint.sqlite import SqliteSaver

memory = SqliteSaver.from_conn_string(":memory:")
graph = workflow.compile(checkpointer=memory)
```

## Troubleshooting

### "ANTHROPIC_API_KEY not found"
- Check `.env` file has the key
- Restart your terminal/IDE after adding the key
- Verify with: `python -c "import os; from dotenv import load_dotenv; load_dotenv(); print(os.getenv('ANTHROPIC_API_KEY'))"`

### "ModuleNotFoundError: No module named 'langgraph'"
```bash
pip install langgraph langgraph-checkpoint
```

### "Rate limit exceeded"
- Free tier has 5 requests/min limit
- LangGraph breaks work into phases, so each phase is a separate request
- Add delays between phases or upgrade to paid tier

### Browser doesn't open
- Check `headless=False` in config for debugging
- Verify Playwright is installed: `python -m playwright install chromium`

### Agent gets stuck in retry loop
- Check max_retries setting (default: 3)
- Look at error messages in logs
- May need to adjust task prompts for clarity

## Integration with Multi-Agent System

LangGraph tools are available to **Nivora** (technical agent):

```python
# In multi_agent_livekit.py
NIVORA_TOOLS = [
    # ... other tools ...
    solve_ebox_course_langgraph,      # Full course
    solve_ebox_section_langgraph,     # Specific section
]
```

When you ask Nivora to "solve my E-Box course with orchestration", it will:
1. Call `solve_ebox_course_langgraph()`
2. LangGraph creates workflow graph
3. Executes phases: Initialize → Login → Navigate → Solve → Verify → Finalize
4. Returns summary to Nivora
5. Nivora speaks the result to you

## Future Enhancements

Possible improvements:
- Add human-in-the-loop approval for each phase
- Persist checkpoints to database for multi-day sessions
- Add parallel section solving (i-Learn and i-Analyse simultaneously)
- Integrate with Notion for progress tracking
- Add email notifications on completion/errors

## Credits

- **LangGraph**: https://github.com/langchain-ai/langgraph
- **browser-use**: https://github.com/browser-use/browser-use
- **Claude API**: https://console.anthropic.com

---

**Built for Nivora AI Assistant** - Making E-Box automation smarter with orchestration! 🚀

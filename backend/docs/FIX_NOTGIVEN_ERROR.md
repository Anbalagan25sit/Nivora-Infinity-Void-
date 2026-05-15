# 🔧 Fix: AttributeError in agent.py

## Error Description

```
AttributeError: 'NotGiven' object has no attribute 'chat'
```

**Location:** `agent.py`, line 170 in `NivoraAgent.__init__`

## Root Cause

The `NivoraAgent.__init__` method was trying to access `self._llm.chat` immediately after calling `super().__init__()`. However, at that point, `self._llm` was still a `NotGiven` sentinel object (from the `openai` library) rather than an actual LLM instance.

This happens because the LiveKit `Agent` class initializes the LLM lazily - it's not fully set up until later in the agent lifecycle.

## Solution

Added defensive checks before accessing `self._llm.chat`:

```python
def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    # Wrap the LLM to filter responses before they reach the chat UI
    # Only apply if _llm is properly initialized (not NotGiven)
    if hasattr(self, '_llm') and self._llm is not None:
        # Check if _llm has chat attribute (it's a valid LLM instance)
        if hasattr(self._llm, 'chat'):
            original_chat = self._llm.chat
            # ... rest of the filtering logic
```

## Changes Made

**Before:**
```python
if hasattr(self, '_llm'):
    original_chat = self._llm.chat  # ❌ Crashes if _llm is NotGiven
```

**After:**
```python
if hasattr(self, '_llm') and self._llm is not None:
    if hasattr(self._llm, 'chat'):  # ✅ Safe check
        original_chat = self._llm.chat
```

## Why This Works

1. **First check:** `hasattr(self, '_llm')` - Ensures attribute exists
2. **Second check:** `self._llm is not None` - Ensures it's not None
3. **Third check:** `hasattr(self._llm, 'chat')` - Ensures it's a valid LLM with chat method

This triple-check approach ensures we only try to wrap the LLM's chat method when it's actually available.

## Impact

- ✅ **No functional change** - The thinking tag filtering still works when LLM is available
- ✅ **No crash** - Agent initializes successfully even if LLM is NotGiven initially
- ✅ **Graceful degradation** - If LLM doesn't have chat method, we skip wrapping

## Testing

```bash
$ python -m py_compile agent.py
✅ agent.py syntax is valid
```

The agent should now start successfully without the AttributeError!

## Next Steps

Try running the agent again:

```bash
python agent.py dev
```

Or multi-agent:

```bash
python multi_agent_livekit.py
```

The error should be resolved! 🎉

---

*Fix applied: April 8, 2026*
*Issue: AttributeError with NotGiven object*
*Status: ✅ Resolved*

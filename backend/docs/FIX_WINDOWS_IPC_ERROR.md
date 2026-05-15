# Windows IPC Error Fix

## Error Details
```
ERROR livekit.agents Error in _read_ipc_task
asyncio.exceptions.IncompleteReadError: 0 bytes read on a total of 4 expected bytes
livekit.agents.utils.aio.duplex_unix.DuplexClosed
```

## Root Cause
The LiveKit CLI `dev` mode uses **Unix-style IPC (Inter-Process Communication)** for hot-reloading, which doesn't work on Windows. The file watcher tries to communicate between processes using Unix pipes, causing `DuplexClosed` errors.

## ✅ Solution: Use `start` Instead of `dev`

### Quick Fix
```bash
# ❌ DON'T use this on Windows:
python agent.py dev

# ✅ USE this instead:
python agent.py start
```

### Or Use the Batch Script
```bash
# Just double-click or run:
start-agent.bat
```

---

## Comparison: `dev` vs `start`

| Mode | Hot Reload | Windows Compatible | Best For |
|------|------------|-------------------|----------|
| `dev` | ✅ Yes | ❌ No (IPC errors) | Linux/Mac development |
| `start` | ❌ No | ✅ Yes | Windows, production |

---

## Alternative: Direct Python Execution

If `python agent.py start` doesn't work, run directly:

```bash
cd "Nivora-Ver-loop-main"
venv\Scripts\activate
python -m livekit.agents.cli start
```

---

## For Development on Windows

If you need hot-reload (auto-restart on code changes), use **nodemon** or **watchdog**:

### Option 1: Use nodemon (Node.js)
```bash
# Install nodemon globally
npm install -g nodemon

# Watch Python files and restart
nodemon --watch . --ext py --exec "python agent.py start"
```

### Option 2: Use watchdog (Python)
```bash
pip install watchdog

# Create watch script
watchmedo auto-restart --patterns="*.py" --recursive -- python agent.py start
```

---

## Permanent Fix (For Developers)

If you want `dev` mode to work on Windows, you need to patch LiveKit:

### File: `venv\Lib\site-packages\livekit\agents\cli\watcher.py`

Around line 136, wrap in try-except:

```python
async def _read_ipc_task(self):
    try:
        msg = await channel.arecv_message(self._pch, proto.IPC_MESSAGES)
        # ... rest of code
    except DuplexClosed:
        # IPC channel closed (expected on Windows)
        logger.debug("IPC channel closed - this is expected on Windows")
        return
```

**But this is not recommended** - just use `start` mode instead.

---

## Summary

**Problem:** Windows doesn't support Unix IPC used by `dev` mode

**Solution:** Use `start` mode or the provided `start-agent.bat`

**For Hot Reload:** Use nodemon or watchdog instead

---

**Status:** This is a known limitation, not a bug in your setup!
**Works on:** ✅ Linux, ✅ macOS, ❌ Windows `dev` mode
**Workaround:** ✅ Use `start` mode on Windows

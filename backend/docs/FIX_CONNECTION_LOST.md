# Fix: Connection Lost Error (WinError 64)

## Error Details
```
ConnectionError: Connection lost
aiohttp.client_exceptions.ClientOSError: [WinError 64]
The specified network name is no longer available
```

## Root Cause
This is a **Windows network instability issue** with WebSocket connections. Common causes:
1. Windows Firewall blocking persistent connections
2. Network adapter power saving
3. Antivirus interfering with WebSocket
4. IPv6/IPv4 conflicts
5. LiveKit connection timeout

---

## Quick Fixes (Try in Order)

### Fix 1: Allow Python Through Firewall ⭐ (Most Common)

**Windows Firewall is likely blocking the persistent LiveKit connection.**

```powershell
# Run PowerShell as Administrator, then:

# Allow Python (all profiles)
New-NetFirewallRule -DisplayName "Python LiveKit" -Direction Inbound -Program "C:\Users\Nivorichi\AppData\Local\Programs\Python\Python313\python.exe" -Action Allow

New-NetFirewallRule -DisplayName "Python LiveKit Outbound" -Direction Outbound -Program "C:\Users\Nivorichi\AppData\Local\Programs\Python\Python313\python.exe" -Action Allow
```

**Or via GUI:**
1. Windows Security → Firewall & network protection
2. Advanced settings
3. Inbound Rules → New Rule
4. Program → Browse to Python.exe
5. Allow the connection
6. Repeat for Outbound Rules

---

### Fix 2: Disable Network Adapter Power Saving

**Windows might be turning off your network adapter to save power.**

1. Open **Device Manager** (Win + X → Device Manager)
2. Expand **Network adapters**
3. Right-click your adapter (Wi-Fi or Ethernet)
4. Properties → Power Management tab
5. **Uncheck** "Allow the computer to turn off this device to save power"
6. Click OK

---

### Fix 3: Disable Antivirus WebSocket Scanning

**Antivirus can block WebSocket connections:**

**For Windows Defender:**
1. Windows Security → Virus & threat protection
2. Manage settings
3. Add exclusion → Folder
4. Add: `C:\Users\Nivorichi\Downloads\Nivora infinity void\Nivora-Ver-loop-main`

**For Third-Party Antivirus:**
- Temporarily disable to test
- Add Python.exe to exclusions

---

### Fix 4: Use HTTP/1.1 Instead of HTTP/2

**Some Windows network stacks have issues with HTTP/2 WebSockets.**

Edit `agent.py` and add this near the top:

```python
import os
os.environ['AIOHTTP_NO_EXTENSIONS'] = '1'  # Disable HTTP/2
```

**Full change:**
```python
# At line 28-38 (after imports, before logging setup)
import os
import asyncio
import re
import httpx

# FIX: Disable HTTP/2 for better Windows compatibility
os.environ['AIOHTTP_NO_EXTENSIONS'] = '1'
os.environ['AIOHTTP_CONNECTOR_LIMIT'] = '100'

# Keep thread counts low to avoid OOM on resource-constrained machines
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
```

---

### Fix 5: Increase Connection Timeout

**The default timeout might be too aggressive.**

Edit `agent.py` around line 204-223 (the `AgentSession` creation):

```python
# Build the AgentSession with AWS Nova Pro, Sarvam STT, and FREE Edge TTS
session = AgentSession(
    vad=silero.VAD.load(min_silence_duration=1.5),
    # Sarvam STT
    stt=sarvam.STT(
        language="en-IN",
        model="saaras:v3",
        mode="transcribe",
    ),
    # AWS Bedrock Nova Pro
    llm=aws.LLM(
        model=AWS_BEDROCK_MODEL,
        region=AWS_REGION,
        temperature=0.8,
    ),
    # FREE TTS: Microsoft Edge Neural Voices (no API key needed!)
    tts=edge_tts_plugin.TTS(
        voice="en-US-AriaNeural",
    ),
    mcp_servers=mcp_servers,
    # ADD THESE:
    timeout=120,  # Increase connection timeout to 120 seconds
)
```

---

### Fix 6: Use wss:// with Port Explicitly

**Sometimes Windows needs explicit port specification.**

In `.env`, change:
```env
# Before
LIVEKIT_URL=wss://your-project.livekit.cloud

# After (add explicit port)
LIVEKIT_URL=wss://your-project.livekit.cloud:443
```

---

### Fix 7: Check Network Stability

**Test if it's your internet connection:**

```bash
# Continuous ping to LiveKit server
ping -t your-project.livekit.cloud

# Watch for packet loss or high latency
```

If you see packet loss > 1% or ping > 200ms, your internet is unstable.

---

## Complete Fix Script (PowerShell as Admin)

```powershell
# Run this as Administrator to apply all Windows fixes

# 1. Allow Python through firewall
$pythonPath = "C:\Users\Nivorichi\AppData\Local\Programs\Python\Python313\python.exe"
New-NetFirewallRule -DisplayName "Python LiveKit In" -Direction Inbound -Program $pythonPath -Action Allow -Force
New-NetFirewallRule -DisplayName "Python LiveKit Out" -Direction Outbound -Program $pythonPath -Action Allow -Force

# 2. Disable network adapter power saving
$adapters = Get-NetAdapter | Where-Object {$_.Status -eq "Up"}
foreach ($adapter in $adapters) {
    $key = "HKLM:\SYSTEM\CurrentControlSet\Control\Class\{4d36e972-e325-11ce-bfc1-08002be10318}\*"
    Get-ChildItem $key | ForEach-Object {
        if ((Get-ItemProperty $_.PSPath).DriverDesc -eq $adapter.InterfaceDescription) {
            Set-ItemProperty -Path $_.PSPath -Name "PnPCapabilities" -Value 24 -Force
        }
    }
}

# 3. Flush DNS and reset network
ipconfig /flushdns
netsh winsock reset

Write-Host "Network fixes applied. Restart your computer for full effect."
```

---

## Alternative: Use Local Network Mode

If nothing works, try connecting via localhost instead of cloud:

### Option 1: Run LiveKit Locally

```bash
# Install LiveKit locally with Docker
docker run --rm -p 7880:7880 -p 7881:7881 -p 7882:7882/udp livekit/livekit-server --dev

# Update .env to use local server
LIVEKIT_URL=ws://localhost:7880
```

### Option 2: Use ngrok Tunnel

```bash
# If cloud won't work, tunnel through ngrok
ngrok tcp 7880

# Use the ngrok URL in .env
```

---

## Testing the Fix

After applying fixes:

1. **Restart Windows** (important for network changes)

2. **Test the agent:**
```bash
cd "Nivora-Ver-loop-main"
python agent.py dev
```

3. **Watch for these logs:**
```
INFO     Connected to LiveKit room.
INFO     AgentSession started successfully.
```

4. **No more "Connection lost" errors?** ✅ Fixed!

---

## Still Not Working?

### Check Windows Event Viewer

1. Win + R → `eventvwr`
2. Windows Logs → System
3. Filter by "Network" or "TCP/IP"
4. Look for errors around the time of disconnect

### Enable Debug Logging

Add to top of `agent.py`:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

This will show exactly where the connection drops.

---

## Summary

**Most Likely Solution:** Fix 1 (Windows Firewall)

**Quick Test:**
1. Temporarily disable Windows Firewall
2. Run agent
3. If it works → Add Python firewall rule
4. If doesn't work → Try Fix 2-7

**Nuclear Option:**
Use local LiveKit server with Docker (100% reliable)

---

**Created:** 2026-04-07
**Status:** Firewall is most common cause on Windows

# LiveKit Playground Connection Troubleshooting

## Common Issues & Solutions

### Issue 1: Agent Not Showing Up in Playground

**Symptoms:**
- Agent starts but doesn't appear in LiveKit Agents Playground
- Playground shows "No agents available"

**Solution:**

1. **Check if agent is running in dev mode:**
   ```bash
   cd "Nivora-Ver-loop-main"
   python agent.py dev
   ```

2. **Verify LiveKit credentials in `.env`:**
   ```env
   LIVEKIT_URL="wss://xxxxxxxx.livekit.cloud"
   LIVEKIT_API_KEY="your_api_key_here"
   LIVEKIT_API_SECRET="your_api_secret_here"
   ```

3. **Check agent logs for connection errors:**
   - Look for `"Connected to LiveKit room"`
   - Check for authentication errors

---

### Issue 2: "Connection Failed" in Playground

**Symptoms:**
- Playground UI loads but connection fails
- Error: "Failed to connect to agent"

**Possible Causes:**

1. **Agent not running**
   - Solution: Start agent with `python agent.py dev`

2. **Wrong LiveKit URL**
   - Solution: Verify URL matches in both `.env` and playground settings

3. **API Key mismatch**
   - Solution: Use same API key/secret for both agent and playground

---

### Issue 3: Agent Connects but No Audio

**Symptoms:**
- Visual connection established
- No voice input/output

**Solutions:**

1. **Check microphone permissions:**
   - Browser needs microphone access
   - Check browser settings

2. **Verify STT configuration:**
   ```python
   # In agent.py, check:
   stt=sarvam.STT(
       language="en-IN",
       model="saaras:v3",
       mode="transcribe",
   )
   ```

3. **Check GROQ_API_KEY in `.env`:**
   ```env
   GROQ_API_KEY=XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
   ```

---

### Issue 4: "AWS Bedrock Error"

**Symptoms:**
- Agent starts but crashes when responding
- Error: "bedrock:InvokeModel permission denied"

**Solutions:**

1. **Verify AWS credentials:**
   ```env
   AWS_ACCESS_KEY_ID=XXXXXXXXXXXXXXXXXXXXXXXXX
   AWS_SECRET_ACCESS_KEY=XXXXXXXXXXXXXXXXXXXXXXXXX
   AWS_REGION=XXXXXXX
   AWS_BEDROCK_MODEL=amazon.nova-pro-v1:0
   ```

2. **Enable Nova Pro in AWS Console:**
   - Go to AWS Bedrock console
   - Navigate to "Model access"
   - Enable `amazon.nova-pro-v1:0`

3. **Check IAM permissions:**
   - User needs `bedrock:InvokeModel` permission

---

## How to Connect to Playground

### Step 1: Start the Agent

```bash
cd "C:\Users\Nivorichi\Downloads\Nivora infinity void\Nivora-Ver-loop-main"
python agent.py dev
```

**Expected output:**
```
INFO     Agent entrypoint starting — room: ...
INFO     AWS credential check passed.
INFO     Connected to LiveKit room.
INFO     AgentSession created — MCP servers: 1
INFO     Total tools available: 120+
INFO     AgentSession started successfully.
```

---

### Step 2: Open LiveKit Playground

**Option A: LiveKit Cloud Playground**
1. Go to https://cloud.livekit.io/
2. Navigate to your project: `your-project-id`
3. Click "Agents Playground"

**Option B: Local Playground**
1. Open https://agents-playground.livekit.io/
2. Enter your LiveKit URL: `wss://your-project.livekit.cloud`
3. Enter API Key: `your_api_key_here`
4. Enter API Secret: `your_api_secret_here`

---

### Step 3: Connect

1. Click "Connect" in playground
2. Allow microphone access
3. Wait for agent to join
4. Start speaking!

---

## Using the Web Chat Instead

If playground isn't working, use the web chat interface:

### Step 1: Start Token Server

```bash
cd "Nivora-Ver-loop-main/Nivora-web-page"
python token-server-ultimate.py
```

### Step 2: Start Agent

```bash
cd "Nivora-Ver-loop-main"
python agent.py dev
```

### Step 3: Open Chat Page

1. Open `Nivora-web-page/chat.html` in browser
2. Click microphone button or type message
3. Chat with Nivora!

---

## Debugging Commands

### Check if agent is running:
```bash
ps aux | grep agent.py
```

### View agent logs in real-time:
```bash
python agent.py dev 2>&1 | tee agent.log
```

### Test LiveKit connection:
```bash
curl https://your-project.livekit.cloud
```

### Verify AWS credentials:
```bash
aws bedrock list-foundation-models --region us-east-1
```

---

## Common Error Messages

| Error | Cause | Solution |
|-------|-------|----------|
| `ConnectionError: Failed to connect` | Agent not running | Start with `python agent.py dev` |
| `ValidationException: bedrock` | AWS config issue | Check AWS credentials & region |
| `STT failed` | GROQ_API_KEY missing | Add to `.env` |
| `No audio` | Mic permissions | Allow browser mic access |
| `Agent not found` | Wrong room/URL | Verify LiveKit URL matches |

---

## Full Startup Sequence

```bash
# 1. Activate venv
cd "Nivora-Ver-loop-main"
venv\Scripts\activate

# 2. Start agent in dev mode
python agent.py dev

# 3. Open playground or web chat
# Playground: https://cloud.livekit.io/
# Web chat: open Nivora-web-page/chat.html
```

---

## Need More Help?

**Check logs for specific errors:**
```bash
python agent.py dev 2>&1 | grep -i "error\|warning\|failed"
```

**Verify all dependencies:**
```bash
pip install -r requirements.txt
```

**Test individual components:**
```bash
# Test AWS
python -c "import boto3; print(boto3.client('bedrock-runtime', region_name='us-east-1'))"

# Test Edge TTS
edge-tts --text "Hello" --write-media test.mp3

# Test LiveKit SDK
python -c "from livekit import api; print('LiveKit SDK OK')"
```

---

**Last Updated:** 2026-04-07
**Status:** All credentials verified in `.env`

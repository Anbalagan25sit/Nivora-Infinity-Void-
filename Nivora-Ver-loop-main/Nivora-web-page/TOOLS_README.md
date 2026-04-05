# Nivora Web Chat - ENHANCED WITH TOOLS 🛠️

## Overview

The Nivora web chat interface now has **full tool support** with beautiful animations! When you ask Nivora to search the web, check weather, or perform calculations, you'll see animated indicators showing which tools are being used.

## 🎨 Features

### Available Tools

1. **🔍 Web Search** - Search the web using DuckDuckGo
   - Example: *"Search for latest news about AI"*
   - Example: *"Find information about quantum computing"*

2. **🌤️ Weather** - Get current weather for any city
   - Example: *"What's the weather in Tokyo?"*
   - Example: *"Tell me the weather in London"*

3. **🌐 Open Website** - Open websites in your browser
   - Example: *"Open YouTube"*
   - Example: *"Open https://github.com"*

4. **⏰ Current Time** - Get current date and time
   - Example: *"What time is it?"*
   - Example: *"What's today's date?"*

5. **🔢 Calculate** - Perform mathematical calculations
   - Example: *"Calculate 15% of 240"*
   - Example: *"What's (10 * 5) / 2?"*

### Beautiful Tool Animations

When Nivora uses a tool, you'll see:
- ✨ **Animated tool icon** with pulsing effect
- 🔄 **Expanding rings** showing activity
- ✅ **Completion checkmark** when done
- 🎨 **Color-coded indicators** for each tool type

## 🚀 How to Run

### 1. Install Dependencies

First, make sure you have the required Python packages:

```bash
pip install flask flask-cors livekit duckduckgo-search requests python-dotenv
```

### 2. Configure AWS Credentials

Make sure your `.env` file has AWS credentials:

```env
AWS_ACCESS_KEY_ID=your_key_here
AWS_SECRET_ACCESS_KEY=your_secret_here
AWS_REGION=us-east-1
AWS_BEDROCK_MODEL=amazon.nova-pro-v1:0
```

### 3. Start the Enhanced Server

```bash
cd Nivora-web-page
python token-server-enhanced.py
```

You should see:

```
============================================================
  Nivora Token & Chat Server (ENHANCED WITH TOOLS)
============================================================
  LiveKit URL: wss://nivora-5opea2lo.livekit.cloud
  AWS Bedrock: ✓ Configured
  Tools Available: 5
    - web_search (DuckDuckGo)
    - get_weather (wttr.in)
    - open_website (Browser)
    - get_current_time
    - calculate
------------------------------------------------------------
  Endpoints:
    POST /api/livekit-token  - Get LiveKit token (voice)
    POST /api/chat           - Text-to-text chat WITH TOOLS
    POST /api/chat/clear     - Clear chat history
    GET  /health             - Health check
============================================================
```

### 4. Open the Chat Interface

Open `chat.html` in your browser (or serve it via a local server):

```bash
# Option 1: Direct file access
open chat.html

# Option 2: Python HTTP server
python -m http.server 8080
# Then visit: http://localhost:8080/chat.html
```

## 💬 Example Conversations

### Example 1: Web Search
**You:** "Search for the latest news about SpaceX"

**Nivora:**
- 🔍 *[Animated web_search tool appears]*
- *Shows search results with links and descriptions*

### Example 2: Weather Check
**You:** "What's the weather like in Paris?"

**Nivora:**
- 🌤️ *[Animated get_weather tool appears]*
- "Weather in Paris:
  🌡️ 15°C (feels like 13°C)
  ☁️ Partly cloudy
  💧 Humidity: 65%
  🌬️ Wind: 12 km/h"

### Example 3: Multiple Tools
**You:** "What's the weather in New York and also search for tourist attractions there"

**Nivora:**
- 🌤️ *[Animated get_weather tool]*
- 🔍 *[Animated web_search tool]*
- *Provides weather + search results*

### Example 4: Calculations
**You:** "If I have $500 and want to save 15% each month, how much is that?"

**Nivora:**
- 🔢 *[Animated calculate tool]*
- "That would be $75 per month..."

### Example 5: Open Websites
**You:** "Open YouTube and GitHub for me"

**Nivora:**
- 🌐 *[Animated open_website tool - YouTube]*
- 🌐 *[Animated open_website tool - GitHub]*
- *Opens both websites in your browser*

## 🎯 Comparison: Old vs New

### Before (token-server.py)
```
User: "What's the weather in Tokyo?"
Nivora: "I don't have access to real-time weather data..."
```

### After (token-server-enhanced.py)
```
User: "What's the weather in Tokyo?"
[Animated weather tool appears]
Nivora: "Weather in Tokyo:
🌡️ 18°C (feels like 16°C)
☁️ Clear sky
💧 Humidity: 55%
🌬️ Wind: 8 km/h"
```

## 🔧 Architecture

### How It Works

1. **User sends message** → Frontend (`nivora-chat-enhanced.js`)
2. **Backend receives** → `token-server-enhanced.py`
3. **AWS Bedrock decides** → Should I use a tool?
4. **Tool execution** → Python function runs (web_search, etc.)
5. **Result returned** → Bedrock gets tool result
6. **Final response** → Bedrock generates natural language answer
7. **Frontend animates** → Shows tool animations + response

### Tool Flow Diagram

```
User Input
    ↓
AWS Bedrock Nova Pro (decides if tool needed)
    ↓
    ├─ web_search() → DuckDuckGo API
    ├─ get_weather() → wttr.in API
    ├─ open_website() → webbrowser.open()
    ├─ get_current_time() → datetime
    └─ calculate() → eval (safe)
    ↓
Results → Bedrock → Natural Language Response
    ↓
Frontend Animations + Display
```

## 📝 Adding More Tools

Want to add more tools? Edit `token-server-enhanced.py`:

```python
# 1. Create the tool function
def my_new_tool(param1: str, param2: int) -> str:
    """Your tool description."""
    # Your code here
    return "Result"

# 2. Add to TOOLS_SCHEMA
TOOLS_SCHEMA.append({
    "toolSpec": {
        "name": "my_new_tool",
        "description": "What the tool does",
        "inputSchema": {
            "json": {
                "type": "object",
                "properties": {
                    "param1": {"type": "string", "description": "..."},
                    "param2": {"type": "integer", "description": "..."}
                },
                "required": ["param1", "param2"]
            }
        }
    }
})

# 3. Register function
TOOL_FUNCTIONS["my_new_tool"] = my_new_tool

# 4. Add animation metadata to nivora-chat-enhanced.js
const TOOL_METADATA = {
    // ... existing tools ...
    my_new_tool: {
        icon: 'star',  // Material icon name
        color: '#ffb59e',  // Hex color
        label: 'Doing something cool'
    }
};
```

## 🐛 Troubleshooting

### Tools not working?
1. Check AWS credentials are set
2. Ensure `token-server-enhanced.py` is running (not the old `token-server.py`)
3. Check browser console for errors
4. Verify the enhanced JavaScript is loaded (check Network tab)

### Animations not showing?
1. Make sure you're using `chat.html` with the enhanced script
2. Clear browser cache
3. Check that CSS animations are loaded

### "AWS not configured" error?
1. Set `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` in `.env`
2. Make sure `aws_config.py` is in the parent directory
3. Restart the server

## 🎉 Enjoy Your Enhanced Nivora!

Now you have a fully-featured AI assistant with:
- ✅ Real-time web search
- ✅ Weather information
- ✅ Website opening
- ✅ Time/date info
- ✅ Calculations
- ✅ Beautiful animations
- ✅ Natural conversation

Try asking Nivora anything and watch the magic happen! ✨

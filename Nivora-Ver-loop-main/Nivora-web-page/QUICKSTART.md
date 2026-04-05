# 🚀 QUICK START GUIDE - Nivora Chat with Tools

## ⚡ 3-Step Setup

### Step 1: Install Dependencies
```bash
pip install flask flask-cors livekit ddgs requests python-dotenv
```

### Step 2: Start the Enhanced Server
```bash
cd Nivora-web-page
python token-server-enhanced.py
```

You should see:
```
============================================================
  Nivora Token & Chat Server (ENHANCED WITH TOOLS)
============================================================
  Tools Available: 5
    - web_search (DuckDuckGo)
    - get_weather (wttr.in)
    - open_website (Browser)
    - get_current_time
    - calculate
============================================================
```

### Step 3: Open Chat
Open `chat.html` in your browser

---

## 🎯 Try These Commands

### Weather
```
"What's the weather in Tokyo?"
"How's the weather in Paris and London?"
```

### Web Search
```
"Search for latest AI news"
"Find information about quantum computing"
```

### Open Websites
```
"Open YouTube"
"Open GitHub and Stack Overflow"
```

### Calculations
```
"Calculate 15% of 240"
"What's (100 * 5) / 2?"
```

### Current Time
```
"What time is it?"
"What's today's date?"
```

---

## 🎨 See Animations

Open `tool-animations-demo.html` in your browser to preview all tool animations!

---

## 📚 Full Documentation

- **TOOLS_README.md** - Complete guide with examples
- **IMPLEMENTATION_SUMMARY.md** - Technical details
- **test_tools.py** - Test your setup

---

## ❓ Troubleshooting

### Server won't start?
```bash
# Check dependencies
pip install flask flask-cors livekit ddgs requests python-dotenv

# Check AWS config
# Make sure .env has AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY
```

### Tools not working?
```bash
# Run test script
python test_tools.py

# Should show:
# ✓ Flask installed
# ✓ AWS credentials configured
# ✓ All tools working
```

### Animations not showing?
1. Clear browser cache
2. Make sure `chat.html` is loading `nivora-chat-enhanced.js`
3. Check browser console for errors

---

## 🎉 That's It!

You now have a fully-functional AI chat with:
- ✅ 5 working tools
- ✅ Beautiful animations
- ✅ AWS Bedrock Nova Pro
- ✅ Professional UI

**Enjoy! 🚀**

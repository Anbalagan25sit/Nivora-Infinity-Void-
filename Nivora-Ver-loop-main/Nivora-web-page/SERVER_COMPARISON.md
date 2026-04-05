# 📊 Nivora Chat Servers Comparison

## Which Server Should You Use?

| Feature | token-server.py | token-server-enhanced.py | token-server-ultimate.py |
|---------|-----------------|--------------------------|--------------------------|
| **Basic Chat** | ✅ | ✅ | ✅ |
| **Web Search** | ❌ | ✅ | ✅ |
| **Weather** | ❌ | ✅ | ✅ |
| **Calculator** | ❌ | ✅ | ✅ |
| **Open Websites** | ❌ | ✅ | ✅ |
| **Gmail** | ❌ | ❌ | ✅ |
| **Notion** | ❌ | ❌ | ✅ |
| **Browser Tools** | ❌ | ❌ | ✅ |
| **Tool Animations** | ❌ | ✅ | ✅ |
| **Total Tools** | 0 | 5 | 11 |

---

## 🎯 Quick Decision Guide

### Use `token-server.py` if:
- ✅ You just want basic text chat
- ✅ Don't need any tools
- ✅ Simplest setup

**Start with:**
```bash
python token-server.py
```

---

### Use `token-server-enhanced.py` if:
- ✅ You want web search & weather
- ✅ Want beautiful tool animations
- ✅ Don't need email/Notion integration
- ✅ Minimal configuration (just AWS)

**Start with:**
```bash
python token-server-enhanced.py
```

**Tools you get:**
- 🔍 Web Search
- 🌤️ Weather
- 🌐 Open Websites
- ⏰ Time/Date
- 🔢 Calculator

---

### Use `token-server-ultimate.py` if: ⭐ **RECOMMENDED**
- ✅ You want ALL the tools!
- ✅ Need Gmail integration
- ✅ Need Notion integration
- ✅ Want browser automation
- ✅ Full productivity assistant

**Start with:**
```bash
python token-server-ultimate.py
```

**Tools you get:**
- 🔍 Web Search
- 🌤️ Weather
- 🌐 Open Websites
- ⏰ Time/Date
- 🔢 Calculator
- 📧 **Send Emails**
- 📬 **Read Emails**
- 📝 **Create Notion Pages**
- 🔍 **Search Notion**
- 🌐 **Browser Navigation**
- 📸 **Take Screenshots**

---

## 📋 Setup Requirements

### token-server.py
```env
# .env file
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...
```

**Dependencies:**
```bash
pip install flask flask-cors livekit
```

---

### token-server-enhanced.py
```env
# .env file
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...
```

**Dependencies:**
```bash
pip install flask flask-cors livekit ddgs requests
```

---

### token-server-ultimate.py ⭐
```env
# .env file (required)
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...

# Optional - for Gmail
EMAIL_USER=your.email@gmail.com
EMAIL_PASS=your_app_password

# Optional - for Notion
NOTION_API_KEY=secret_...
NOTION_DATABASE_ID=...
```

**Dependencies:**
```bash
pip install flask flask-cors livekit ddgs requests pyautogui
```

---

## 🎨 Example Conversations

### With token-server.py (Basic)
```
You: "What's the weather in Paris?"
Nivora: "I don't have access to real-time weather data, but I can help you find a weather website..."
```

### With token-server-enhanced.py (Enhanced)
```
You: "What's the weather in Paris?"
[🌤️ Animated weather tool]
Nivora: "Weather in Paris:
🌡️ 15°C (feels like 13°C)
☁️ Partly cloudy
💧 Humidity: 65%"
```

### With token-server-ultimate.py (Ultimate)
```
You: "What's the weather in Paris and send an email to alice@example.com with the weather info"
[🌤️ Animated weather tool]
[📧 Animated send email tool]
Nivora: "Weather in Paris: 15°C, Partly cloudy

I've sent an email to alice@example.com with the weather information!"
```

---

## 💡 Recommendation

### **For Most Users:** token-server-ultimate.py ⭐

**Why?**
- ✅ All features included
- ✅ Beautiful animations for every tool
- ✅ Gmail & Notion work without extra config (just add credentials when you need them)
- ✅ Browser tools work immediately
- ✅ Most productive experience

### **For Quick Testing:** token-server-enhanced.py

**Why?**
- ✅ No Gmail/Notion setup needed
- ✅ Still has animations
- ✅ Web search & weather work great
- ✅ Faster to get started

### **For Minimal Setup:** token-server.py

**Why?**
- ✅ Absolute simplest
- ✅ Just chat, no tools
- ✅ Good for testing AWS Bedrock

---

## 🚀 Migration Path

Start simple, upgrade as needed:

```
token-server.py
    ↓ (want web search & weather)
token-server-enhanced.py
    ↓ (want Gmail & Notion)
token-server-ultimate.py ⭐
```

All servers use the **same chat.html** file!

---

## 📝 Quick Commands

### Start Basic Server
```bash
python token-server.py
```

### Start Enhanced Server
```bash
python token-server-enhanced.py
```

### Start Ultimate Server ⭐
```bash
python token-server-ultimate.py
```

---

## ✅ Summary

| Choose | If You Want |
|--------|-------------|
| **Basic** | Simple chat only |
| **Enhanced** | Web search, weather, calculations |
| **Ultimate** ⭐ | **Everything** (Gmail, Notion, Browser, etc.) |

**Recommendation:** Go with **token-server-ultimate.py** for the best experience! You can always skip the Gmail/Notion setup if you don't need them.

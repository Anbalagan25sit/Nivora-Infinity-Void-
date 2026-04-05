# 🚀 Nivora ULTIMATE - Gmail, Notion & Browser Tools Setup

## 🎯 **New Tools Available**

### 📧 **Gmail Tools**
1. **send_email** - Send emails via Gmail
2. **read_emails** - Read recent emails from inbox

### 📝 **Notion Tools**
3. **notion_create_page** - Create new Notion pages
4. **notion_search** - Search your Notion workspace

### 🌐 **Browser Tools**
5. **browser_navigate** - Navigate to any URL
6. **take_screenshot** - Capture screenshots

---

## 📋 **Setup Instructions**

### **1. Gmail Setup (Required for Email Tools)**

#### **Step 1: Enable 2-Step Verification**
1. Go to [Google Account](https://myaccount.google.com/)
2. Click **Security** → **2-Step Verification**
3. Follow the steps to enable it

#### **Step 2: Generate App Password**
1. Go to [App Passwords](https://myaccount.google.com/apppasswords)
   - (Or: Security → 2-Step Verification → App passwords)
2. Select **Mail** and **Other (Custom name)**
3. Enter "Nivora" as the name
4. Click **Generate**
5. **Copy the 16-character password** (looks like: `abcd efgh ijkl mnop`)

#### **Step 3: Add to .env File**
Add these to your `.env` file:
```env
# Gmail Configuration
EMAIL_USER=your.email@gmail.com
EMAIL_PASS=abcd efgh ijkl mnop
```

**Important:** Use the **App Password**, not your regular Gmail password!

---

### **2. Notion Setup (Required for Notion Tools)**

#### **Step 1: Create Notion Integration**
1. Go to [Notion Integrations](https://www.notion.so/my-integrations)
2. Click **+ New integration**
3. Fill in:
   - **Name:** Nivora
   - **Associated workspace:** Select your workspace
   - **Type:** Internal integration
4. Click **Submit**
5. **Copy the "Internal Integration Token"** (starts with `secret_...`)

#### **Step 2: Create/Connect a Database**
1. Open Notion and create a new **Database** (or use existing)
2. Click the **•••** menu → **Add connections**
3. Select **Nivora** (your integration)
4. **Copy the Database ID** from URL:
   - URL: `https://notion.so/workspace/DATABASE_ID?v=...`
   - The DATABASE_ID is the long string of letters/numbers

#### **Step 3: Add to .env File**
```env
# Notion Configuration
NOTION_API_KEY=secret_ABC123XYZ...
NOTION_DATABASE_ID=abc123def456...
```

---

### **3. Browser Tools Setup (Optional)**

#### **For Screenshots:**
```bash
pip install pyautogui
```

No configuration needed - works immediately!

---

## 🚀 **Quick Start**

### **1. Install Dependencies**
```bash
pip install flask flask-cors livekit ddgs requests python-dotenv pyautogui
```

### **2. Configure .env**
Your complete `.env` should look like:
```env
# AWS (Required)
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret
AWS_REGION=us-east-1
AWS_BEDROCK_MODEL=amazon.nova-pro-v1:0

# Gmail (Optional - for email tools)
EMAIL_USER=your.email@gmail.com
EMAIL_PASS=your app password here

# Notion (Optional - for Notion tools)
NOTION_API_KEY=secret_ABC123...
NOTION_DATABASE_ID=abc123def...

# LiveKit (Required)
LIVEKIT_API_KEY=your_key
LIVEKIT_API_SECRET=your_secret
LIVEKIT_URL=wss://your-project.livekit.cloud
```

### **3. Start the Server**
```bash
cd Nivora-web-page
python token-server-ultimate.py
```

You'll see:
```
======================================================================
  NIVORA TOKEN & CHAT SERVER - ULTIMATE EDITION
======================================================================
  Tools Available: 11

  📦 Basic Tools:
    • web_search, get_weather, open_website
    • get_current_time, calculate

  📧 Gmail Tools:
    • send_email, read_emails

  📝 Notion Tools:
    • notion_create_page, notion_search

  🌐 Browser Tools:
    • browser_navigate, take_screenshot
======================================================================
```

### **4. Open Chat**
Open `chat.html` in your browser

---

## 💬 **Example Commands**

### **📧 Gmail Examples**

#### **Send an Email**
```
"Send an email to john@example.com with subject 'Meeting Tomorrow' and body 'Hi John, just confirming our 2pm meeting.'"
```

**What happens:**
- 📧 Animated **send_email** tool appears
- Email is sent via Gmail
- ✅ Confirmation message

#### **Read Emails**
```
"What are my recent emails?"
"Show me my last 3 emails"
```

**What happens:**
- 📧 Animated **read_emails** tool appears
- Shows sender, subject, and date

---

### **📝 Notion Examples**

#### **Create a Page**
```
"Create a Notion page titled 'Meeting Notes' with content 'Discussed Q4 goals and timeline.'"
```

**What happens:**
- 📝 Animated **notion_create_page** tool appears
- Page created in your connected database
- ✅ Confirmation with link

#### **Search Notion**
```
"Search my Notion for 'project ideas'"
"Find pages about 'meeting notes' in Notion"
```

**What happens:**
- 🔍 Animated **notion_search** tool appears
- Shows matching pages with links

---

### **🌐 Browser Examples**

#### **Navigate**
```
"Go to https://github.com/Anbalagan25sit"
"Navigate to my portfolio website"
```

**What happens:**
- 🌐 Animated **browser_navigate** tool appears
- Browser opens to that URL

#### **Screenshot**
```
"Take a screenshot"
"Capture a screenshot and save it as demo.png"
```

**What happens:**
- 📸 Animated **take_screenshot** tool appears
- Screenshot saved to file
- ✅ Confirmation message

---

### **🔥 Combined Examples**

#### **Email + Weather**
```
"What's the weather in Tokyo, and send an email to alice@example.com telling her about it"
```

**What happens:**
1. 🌤️ **get_weather** tool (gets Tokyo weather)
2. 📧 **send_email** tool (sends email with weather info)
3. Beautiful animations for both!

#### **Notion + Web Search**
```
"Search for latest AI trends and create a Notion page summarizing them"
```

**What happens:**
1. 🔍 **web_search** tool (finds AI trends)
2. 📝 **notion_create_page** tool (creates summary page)

---

## 🎨 **Tool Animations**

Each tool has a unique animation:

| Tool | Icon | Color |
|------|------|-------|
| send_email | 📧 mail | Green (#4ade80) |
| read_emails | 📬 mail | Blue (#60a5fa) |
| notion_create_page | 📝 note_add | Black (#000000) |
| notion_search | 🔍 search | Black (#000000) |
| browser_navigate | 🌐 public | Purple (#8b5cf6) |
| take_screenshot | 📸 screenshot | Pink (#ec4899) |

---

## ❓ **Troubleshooting**

### **Gmail: "Authentication failed"**
```
❌ Make sure you're using an App Password, not your regular Gmail password
```

**Fix:**
1. Check you enabled 2-Step Verification
2. Generate new App Password
3. Copy the 16-character code (with spaces removed)
4. Update `.env` file

### **Notion: "Unauthorized"**
```
❌ Notion error: 401 - Unauthorized
```

**Fix:**
1. Go to your Notion database
2. Click **•••** → **Add connections**
3. Select your **Nivora** integration
4. Make sure NOTION_API_KEY is correct in `.env`

### **Notion: "Database not found"**
```
❌ Notion error: database_id is not a valid UUID
```

**Fix:**
1. Copy the Database ID from the URL
2. Format: `https://notion.so/workspace/DATABASE_ID?v=...`
3. Update NOTION_DATABASE_ID in `.env`

### **Screenshot: "pyautogui not found"**
```
❌ pyautogui not installed
```

**Fix:**
```bash
pip install pyautogui
```

---

## 🔒 **Security Notes**

### **Gmail App Password**
- ✅ Safer than using your real password
- ✅ Can be revoked anytime
- ✅ Limited to email access only

### **Notion API Key**
- ✅ Only has access to databases you connect
- ✅ Can be regenerated if compromised
- ✅ Stored securely in `.env` (not in code)

### **Never Share:**
- 🚫 Your `.env` file
- 🚫 App passwords
- 🚫 API keys

---

## 🎉 **You're Ready!**

Start the server and try:

```bash
python token-server-ultimate.py
```

Then ask Nivora:
- "What are my recent emails?"
- "Send an email to..."
- "Create a Notion page about..."
- "Search Notion for..."
- "Take a screenshot"

**Enjoy your AI-powered productivity assistant!** ✨

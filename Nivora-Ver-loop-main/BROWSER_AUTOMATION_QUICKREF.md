# Browser Automation Quick Reference

## 🎯 Voice Commands

### Login/Authentication
```
"Login to Twitter"
"Sign into my Gmail account"
"Authenticate with GitHub"
```

### Form Filling
```
"Fill out the contact form on example.com"
"Complete the signup form with my info"
"Submit the feedback form"
```

### Data Extraction
```
"Extract all prices from this Amazon page"
"What are the top stories on Hacker News?"
"Get all email addresses from the about page"
"List all products and their ratings"
```

### Page Analysis
```
"What's on this page?"
"Summarize this article"
"Is this page showing an error?"
"What is the main heading?"
```

### Navigation + Action
```
"Go to Google and search for Python tutorials"
"Open LinkedIn and check my notifications"
"Navigate to my bank dashboard and tell me my balance"
```

---

## 🛠️ Tool Quick Reference

| Tool | When to Use | Example |
|------|-------------|---------|
| `web_automate` | Complex multi-step tasks | Login flows, multi-click workflows |
| `browser_navigate_and_analyze` | Visit + understand page | Summarize, check status, read content |
| `fill_web_form` | Smart form filling | Contact forms, signups |
| `browser_extract_data` | Data scraping | Prices, listings, tables |

---

## ⚡ Installation Quick Start

```bash
# 1. Install dependencies
pip install playwright selenium

# 2. Install browser
python -m playwright install chromium

# 3. Test it
python test_browser_automation.py

# 4. Run Nivora
python agent.py start
```

---

## 🔥 Pro Tips

### Speed
- **Use CSS selectors** when possible (fastest)
- **Enable headless mode** for background tasks
- **Batch operations** in single calls

### Reliability
- **Enable vision fallback** for complex pages
- **Add wait conditions** for slow-loading elements
- **Verify results** after automation

### Security
- **Never hardcode credentials**
- **Use environment variables** for sensitive data
- **Vision AI handles passwords** securely

---

## 🐛 Quick Troubleshooting

| Problem | Solution |
|---------|----------|
| "Playwright not available" | `pip install playwright && python -m playwright install chromium` |
| Navigation timeout | Increase timeout or check URL |
| Element not found | Vision fallback will auto-engage |
| Vision AI error | Check AWS credentials in `.env` |

---

## 📁 File Structure

```
browser_automation.py         # Core engine
tools.py                      # Tool definitions (updated)
prompts.py                    # Agent instructions (updated)
test_browser_automation.py    # Test suite
BROWSER_AUTOMATION_GUIDE.md   # Full documentation
```

---

## 🎨 Architecture at a Glance

```
Voice Input
    ↓
LLM decides tool
    ↓
Browser Engine (Playwright/Selenium)
    ↓
Vision AI (Nova Pro) for complex cases
    ↓
Execute actions
    ↓
Verify & respond
```

---

## 🌟 Example Workflows

### Workflow 1: Research + Extract
```
1. "Search Google for best laptops 2024"
2. "Click the first result"
3. "Extract all laptop names and prices"
4. "Save this to my notes"
```

### Workflow 2: Login + Check
```
1. "Login to my email"
2. "Check if I have any unread messages"
3. "Read the most recent one"
```

### Workflow 3: Form + Submit
```
1. "Go to example.com/contact"
2. "Fill the form with my info"
3. "Submit it"
4. "Confirm it was sent"
```

---

## 📞 Need Help?

1. **Check logs**: `export LOG_LEVEL=DEBUG`
2. **Run tests**: `python test_browser_automation.py`
3. **Read full guide**: `BROWSER_AUTOMATION_GUIDE.md`
4. **Check errors**: Look at browser window if visible

---

## ✅ Pre-flight Checklist

Before using browser automation:
- [ ] Playwright/Selenium installed
- [ ] Chromium browser installed
- [ ] AWS credentials in `.env`
- [ ] Test script passes
- [ ] Agent starts without errors

---

**You're ready to automate! 🚀**

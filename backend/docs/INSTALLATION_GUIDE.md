# Browser Automation Installation Guide

## 🚀 Step-by-Step Installation

### Prerequisites

Before you start, ensure you have:
- ✅ Python 3.9+ installed
- ✅ Nivora project downloaded
- ✅ AWS credentials configured in `.env`
- ✅ Internet connection

---

## Step 1: Install Browser Automation Libraries

Open your terminal in the Nivora project directory and run:

```bash
# Install Playwright (recommended)
pip install playwright

# Install Selenium (optional fallback)
pip install selenium
```

**Expected output:**
```
Successfully installed playwright-1.40.0
Successfully installed selenium-4.15.0
```

---

## Step 2: Install Browser (Chromium)

After installing Playwright, install the browser:

```bash
python -m playwright install chromium
```

**Expected output:**
```
Downloading Chromium 119.0.6045.9 (playwright build v1091) from https://playwright.azureedge.net...
Chromium 119.0.6045.9 (playwright build v1091) downloaded to...
```

**Size:** ~200 MB download

---

## Step 3: Verify Installation

Run the test suite to verify everything works:

```bash
python test_browser_automation.py
```

**Expected output:**
```
======================================================================
 BROWSER AUTOMATION TEST SUITE
======================================================================

Backends available:
  Playwright: ✓
  Selenium: ✓

======================================================================
TEST 1: Navigation & Screenshot
======================================================================
→ Navigating to example.com...
✓ Navigated successfully
  Title: Example Domain
  URL: https://example.com/

...

======================================================================
 TEST SUMMARY
======================================================================
✓ PASS - Navigation & Screenshot
✓ PASS - Vision AI Analysis
✓ PASS - Element Interaction
✓ PASS - Form Filling
✓ PASS - Data Extraction
✓ PASS - Complete Workflow

6/6 tests passed

🎉 All tests passed!
```

---

## Step 4: Test Individual Components

If the full test suite fails, test components individually:

```bash
# Test navigation only
python test_browser_automation.py --test navigation

# Test vision analysis
python test_browser_automation.py --test vision

# Test form filling
python test_browser_automation.py --test form
```

---

## Step 5: Test with Nivora Agent

Start your Nivora agent:

```bash
python agent.py start
```

**Test voice commands:**
1. Connect to the LiveKit room
2. Say: **"Go to example.com and tell me what you see"**
3. Expected: Nivora should navigate and describe the page

---

## 🐛 Troubleshooting Installation

### Issue 1: "Playwright not found"

**Symptom:**
```
ImportError: No module named 'playwright'
```

**Solution:**
```bash
pip install playwright
python -m playwright install chromium
```

---

### Issue 2: "Browser not installed"

**Symptom:**
```
playwright._impl._api_types.Error: Executable doesn't exist at ...
```

**Solution:**
```bash
# Install browser
python -m playwright install chromium

# Or install all browsers
python -m playwright install
```

---

### Issue 3: "Selenium WebDriver not found"

**Symptom:**
```
selenium.common.exceptions.WebDriverException: Message: 'chromedriver' executable needs to be in PATH
```

**Solution:**
Selenium should auto-download ChromeDriver. If not:
```bash
# Reinstall selenium
pip uninstall selenium
pip install selenium

# Or use Playwright instead (recommended)
```

---

### Issue 4: "AWS credentials error"

**Symptom:**
```
RuntimeError: AWS_ACCESS_KEY_ID or AWS_SECRET_ACCESS_KEY is missing in .env
```

**Solution:**
1. Check `.env` file exists
2. Verify it contains:
   ```
   AWS_ACCESS_KEY_ID=your_key_here
   AWS_SECRET_ACCESS_KEY=your_secret_here
   AWS_REGION=us-east-1
   AWS_BEDROCK_MODEL=amazon.nova-pro-v1:0
   ```

---

### Issue 5: "Vision AI not working"

**Symptom:**
```
Vision analysis failed: ...
```

**Solutions:**

**Check AWS Bedrock access:**
1. Log into AWS Console
2. Go to Amazon Bedrock
3. Enable "Model access" for Nova Pro
4. Wait 5-10 minutes for activation

**Check region:**
- Ensure `AWS_REGION=us-east-1` (or supported region)
- Nova Pro may not be available in all regions

**Check credentials:**
```bash
# Test AWS access
python -c "import boto3; print(boto3.client('bedrock-runtime', region_name='us-east-1').meta.region_name)"
```

---

### Issue 6: "Tests fail on network timeout"

**Symptom:**
```
Navigation timeout: ...
```

**Solutions:**
- Check internet connection
- Increase timeout in code:
  ```python
  await browser.navigate(url, wait_until="load")  # Less strict
  ```
- Some sites block automation - try different test sites

---

### Issue 7: "Permission denied" errors (Linux/Mac)

**Solution:**
```bash
# Make sure Python has execution permissions
chmod +x test_browser_automation.py
chmod +x browser_automation.py

# Or run with python explicitly
python test_browser_automation.py
```

---

### Issue 8: "Module not found" for project files

**Symptom:**
```
ModuleNotFoundError: No module named 'browser_automation'
```

**Solution:**
```bash
# Make sure you're in the project directory
cd /path/to/Nivora-Ver-loop-main

# Run from project root
python test_browser_automation.py
```

---

## 📋 Quick Installation Checklist

Use this checklist to verify each step:

```
Installation Checklist:
□ Python 3.9+ installed
□ In Nivora project directory
□ Playwright installed (pip install playwright)
□ Selenium installed (pip install selenium)
□ Chromium browser installed (python -m playwright install chromium)
□ AWS credentials in .env file
□ Test suite runs successfully
□ Agent starts without errors
□ Voice command test works
```

---

## 🎯 Verification Commands

Run these to verify everything is working:

```bash
# 1. Check Python version
python --version  # Should be 3.9+

# 2. Check Playwright installation
python -c "from playwright.async_api import async_playwright; print('✓ Playwright OK')"

# 3. Check Selenium installation
python -c "from selenium import webdriver; print('✓ Selenium OK')"

# 4. Check browser automation engine
python -c "from browser_automation import BrowserAutomationEngine; print('✓ Engine OK')"

# 5. Check tools
python -c "from tools import web_automate; print('✓ Tools OK')"

# 6. Check AWS credentials
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print('✓ AWS Key:', os.getenv('AWS_ACCESS_KEY_ID')[:8] + '...')"
```

Expected output for all:
```
✓ Playwright OK
✓ Selenium OK
✓ Engine OK
✓ Tools OK
✓ AWS Key: AKIA...
```

---

## 🔧 Alternative Installation (If Issues Persist)

If you encounter persistent issues, try this minimal setup:

```bash
# 1. Create fresh virtual environment
python -m venv venv_browser
source venv_browser/bin/activate  # Linux/Mac
# or
venv_browser\Scripts\activate  # Windows

# 2. Install only Playwright (skip Selenium)
pip install playwright pillow

# 3. Install browser
python -m playwright install chromium

# 4. Install Nivora dependencies
pip install livekit-agents livekit-plugins-aws python-dotenv

# 5. Test minimal setup
python -c "from playwright.async_api import async_playwright; print('OK')"
```

---

## 🆘 Still Having Issues?

### Check Logs

Enable debug logging:
```bash
export LOG_LEVEL=DEBUG  # Linux/Mac
set LOG_LEVEL=DEBUG     # Windows

python test_browser_automation.py
```

### Test Individual Components

```bash
# Test browser engine directly
python browser_automation.py

# Test specific test
python test_browser_automation.py --test navigation
```

### Get Help

1. **Check logs** for specific error messages
2. **Review documentation** in `BROWSER_AUTOMATION_GUIDE.md`
3. **Check issue** - Look for similar problems
4. **Gather info**:
   - Python version: `python --version`
   - OS version
   - Error message (full stack trace)
   - What you were trying to do

---

## ✅ Installation Complete!

If you've reached this point with no errors, you're ready to use browser automation!

**Next steps:**
1. Read `BROWSER_AUTOMATION_QUICKREF.md` for voice commands
2. Review `BROWSER_AUTOMATION_GUIDE.md` for detailed usage
3. Start using Nivora with browser automation enabled!

**Test it now:**
```bash
python agent.py start
```

Say: **"Go to Wikipedia and tell me what you see"**

---

**Happy automating! 🚀**

# E-Box Automation - Chrome Profile Setup & Usage

## 🔧 Important Setup Steps

### 1. Close ALL Chrome Windows First
**CRITICAL:** Before running E-Box automation, you MUST close ALL Chrome windows.

Why? Playwright needs exclusive access to your Chrome profile.

```bash
# Close Chrome completely
# Right-click Chrome in taskbar → Close all windows
# Or: Task Manager → End all Chrome processes
```

### 2. Verify Chrome Profile Path
The automation uses your default Chrome profile at:
```
%LOCALAPPDATA%\Google\Chrome\User Data
```

This means:
- ✅ Your E-Box login will be remembered
- ✅ No need to login every time
- ✅ Cookies and session preserved

### 3. Browser Stays Open
The browser will **NOT** close automatically. This lets you:
- ✅ Verify the code was submitted correctly
- ✅ Check the results
- ✅ Manually fix anything if automation fails
- ✅ Continue working on next problem

---

## 🚀 How to Use

### Method 1: Natural Language (Recommended)

**Start Nivora:**
```bash
python agent.py
```

**Say to Nivora:**
```
"Finish differential equations"
"Complete biology course"
"Solve the current problem"
```

### Method 2: Manual Testing

Test the automation directly:
```python
from ebox_automation import complete_ebox_course
import asyncio

async def test():
    # Simulate Nivora calling the tool
    result = await complete_ebox_course(None, "finish differential equations")
    print(result)

asyncio.run(test())
```

---

## 🔍 What Happens Step-by-Step

1. **Browser Opens** with your Chrome profile
   - Uses your saved cookies
   - E-Box login already active (if you logged in before)

2. **Check Login Status**
   - If already logged in → Skips login
   - If not logged in → Attempts auto-login with SIT25CS170

3. **Navigate to Course**
   - Uses vision AI to find course card
   - Clicks the course

4. **Analyze Problem**
   - Reads problem description
   - Identifies: context, tasks, input/output format
   - Determines programming language needed

5. **Generate Solution**
   - AWS Nova Pro writes complete code
   - Determines command line arguments
   - Provides explanation

6. **Submit Code**
   - Pastes code into editor
   - Fills command line arguments field
   - Clicks submit button

7. **Browser Stays Open**
   - You can verify submission
   - Check results
   - Fix anything manually if needed

---

## 📝 Example Workflow

**You:** "Hey Nivora, finish differential equations"

**Nivora:** "On it! Opening Chrome with your profile..."

*[Browser opens, already logged into E-Box]*

**Nivora:** "Already logged in! Navigating to Differential Equations course..."

*[Finds and clicks course card]*

**Nivora:** "Analyzing the problem: Simulating Bacterial Population Growth..."

*[Vision AI reads problem]*

**Nivora:** "Generating Python code solution..."

*[AWS Nova Pro writes code]*

**Nivora:** "Submitting code with command line arguments: `P0=100 k=0.05`..."

*[Code submitted]*

**Nivora:** "✅ Simulating Bacterial Population Growth completed!

**Solution Approach:** Implemented exponential growth model using differential equations

**Command Line Args:** `P0=100 k=0.05`

Code submitted successfully! Check the E-Box platform for results.

⚠️ **IMPORTANT:** Browser left open for you to verify the submission!"

---

## 🐛 Troubleshooting

### Issue: "Could not use existing Chrome profile"

**Solution:**
```bash
# 1. Close ALL Chrome windows
# 2. Check Task Manager - end all chrome.exe processes
# 3. Try again
```

### Issue: Browser closes immediately

**Solution:** This is fixed! Browser now stays open. If it still closes, check:
- Are you using the updated `ebox_automation.py`?
- Check logs for errors

### Issue: "Login failed"

**Solution:**
- Browser is left open - login manually
- Or: Make sure Chrome profile has saved E-Box login
- Login manually once, then try automation again

### Issue: "Could not find course"

**Solution:**
```
# Ask Nivora:
"What courses are available?"

# Then:
"Complete [exact course name]"
```

### Issue: Code submission fails

**Solution:**
- Browser left open - check the code manually
- Generated code is shown in error message
- Copy and paste manually if needed

---

## 💡 Pro Tips

### Tip 1: Login Once Manually
Before using automation:
1. Open Chrome normally
2. Login to https://pro.e-box.co.in
3. Close Chrome
4. Run automation - you'll stay logged in!

### Tip 2: Keep Browser Open
The browser stays open intentionally:
- Verify code worked
- Check test results
- Run next problem without restarting

### Tip 3: Use Natural Language
Be flexible:
```
"Finish differential equations"
"Complete biology"
"Solve the solution of ordinary differential equations problem"
"Help me with bacterial growth simulation"
```

All work!

### Tip 4: Check Generated Code
When Nivora generates code, you can:
1. See it in the browser editor
2. Test it manually first
3. Submit when satisfied

### Tip 5: Multiple Problems
For multiple problems:
1. Complete first problem
2. Browser stays open
3. Navigate to next problem manually
4. Say: "Solve the current problem"
5. Repeat!

---

## 🔒 Privacy & Security

### What's Stored in Chrome Profile?
- E-Box login cookies
- Session data
- Your browsing history (only for E-Box)

### What's Shared?
- **Nothing!** All processing happens locally
- AWS Nova Pro only sees problem screenshots (no personal data)
- Code generation is based on problem description only

### Credentials
- Hardcoded: SIT25CS170/SIT25CS170
- Only used if not already logged in
- Never sent anywhere except E-Box login

---

## 📊 Success Indicators

**Good Signs:**
```
✅ "Already logged in via Chrome profile"
✅ "Logged in successfully"
✅ "Analyzing the problem: [Problem Name]"
✅ "Generated Python code solution"
✅ "Code submitted successfully"
✅ "Browser left open for verification"
```

**Warning Signs (Not Fatal):**
```
⚠️ "Please complete login manually in browser"
⚠️ "Browser left open - please check manually"
⚠️ "Generated code: [shown for manual copy]"
```

---

## 🎯 Quick Checklist

Before running automation:
- [ ] Close ALL Chrome windows
- [ ] Logged into E-Box at least once manually
- [ ] AWS credentials in .env (AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)
- [ ] Playwright installed: `pip install playwright && python -m playwright install chromium`

To run:
- [ ] Start Nivora: `python agent.py`
- [ ] Connect via LiveKit
- [ ] Say: "Finish [course name]"
- [ ] Wait for completion message
- [ ] Verify in open browser
- [ ] Done! ✅

---

## 📞 Need Help?

**Test the setup:**
```bash
python test_ebox_simple.py
```

**Check logs:**
Look for `[EBox]` messages in console output.

**Manual verification:**
Browser stays open - you can always check/fix manually!

---

**Remember:** The automation is a HELPER, not a replacement. Always verify the code and results! 🚀

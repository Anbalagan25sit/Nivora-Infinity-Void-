# E-Box Course Automation Guide

## 🎓 Overview

Nivora can now **automatically complete E-Box course assessments** using advanced AI-powered question solving! This feature uses a hybrid approach combining:
- **Vision AI** (AWS Nova Pro) for screenshot analysis
- **Text Extraction** for direct HTML parsing
- **Natural Language Processing** for understanding course requests

---

## ✨ Features

✅ **Automatic Login** - Uses credentials SIT25CS170/SIT25CS170
✅ **Natural Language Commands** - Just speak naturally ("finish my course")
✅ **AI Question Solving** - Hybrid vision + text analysis
✅ **Smart Answer Selection** - Makes best guesses on ambiguous questions
✅ **Progress Tracking** - Reports answered questions and confidence levels
✅ **Course Navigation** - Automatically finds units and sections

---

## 🗣️ How to Use (Natural Language Examples)

Just speak to Nivora naturally using any of these commands:

### Complete Entire Course
```
"Finish my course"
"Complete my course"
"Do my course"
```

### Complete Specific Unit
```
"Complete unit 3"
"Finish unit 2"
"Do unit 1"
"Complete OS unit 4"
"Finish compiler design unit 2"
```

### Complete Specific Section
```
"Complete section 3 of unit 1"
"Do section 2"
"Finish section 1 of unit 3"
```

### Course-Specific Commands
```
"Do compiler design unit 2"
"Complete operating systems unit 3"
"Finish DBMS unit 1"
```

---

## 🧠 How It Works

### Step 1: Login
- Automatically navigates to https://pro.e-box.co.in/login
- Fills username and password fields
- Submits login form
- Verifies successful login

### Step 2: Course Navigation
- Uses vision AI to identify available courses
- Clicks the requested course
- Navigates to specified unit and section

### Step 3: Question Extraction
- Takes screenshot of assessment page
- Uses AWS Nova Pro to identify:
  - Total number of questions
  - Question text
  - Answer options
  - Question types (MCQ, True/False, etc.)

### Step 4: AI Question Solving
- **For each question:**
  1. Captures screenshot of question
  2. Extracts question text and options
  3. Sends to AWS Nova Pro for analysis
  4. AI analyzes and selects best answer
  5. Returns answer with confidence score

### Step 5: Answer Selection
- Uses vision AI to locate answer option
- Clicks the correct radio button/checkbox
- Waits for response to register

### Step 6: Submission
- Finds and clicks submit button
- Verifies submission success
- Reports results to user

---

## 📊 Question Solving Strategy

### Hybrid Approach

**Vision-Based Solving:**
- Takes screenshot of question
- AWS Nova Pro reads question visually
- Handles complex formatting, images, diagrams
- Best for: Math equations, diagrams, formatted code

**Text-Based Solving:**
- Extracts HTML text directly
- Sends plain text to Nova Pro
- Faster processing
- Best for: Text-only questions, definitions

**Smart Selection:**
- For conditional/ambiguous questions, AI makes **best educated guess**
- Uses computer science knowledge base
- Considers **most commonly accepted answers**
- Returns confidence score (0.0 to 1.0)

### Example AI Reasoning

**Question:** "What is a compiler?"

**Options:**
1. A program that translates high-level code to machine code
2. A hardware component
3. A database system
4. An operating system

**AI Analysis:**
```json
{
  "answer_index": 0,
  "answer_text": "A program that translates high-level code to machine code",
  "confidence": 0.95,
  "reasoning": "By definition, a compiler is a translator program that converts high-level programming language to machine code."
}
```

---

## 🎯 Course Name Mappings

For convenience, Nivora understands common abbreviations:

| User Says | Mapped To |
|-----------|-----------|
| "compiler" / "cd" | Compiler Design |
| "os" | Operating Systems |
| "dbms" / "database" | Database Management Systems |
| "cn" | Computer Networks |
| "ds" | Data Structures |
| "algo" / "algorithm" | Algorithms |

You can also use full course names directly!

---

## 📋 Progress Reporting

Nivora will report progress like:

```
"Alright, completing unit 3 for you now..."

[Processing...]

"✅ Unit 3 completed! Answered 18/20 questions across 4 sections."
```

For each section:
```
✓ Question 1/20 answered (confidence: 95%)
✓ Question 2/20 answered (confidence: 87%)
✓ Question 3/20 answered (confidence: 92%)
...
```

---

## ⚙️ Technical Details

### Files
- **`ebox_automation.py`** - Main automation logic
- **`tools.py`** - Tool registration (imports E-Box tools)
- **`prompts.py`** - Natural language trigger instructions
- **`agent.py`** - Agent configuration

### Dependencies
```bash
# Browser automation
pip install playwright
playwright install chromium

# AWS Bedrock for AI
boto3

# Image processing (for screenshots)
pillow
```

### Credentials
- **Username:** SIT25CS170
- **Password:** SIT25CS170
- **Login URL:** https://pro.e-box.co.in/login

---

## 🔧 Troubleshooting

### "Login failed"
- Check internet connection
- Verify E-Box website is accessible
- Credentials might have changed (update in `ebox_automation.py`)

### "Could not find course"
- Speak the full course name
- Check available courses: "list my courses"
- Try using abbreviations (see mappings above)

### "Questions not extracting"
- E-Box page structure might have changed
- Check browser console for errors
- Playwright might need reinstall: `playwright install chromium`

### Low confidence answers
- AI will still select best guess
- Confidence < 70% = uncertain but will try
- You can manually review with `ebox_quick_answer` tool

---

## 🚀 Advanced Usage

### Quick Answer Tool (Manual Verification)

If you want to verify a single question's answer:

```python
ebox_quick_answer(
    question="What is a compiler?",
    option_a="A translator program",
    option_b="A hardware device",
    option_c="An OS component",
    option_d="A database"
)
```

Response:
```
💡 Answer: A translator program

Confidence: 95%

Reasoning: A compiler translates high-level programming language to machine code.
```

---

## 📝 Example Conversation

**You:** "Hey Nivora, finish my course"

**Nivora:** "On it! Logging in and completing your course now..."

*[Processing...]*

**Nivora:** "Logged in successfully. I see 3 available courses: Compiler Design, Operating Systems, and DBMS. Which one should I complete?"

**You:** "Compiler design unit 2"

**Nivora:** "Starting compiler design unit 2. This'll take a minute..."

*[Processing...]*

**Nivora:** "✅ Unit 2 completed! Answered 18/20 questions across 4 sections. Nice work!"

---

## 🎤 Speech Improvements

Nivora now speaks with:
- ✅ **Clear enunciation** - No more monotone
- ✅ **Natural pauses** - Uses commas, periods, and ellipsis correctly
- ✅ **Emotional variety** - Excitement, concern, warmth
- ✅ **Proper pacing** - Controlled rhythm and flow
- ✅ **Temperature adjusted** - 0.8 for more consistent, clear speech

---

## 🛡️ Safety & Ethics

- **Authorized Use Only** - Only use on your own account (SIT25CS170)
- **Educational Purpose** - Designed to help with course completion
- **AI Accuracy** - AI makes best guesses but may not be 100% accurate
- **Manual Review** - For important assessments, verify answers manually

---

## 💡 Tips

1. **Be specific** - "Complete unit 3 section 2" is better than just "do course"
2. **Check available courses** - If unsure, ask "what courses are available?"
3. **Review results** - Check confidence scores for verification
4. **One at a time** - Complete one section at a time for best results
5. **Stable internet** - Ensure good connection for vision AI processing

---

## 📞 Support

If you encounter issues:
1. Check this guide first
2. Review error messages
3. Try manual login to verify credentials
4. Check browser console for errors
5. Restart Nivora if needed

---

**Happy Learning! 🎓✨**

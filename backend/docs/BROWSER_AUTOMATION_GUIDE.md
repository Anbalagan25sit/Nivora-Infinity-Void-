# Browser Automation Feature - Complete Guide

## 🎯 Overview

Nivora now has **powerful browser automation capabilities** that combine:
- **Playwright/Selenium** for fast, reliable DOM-based control
- **AWS Nova Pro Vision AI** for intelligent page understanding
- **Hybrid approach** that automatically falls back to vision when DOM fails

This means Nivora can:
- ✅ Login to websites automatically
- ✅ Fill out forms intelligently
- ✅ Extract data from any webpage
- ✅ Navigate complex multi-step workflows
- ✅ Analyze pages with natural language queries
- ✅ Handle dynamic content and SPAs

---

## 🚀 Quick Start

### 1. Install Dependencies

```bash
# Install browser automation libraries
pip install playwright selenium

# Install Playwright browser (required)
python -m playwright install chromium

# Or install all requirements at once
pip install -r requirements.txt
```

### 2. Test the Installation

```bash
# Run all tests
python test_browser_automation.py

# Run specific test
python test_browser_automation.py --test navigation
```

### 3. Start Using with Nivora

Run your agent normally:
```bash
python agent.py start
```

Now you can ask Nivora to automate web tasks:
- **"Login to Twitter for me"**
- **"Fill out the contact form on example.com"**
- **"Extract all prices from this Amazon search"**
- **"Go to Hacker News and summarize the top stories"**

---

## 🛠️ Available Tools

### 1. `web_automate(task, url)`

**General-purpose automation** - handles complex multi-step workflows.

**Use for:**
- Logging into websites
- Multi-step processes (search → click result → extract info)
- Complex interactions requiring multiple actions

**Examples:**
```python
# Login flow
web_automate(
    task="Login to Twitter",
    url="https://twitter.com/login"
)

# Multi-step search and extraction
web_automate(
    task="Search for Python tutorials and click the first result",
    url="https://google.com"
)

# Form filling and submission
web_automate(
    task="Fill out the contact form and submit it",
    url="https://example.com/contact"
)
```

**How it works:**
1. Navigates to the URL
2. Captures screenshot
3. Vision AI creates step-by-step plan
4. Executes each step (click, type, wait, etc.)
5. Verifies success with vision AI

---

### 2. `browser_navigate_and_analyze(url, task)`

**Navigate and analyze** - visit a page and understand it using vision AI.

**Use for:**
- Summarizing web content
- Reading articles or documentation
- Checking page state (logged in, errors, etc.)
- Understanding layouts and content

**Examples:**
```python
# Summarize content
browser_navigate_and_analyze(
    url="https://news.ycombinator.com",
    task="Summarize the top 5 stories"
)

# Check account status
browser_navigate_and_analyze(
    url="https://mybank.com/dashboard",
    task="What is my account balance?"
)

# Analyze product page
browser_navigate_and_analyze(
    url="https://amazon.com/product/B08N5WRWNW",
    task="Extract the price, rating, and shipping info"
)
```

---

### 3. `fill_web_form(url, form_data, submit)`

**Smart form filling** - vision AI identifies fields and fills them.

**Use for:**
- Contact forms
- Signup/registration forms
- Survey forms
- Any structured input forms

**Examples:**
```python
# Contact form
fill_web_form(
    url="https://example.com/contact",
    form_data="name=John Doe, email=john@example.com, message=Hello there",
    submit=True
)

# Signup form
fill_web_form(
    url="https://site.com/signup",
    form_data="username=johndoe, email=john@example.com, password=SecurePass123",
    submit=False  # Don't submit yet
)
```

**How it works:**
1. Vision AI analyzes form structure
2. Matches your data to field labels/names
3. Fills each field intelligently
4. Optionally submits the form

---

### 4. `browser_extract_data(url, query)`

**Data extraction** - scrape structured information from any page.

**Use for:**
- Price comparison
- Product listings
- Contact information
- Table data
- Article headlines

**Examples:**
```python
# Extract prices
browser_extract_data(
    url="https://amazon.com/s?k=laptop",
    query="Extract all product names and prices"
)

# Extract contact info
browser_extract_data(
    url="https://company.com/about",
    query="Find all email addresses and phone numbers"
)

# Extract table data
browser_extract_data(
    url="https://example.com/data-table",
    query="Extract all rows from the main table"
)
```

---

## 💡 Usage Examples with Voice Commands

### Example 1: Login Automation
**You:** "Nivora, log me into Twitter"

**Nivora:** *Silently calls:*
```python
web_automate("Login to Twitter", "https://twitter.com/login")
```

**Nivora says:** "You're now logged into Twitter. Your timeline is ready."

---

### Example 2: Form Filling
**You:** "Fill out the contact form on example.com with my info"

**Nivora:** *Calls:*
```python
fill_web_form(
    "https://example.com/contact",
    "name=Your Name, email=your@email.com, message=Hi there",
    submit=True
)
```

**Nivora says:** "Contact form submitted. Confirmation should arrive soon."

---

### Example 3: Data Extraction
**You:** "What are the top stories on Hacker News right now?"

**Nivora:** *Calls:*
```python
browser_navigate_and_analyze(
    "https://news.ycombinator.com",
    "List the top 5 story titles"
)
```

**Nivora says:** "Here are the top 5 stories: [lists them naturally]"

---

### Example 4: Price Comparison
**You:** "Find me the cheapest laptop on Amazon"

**Nivora:** *Calls:*
```python
browser_extract_data(
    "https://amazon.com/s?k=laptop",
    "Extract all product names and prices, find the cheapest one"
)
```

**Nivora says:** "The cheapest laptop is [name] at $[price]."

---

## 🏗️ Architecture

```
┌──────────────────────────────────────┐
│     Nivora Agent (Voice Input)       │
│  "Login to Twitter for me"           │
└──────────────┬───────────────────────┘
               │
               ▼
┌──────────────────────────────────────┐
│  Tool Selection (LLM Decision)       │
│  → web_automate(task, url)           │
└──────────────┬───────────────────────┘
               │
               ▼
┌──────────────────────────────────────┐
│  BrowserAutomationEngine              │
│  ┌────────────┬──────────────┐       │
│  │ Playwright │ Vision AI     │       │
│  │ (DOM)      │ (Nova Pro)   │       │
│  └────────────┴──────────────┘       │
└──────────────┬───────────────────────┘
               │
               ▼
┌──────────────────────────────────────┐
│  Execution Flow:                     │
│  1. Navigate to URL                  │
│  2. Capture screenshot               │
│  3. Vision AI creates plan           │
│  4. Execute steps (click, type, etc) │
│  5. Verify success                   │
└──────────────────────────────────────┘
```

---

## 🔧 Technical Details

### Backend Selection

The system automatically chooses the best available backend:
1. **Playwright** (preferred) - Modern, fast, async API
2. **Selenium** (fallback) - Mature, widely supported

You can manually specify:
```python
async with BrowserAutomationEngine(backend="playwright") as browser:
    # Use Playwright specifically
    pass
```

### Vision AI Integration

Uses **AWS Bedrock Nova Pro** for:
- Page analysis and understanding
- Element location when DOM selectors fail
- Form structure analysis
- Data extraction from visual content

### Hybrid Approach

Example click operation:
1. **Try DOM selector** (fastest) - `button#submit`
2. **Try text matching** - "Submit" button
3. **Try vision AI** (fallback) - "Find the submit button and give me coordinates"

This ensures maximum reliability across different page types.

---

## 🎨 Customization

### Headless vs Visible Browser

**Visible (default)** - Good for debugging:
```python
BrowserAutomationEngine(headless=False)
```

**Headless** - Faster, no window:
```python
BrowserAutomationEngine(headless=True)
```

### Adjusting Wait Times

```python
# Wait for element with custom timeout
await browser.wait_for_element("#slow-element", timeout=10000)  # 10 seconds

# Add manual delays between actions
await asyncio.sleep(2)
```

### Custom JavaScript Execution

```python
# Execute custom JavaScript
result = await browser.execute_javascript(
    "return document.querySelector('.price').textContent"
)
```

---

## 🐛 Troubleshooting

### "Playwright not available"
```bash
pip install playwright
python -m playwright install chromium
```

### "Selenium WebDriver not found"
```bash
pip install selenium
# Selenium will auto-download chromedriver
```

### "Navigation timeout"
- Increase timeout in navigate() call
- Check internet connection
- Verify URL is accessible

### "Element not found"
- Vision fallback should automatically engage
- Check if element exists on page
- Try different selector strategies

### "Vision AI returns error"
- Verify AWS credentials in .env
- Check AWS_BEDROCK_MODEL is set correctly
- Ensure Nova Pro is enabled in your AWS region

---

## 📊 Performance Tips

### Speed Optimization

1. **Use specific selectors** - CSS selectors are fastest
2. **Minimize vision AI calls** - Use for complex cases only
3. **Batch operations** - Multiple actions in one call
4. **Headless mode** - Faster than visible browser

### Reliability Tips

1. **Use vision fallback** - Enable for critical interactions
2. **Add wait conditions** - Don't assume instant loads
3. **Verify success** - Check results after automation
4. **Handle errors gracefully** - Provide fallback strategies

---

## 🔐 Security Considerations

### Credentials Management

**Never hardcode passwords:**
```python
# ❌ BAD
web_automate("Login with password123", url)

# ✓ GOOD - use environment variables
password = os.getenv("MY_PASSWORD")
```

### Secure Form Filling

The vision AI automatically detects password fields and handles them securely. Sensitive data stays in memory and is never logged.

---

## 🚀 Advanced Features

### Multi-Tab Support (Future)

```python
# Open multiple pages
tab1 = await browser.new_page()
tab2 = await browser.new_page()

# Switch between tabs
await browser.switch_to_page(tab1)
```

### Session Persistence (Future)

```python
# Save browser state
await browser.save_session("twitter_logged_in")

# Load saved session
await browser.load_session("twitter_logged_in")
```

### CAPTCHA Handling (Future)

Integration with 2Captcha or similar services for automatic CAPTCHA solving.

---

## 📚 Examples Repository

Check `test_browser_automation.py` for complete working examples:
- Basic navigation
- Vision AI analysis
- Element interaction
- Form filling
- Data extraction
- Complete workflows

---

## 🤝 Integration with Existing Tools

Browser automation works seamlessly with existing Nivora tools:

```python
# Combined workflow example
1. web_search("best laptop 2024")  # Search query
2. browser_extract_data(url, "extract laptop names and prices")  # Extract data
3. take_note(f"Laptop research results: {data}")  # Save results
```

---

## 📝 Best Practices

### Do's ✅
- Use browser automation for complex web tasks
- Enable vision fallback for reliability
- Add appropriate wait times between actions
- Verify success after automation
- Handle errors gracefully

### Don'ts ❌
- Don't use for simple URL opening (use `open_website`)
- Don't skip error handling
- Don't hardcode sensitive data
- Don't ignore timeout errors
- Don't abuse automation (respect rate limits)

---

## 🎓 Learning Path

### Beginner
1. Run `test_browser_automation.py` to see capabilities
2. Try simple navigation and analysis
3. Practice with public websites (Wikipedia, Hacker News)

### Intermediate
4. Implement form filling workflows
5. Extract structured data
6. Build multi-step automation

### Advanced
7. Create custom automation flows
8. Integrate with other Nivora tools
9. Build complex data pipelines

---

## 🆘 Getting Help

### Check Logs
```bash
# Enable debug logging
export LOG_LEVEL=DEBUG
python agent.py start
```

### Test Individual Components
```bash
# Test specific features
python browser_automation.py  # Test engine directly
python test_browser_automation.py --test navigation  # Test specific capability
```

### Common Issues
- See troubleshooting section above
- Check GitHub issues
- Review error logs for details

---

## 🎉 Summary

You now have a **complete browser automation system** that:
- Combines DOM automation with AI vision
- Handles complex workflows automatically
- Works reliably across different websites
- Integrates seamlessly with Nivora's voice interface

**Ready to automate the web with just your voice! 🚀**

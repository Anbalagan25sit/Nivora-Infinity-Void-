# Notion Tool Setup Guide

## Overview
Complete Notion integration for Nivora voice agent with page creation, search, reading, database operations, and automatic logging.

## Features
- ✅ Create Notion pages with markdown content
- ✅ Search all accessible pages and databases
- ✅ Read full page content
- ✅ Add entries to Notion databases
- ✅ Append content to existing pages
- ✅ Auto-log agent output to "Nivora Notes"
- ✅ Voice command support
- ✅ Markdown formatting (headers, bullets, checkboxes)

## Quick Setup (5 minutes)

### 1. Create Notion Integration

1. **Go to Notion Integrations**:
   - Visit: https://www.notion.so/my-integrations
   - Sign in with your Notion account

2. **Create New Integration**:
   - Click **"+ New integration"**
   - Name: `Nivora Agent`
   - Associated workspace: Select your workspace
   - Click **"Submit"**

3. **Copy Integration Token**:
   - After creation, you'll see **"Internal Integration Token"**
   - Click **"Show"** then **"Copy"**
   - It starts with `secret_`

4. **Set Capabilities** (default settings are fine):
   - ✅ Read content
   - ✅ Update content
   - ✅ Insert content

### 2. Add Token to .env

Add to your `.env` file in project root:

```env
# Notion Integration
NOTION_API_KEY=secret_xxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Optional: Default database for quick task adding
NOTION_DEFAULT_DATABASE_ID=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Optional: Dedicated page for agent output logging
NOTION_NOTES_PAGE_ID=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

### 3. Share Pages with Integration

**IMPORTANT**: Your integration can only access pages you explicitly share with it.

1. **Open a Notion page** you want the agent to access
2. Click the **"..."** menu (top right)
3. Scroll down to **"Add connections"**
4. Find and select your **"Nivora Agent"** integration
5. Click **"Confirm"**

Repeat for any pages/databases you want accessible.

### 4. Install Dependencies

```bash
pip install notion-client python-dotenv
```

Or add to `requirements.txt`:
```txt
notion-client>=2.0.0
python-dotenv>=1.0.0
```

### 5. Test Connection

```bash
python agent/tools/setup_notion.py
```

This will verify:
- ✅ API key is valid
- ✅ Connection works
- ✅ List accessible pages

---

## Voice Command Examples

### Create Pages
```
"Create a Notion page about project ideas"
"Make a new Notion page called Meeting Notes with today's discussion"
```

### Search
```
"Search Notion for my project notes"
"Find my meeting notes in Notion"
"Search Notion for todo list"
```

### Read Pages
```
"Read my Notion page about project plan"
"What's in my Notion meeting notes?"
```

### Add to Database
```
"Add task 'Finish report' to my Notion database"
"Add a new project entry to Notion"
```

### Update Pages
```
"Add this to my Notion journal"
"Update my Notion notes with this info"
```

### Save Agent Output
```
"Save this to Notion"
"Remember this in Notion"
"Log this to my Nivora notes"
```

---

## Integration with Agents

### Add to multi_agent_livekit.py

```python
from agent.tools.notion_tool import NOTION_TOOLS

class AgentConfig:
    # Add to Infin (life management assistant)
    INFIN_TOOLS = [
        # ... existing tools ...
        *NOTION_TOOLS,
    ]

    # Or add to Nivora (technical companion)
    NIVORA_TOOLS = [
        # ... existing tools ...
        *NOTION_TOOLS,
    ]
```

### Update Agent Instructions

Add to `infin_prompts.py` or `prompts.py`:

```python
"""
## Notion Integration

You can interact with Notion for knowledge management:

### Available Commands:
- Create pages: "Create a Notion page about X"
- Search: "Search Notion for Y"
- Read pages: "Read my Notion page about Z"
- Add to database: "Add task to my Notion database"
- Update pages: "Add this to my Notion notes"
- Save output: "Save this to Notion" (auto-logs with timestamp)

### Markdown Support:
When creating/updating pages, you can use:
- # Heading 1, ## Heading 2, ### Heading 3
- - Bullet points or • Bullet points
- 1. Numbered lists
- [ ] Todo items, [x] Completed todos
- --- Dividers

### Examples:
User: "Create a Notion page for today's meeting"
You: create_notion_page(title="Meeting Notes - 2024-03-30", content="## Agenda\n- Project updates\n- Q1 review")

User: "Save this idea to Notion"
You: save_agent_output(title="Project Idea", content="[user's idea here]")
"""
```

---

## Function Reference

### 1. create_notion_page(title, content, parent_page_id=None)

Creates a new Notion page.

**Parameters:**
- `title` (str): Page title
- `content` (str): Page content (markdown supported)
- `parent_page_id` (str, optional): Parent page ID/URL

**Returns:** Success message with page URL

**Example:**
```python
create_notion_page(
    title="Project Ideas",
    content="# Ideas\n- Voice assistant\n- AI automation\n[ ] Research competitors"
)
```

**Markdown Support:**
- `# Heading 1`, `## Heading 2`, `### Heading 3`
- `- Bullet` or `• Bullet`
- `1. Numbered list`
- `[ ] Todo`, `[x] Done`
- `---` (divider)

---

### 2. search_notion(query)

Search all accessible pages and databases.

**Parameters:**
- `query` (str): Search query

**Returns:** List of matching pages with titles and URLs

**Example:**
```python
search_notion("project notes")
```

**Output:**
```
Search results for 'project notes':

1. Project Planning Notes
   URL: https://notion.so/...
   Type: page

2. Active Projects Database
   URL: https://notion.so/...
   Type: database
```

---

### 3. read_notion_page(page_id_or_url)

Read full content of a page.

**Parameters:**
- `page_id_or_url` (str): Page ID or full Notion URL

**Returns:** Page title and formatted content

**Example:**
```python
read_notion_page("https://notion.so/Project-Plan-abc123")
# or
read_notion_page("abc123-def456-...")
```

**Output:**
```
Page: Project Plan

# Overview
This is our Q1 project plan.

• Goal 1: Launch MVP
• Goal 2: Get 100 users
```

---

### 4. add_to_notion_database(database_id, properties)

Add a new entry/row to a database.

**Parameters:**
- `database_id` (str): Database ID or URL
- `properties` (dict): Property values as key-value pairs

**Returns:** Success message with entry URL

**Property Types:**
- Text/Title: `{"Name": "Task name"}`
- Select: `{"Status": "In Progress"}`
- Number: `{"Priority": 5}`
- Checkbox: `{"Done": False}`
- Date: `{"Due Date": "2024-03-30"}`

**Example:**
```python
add_to_notion_database(
    database_id="abc123...",
    properties={
        "Name": "Finish quarterly report",
        "Status": "In Progress",
        "Priority": 1,
        "Done": False,
        "Due Date": "2024-03-31"
    }
)
```

---

### 5. update_notion_page(page_id, content)

Append new content to existing page.

**Parameters:**
- `page_id` (str): Page ID or URL
- `content` (str): Content to append (markdown supported)

**Returns:** Success message

**Example:**
```python
update_notion_page(
    page_id="abc123...",
    content="## Update 2024-03-30\nCompleted first draft"
)
```

---

### 6. save_agent_output(title, content)

Save agent output to "Nivora Notes" page with auto-timestamp.

**Parameters:**
- `title` (str): Entry title/heading
- `content` (str): Content to save

**Returns:** Success message with timestamp

**Setup Required:**
1. Create a page called "Nivora Notes" in Notion
2. Share it with your integration
3. (Optional) Add page ID to .env as `NOTION_NOTES_PAGE_ID`

**Example:**
```python
save_agent_output(
    title="User Request",
    content="User asked about project timeline. Explained Q1 goals."
)
```

**Output in Notion:**
```
## User Request
*2024-03-30 14:30*

User asked about project timeline. Explained Q1 goals.

---
```

---

## Configuration Options

### .env Variables

```env
# Required
NOTION_API_KEY=secret_xxxxx

# Optional: Quick task adding
NOTION_DEFAULT_DATABASE_ID=abc123def456...

# Optional: Agent output logging
NOTION_NOTES_PAGE_ID=abc123def456...
```

### Getting Page/Database IDs

**From URL:**
```
https://notion.so/workspace/Page-Name-abc123def456ghi789
                                      ↑ This is the ID
```

**Clean format:**
```
abc123def456ghi789
↓
abc123de-f456-ghi7-89ab-cdef12345678
```

Tool automatically handles both formats!

---

## Common Use Cases

### 1. Morning Briefing Log

```python
# Save daily briefing to Notion
save_agent_output(
    title="Morning Briefing - 2024-03-30",
    content=f"""
## Email Summary
- 12 unread emails
- 2 urgent from boss

## Calendar
- 3 meetings today
- Project review at 2pm

## Weather
- Sunny, 72°F
"""
)
```

### 2. Meeting Notes

```python
create_notion_page(
    title="Team Standup - 2024-03-30",
    content="""
# Attendees
- Alice, Bob, Charlie

# Updates
- Alice: Finished API integration
- Bob: Working on frontend
- Charlie: Testing phase

# Action Items
[ ] Alice: Review Bob's PR
[ ] Bob: Fix navigation bug
[ ] Charlie: Write test cases
"""
)
```

### 3. Task Management

```python
# Add to your task database
add_to_notion_database(
    database_id=os.getenv("NOTION_DEFAULT_DATABASE_ID"),
    properties={
        "Task": "Prepare Q1 presentation",
        "Status": "Todo",
        "Priority": "High",
        "Due": "2024-04-01",
        "Assigned": "Me"
    }
)
```

### 4. Daily Journal

```python
# Append to journal page
update_notion_page(
    page_id="your-journal-page-id",
    content=f"""
## {datetime.now().strftime('%Y-%m-%d')}

### Accomplishments
- Completed 3 tasks
- Had productive meeting

### Learnings
- Discovered new approach to problem X

### Tomorrow
- Start new project
- Review team feedback
"""
)
```

---

## Troubleshooting

### "NOTION_API_KEY not found"
- Add to `.env` file in project root
- Format: `NOTION_API_KEY=secret_xxxxx`
- Get from: https://www.notion.so/my-integrations

### "No pages found" when searching
- Share pages with your integration:
  1. Open page in Notion
  2. Click "..." > "Add connections"
  3. Select your integration
- Integration can only access explicitly shared pages

### "Parent page not found" when creating
- Provide `parent_page_id` parameter
- Or share a workspace page as the parent
- Tool cannot create pages in workspace root without parent

### "Property not found" in database
- Check database schema for exact property names
- Property names are case-sensitive
- Use same names as shown in Notion

### "Invalid page ID"
- Tool accepts both formats:
  - Full URL: `https://notion.so/Page-Name-abc123`
  - Just ID: `abc123-def4-56gh-ij78-klmn90123456`
- Auto-extracts ID from URLs

### "Nivora Notes page not found"
- Create a page called "Nivora Notes"
- Share it with your integration
- Add ID to .env as `NOTION_NOTES_PAGE_ID` (optional)

---

## Security Notes

✅ **Integration Tokens:**
- Keep `NOTION_API_KEY` secret
- Don't commit to git (add `.env` to `.gitignore`)
- Regenerate if exposed

✅ **Permissions:**
- Integration only accesses shared pages
- Revoke access: Notion Settings > Connections
- Or delete integration at notion.so/my-integrations

✅ **Scope:**
- Read/write only (no admin access)
- Cannot modify workspace settings
- Cannot access unshared pages

---

## Advanced Features

### Custom Parent Pages

```python
# Create page under specific parent
create_notion_page(
    title="Sub-page",
    content="Content here",
    parent_page_id="parent-page-id-here"
)
```

### Database Filtering

```python
# The tool searches all accessible content
# For specific database queries, use Notion's native filters
```

### Bulk Operations

```python
# Add multiple tasks
tasks = [
    {"Name": "Task 1", "Status": "Todo"},
    {"Name": "Task 2", "Status": "In Progress"},
    {"Name": "Task 3", "Status": "Done"}
]

for task in tasks:
    add_to_notion_database(database_id, task)
```

---

## Integration with Other Tools

### Gmail + Notion

```python
# Save important emails to Notion
email_content = read_emails(query="is:important", max_results=1)
save_agent_output("Important Email", email_content)
```

### Calendar + Notion

```python
# Log today's meetings to Notion
events = get_calendar_events(days=1)
create_notion_page("Meeting Log - Today", events)
```

### Screen Share + Notion

```python
# Save screenshot analysis to Notion
analysis = describe_screen_share()
save_agent_output("Screen Analysis", analysis)
```

---

## Testing

### Test Connection
```bash
python agent/tools/setup_notion.py
```

### Test Functions Manually
```python
from agent.tools.notion_tool import *

# Search test
result = search_notion("test")
print(result)

# Create test page (requires parent_page_id)
result = create_notion_page(
    title="Test Page",
    content="# Hello\nThis is a test",
    parent_page_id="your-page-id"
)
print(result)
```

---

## Next Steps

1. ✅ Complete setup above
2. Add NOTION_TOOLS to agent config
3. Test with voice commands
4. Create "Nivora Notes" page for auto-logging
5. Set up task database for quick adding
6. Customize agent instructions

---

## Resources

- **Notion API Docs**: https://developers.notion.com/
- **My Integrations**: https://www.notion.so/my-integrations
- **Python Client**: https://github.com/ramnes/notion-sdk-py
- **API Reference**: https://developers.notion.com/reference

---

**Built for**: Nivora Multi-Agent Voice Assistant
**Framework**: LiveKit + AWS Bedrock + ElevenLabs
**API**: Notion API v1
**Language**: Python 3.8+

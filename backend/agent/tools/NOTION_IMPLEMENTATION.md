# Notion Tool - Complete Implementation Summary

## ✅ What Was Built

A complete Notion integration for Nivora's voice agent with 6 AI-callable functions for knowledge management, note-taking, and database operations.

### 📦 Functions

1. **create_notion_page** - Create pages with markdown content
2. **search_notion** - Search all accessible pages and databases
3. **read_notion_page** - Read full page content
4. **add_to_notion_database** - Add entries to databases
5. **update_notion_page** - Append content to existing pages
6. **save_agent_output** - Auto-log agent output with timestamps

## 📁 Files Created

```
agent/tools/
├── notion_tool.py              # Main Notion tool (550+ lines)
├── setup_notion.py             # Connection test script
├── test_notion.py              # Test suite
├── NOTION_SETUP.md             # Complete setup guide
└── NOTION_VOICE_COMMANDS.md    # Voice command reference
```

## 🎯 Key Features

### 1. Voice-Optimized Functions
- All functions registered as `@function_tool()` for LiveKit
- Natural language voice command support
- Formatted output optimized for TTS

### 2. Markdown Support
- Headers: `# H1`, `## H2`, `### H3`
- Bullets: `- item` or `• item`
- Numbered lists: `1. item`
- Checkboxes: `[ ]` and `[x]`
- Dividers: `---`

### 3. Smart Search & Access
- Search across all shared pages/databases
- Extract page IDs from URLs automatically
- Returns titles, URLs, and types

### 4. Database Operations
- Add entries with multiple property types
- Supports: text, number, select, date, checkbox
- Auto-detects database schema

### 5. Content Management
- Create pages with structured content
- Append to existing pages
- Read and parse page content

### 6. Auto-Logging
- Dedicated "Nivora Notes" page
- Auto-timestamps all entries
- Perfect for conversation history

## 🚀 Quick Setup (5 minutes)

### 1. Create Integration
```
1. Visit: https://www.notion.so/my-integrations
2. Click "New integration"
3. Name: "Nivora Agent"
4. Copy token (starts with secret_)
```

### 2. Add to .env
```env
NOTION_API_KEY=secret_xxxxxxxxxxxxxxxxxxxxx
```

### 3. Share Pages
```
1. Open Notion page
2. Click "..." > "Add connections"
3. Select "Nivora Agent"
```

### 4. Install & Test
```bash
pip install notion-client python-dotenv
python agent/tools/setup_notion.py
```

## 🎤 Voice Command Examples

### Create
```
"Create a Notion page about project ideas"
"Make a new page called Meeting Notes"
```

### Search
```
"Search Notion for my project notes"
"Find my todo list in Notion"
```

### Read
```
"Read my Notion page about project plan"
"What's in my meeting notes?"
```

### Database
```
"Add task 'Finish report' to Notion database"
```

### Update
```
"Add this to my Notion journal"
```

### Save
```
"Save this to Notion"
"Remember this in Notion"
```

## 🔧 Integration with Agents

### multi_agent_livekit.py
```python
from agent.tools.notion_tool import NOTION_TOOLS

class AgentConfig:
    INFIN_TOOLS = [
        *existing_tools,
        *NOTION_TOOLS,  # Add here
    ]
```

### Agent Instructions
```python
"""
## Notion Integration
- Create pages: "Create Notion page about X"
- Search: "Search Notion for Y"
- Read: "Read my Notion page about Z"
- Add to DB: "Add task to Notion"
- Update: "Add this to my notes"
- Save: "Save this to Notion" (auto-logs with timestamp)
"""
```

## 📊 Function Details

### create_notion_page(title, content, parent_page_id=None)
```python
# Create with markdown
create_notion_page(
    title="Project Ideas",
    content="""
# Main Ideas
- Voice assistant
- AI automation

## Next Steps
[ ] Research competitors
[ ] Build prototype
"""
)
```

**Returns**: Success message + page URL

### search_notion(query)
```python
search_notion("project notes")
```

**Returns**: List of matching pages with titles, URLs, types

### read_notion_page(page_id_or_url)
```python
# Accepts both formats
read_notion_page("https://notion.so/Page-abc123")
read_notion_page("abc123-def456-...")
```

**Returns**: Page title + formatted content

### add_to_notion_database(database_id, properties)
```python
add_to_notion_database(
    database_id="abc123...",
    properties={
        "Name": "Finish report",
        "Status": "In Progress",
        "Priority": 1,
        "Done": False,
        "Due Date": "2024-03-31"
    }
)
```

**Returns**: Success message + entry URL

### update_notion_page(page_id, content)
```python
update_notion_page(
    page_id="abc123...",
    content="## Update\nCompleted first draft"
)
```

**Returns**: Success message

### save_agent_output(title, content)
```python
save_agent_output(
    title="User Request",
    content="User asked about timeline. Explained Q1 goals."
)
```

**Creates Entry**:
```
## User Request
*2024-03-30 14:30*

User asked about timeline. Explained Q1 goals.

---
```

## 🎨 Common Use Cases

### 1. Meeting Notes
```python
create_notion_page(
    title="Team Standup - 2024-03-30",
    content="""
# Attendees
- Alice, Bob, Charlie

# Updates
- Alice: API integration done
- Bob: Frontend in progress

# Action Items
[ ] Review Bob's PR
[ ] Fix navigation bug
"""
)
```

### 2. Daily Journal
```python
update_notion_page(
    page_id="journal-page-id",
    content=f"""
## {datetime.now().strftime('%Y-%m-%d')}

### Accomplishments
- Completed 3 tasks
- Productive meeting

### Tomorrow
- Start new project
"""
)
```

### 3. Task Management
```python
add_to_notion_database(
    database_id="tasks-db-id",
    properties={
        "Task": "Prepare Q1 presentation",
        "Status": "Todo",
        "Priority": "High",
        "Due": "2024-04-01"
    }
)
```

### 4. Knowledge Base
```python
# Save research findings
save_agent_output(
    title="React Best Practices",
    content="[AI-generated research summary]"
)
```

## 🔐 Configuration

### Required
```env
NOTION_API_KEY=secret_xxxxx
```

### Optional
```env
# For quick task adding
NOTION_DEFAULT_DATABASE_ID=abc123...

# For agent output logging
NOTION_NOTES_PAGE_ID=def456...
```

## 🧪 Testing

### Test Suite
```bash
python agent/tools/test_notion.py
```

Tests:
1. ✅ API key configuration
2. ✅ API connection
3. ✅ Search function
4. ✅ Accessible pages
5. ✅ Function signatures

### Manual Test
```python
from agent.tools.notion_tool import search_notion

result = search_notion("test")
print(result)
```

## 🔗 Integration with Other Tools

### Gmail + Notion
```python
# Save important emails
emails = read_emails(query="is:important")
save_agent_output("Important Emails", emails)
```

### Calendar + Notion
```python
# Create meeting pages
events = get_calendar_events(days=1)
for event in events:
    create_notion_page(f"Meeting: {event['title']}", "")
```

### Web Search + Notion
```python
# Save research
results = web_search("React trends 2024")
save_agent_output("React Research", results)
```

### Screen Share + Notion
```python
# Log screen analysis
analysis = describe_screen_share()
save_agent_output("Screen Analysis", analysis)
```

## 📋 Workflow Examples

### Morning Routine
```
User: "Good morning Infin"
Agent: [Email + calendar summary]
User: "Save that to Notion"
Agent: [Logs to Nivora Notes]
```

### Research Flow
```
User: "Search the web for X"
Agent: [Results]
User: "Save top 3 to Notion"
Agent: [Creates page with findings]
```

### Task Creation
```
User: "Add these tasks to Notion:
finish report, review code, send emails"
Agent: [Adds 3 tasks to database]
```

### Knowledge Capture
```
User: "I just learned X"
Agent: "Tell me more"
User: [Explains]
User: "Save that to Notion"
Agent: [Auto-logs with timestamp]
```

## ⚠️ Troubleshooting

### "No pages found"
**Fix**: Share pages with integration
1. Open page in Notion
2. Click "..." > "Add connections"
3. Select your integration

### "Parent page not found"
**Fix**: Provide parent_page_id when creating pages

### "Property not found"
**Fix**: Check database schema for exact property names (case-sensitive)

### "Invalid page ID"
**Fix**: Tool auto-handles URLs and IDs, but verify format

### "Nivora Notes page not found"
**Fix**:
1. Create "Nivora Notes" page
2. Share with integration
3. Add ID to .env as NOTION_NOTES_PAGE_ID

## 📈 Feature Highlights

### ✅ Markdown Conversion
Automatically converts markdown to Notion blocks:
- Headers → Notion headings
- Bullets → Notion bullet lists
- Numbers → Notion numbered lists
- Checkboxes → Notion to-do items
- Dividers → Notion dividers

### ✅ Block Parsing
Converts Notion blocks back to readable text:
- Preserves structure
- Formats for voice readout
- Handles nested content

### ✅ ID Extraction
Auto-extracts page IDs from URLs:
```
https://notion.so/Page-abc123def456
→ abc123de-f456-def4-56ab-cdef12345678
```

### ✅ Property Mapping
Auto-detects database schema and maps properties:
- Text → rich_text
- Numbers → number
- Select → select
- Dates → date
- Checkboxes → checkbox

## 🎓 Best Practices

### 1. Share Pages First
Always share pages before trying to access them

### 2. Use Save for Quick Capture
Let agent log important outputs automatically

### 3. Structure with Markdown
Use headers, bullets, and checkboxes for clarity

### 4. Reference by Name
"My project notes" is easier than page IDs

### 5. Create Templates
Set up page templates for recurring use cases

## 📚 Documentation

- **NOTION_SETUP.md** - Complete setup guide
- **NOTION_VOICE_COMMANDS.md** - Voice command reference
- **notion_tool.py** - Source code with docstrings
- **test_notion.py** - Test examples

## 🔜 Future Enhancements

Possible additions:
- [ ] Block-level editing
- [ ] Database filtering/sorting
- [ ] Page templates
- [ ] Linked pages/databases
- [ ] Comments support
- [ ] File attachments
- [ ] Emoji support
- [ ] Page archiving

## 📦 Dependencies

```txt
notion-client>=2.0.0
python-dotenv>=1.0.0
```

Already added to requirements.txt!

## 🎉 Ready to Use!

Your complete Notion integration is ready:

1. ✅ 6 voice-enabled functions
2. ✅ Markdown support
3. ✅ Database operations
4. ✅ Auto-logging
5. ✅ Comprehensive docs
6. ✅ Test suite

**Total setup time**: ~5 minutes ⚡

---

**Next Steps**:

1. Create integration at notion.so/my-integrations
2. Add API key to .env
3. Share pages with integration
4. Run: `python agent/tools/setup_notion.py`
5. Add NOTION_TOOLS to agent config
6. Try: *"Search Notion for my notes"*

---

**Built for**: Nivora Multi-Agent Voice Assistant
**Framework**: LiveKit + AWS Bedrock + ElevenLabs
**API**: Notion API v1
**Language**: Python 3.8+
**License**: Same as Nivora project

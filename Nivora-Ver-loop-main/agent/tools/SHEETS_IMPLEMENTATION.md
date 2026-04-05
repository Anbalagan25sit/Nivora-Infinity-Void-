# Google Sheets Tool - Complete Implementation Summary

## ✅ What Was Built

A complete Google Sheets integration for Nivora's voice agent that reuses the existing Gmail OAuth token. 6 voice-enabled functions for spreadsheet management.

### 📦 Functions

1. **read_sheet** - Read data from any spreadsheet
2. **write_to_sheet** - Write to specific cells
3. **append_row** - Add rows for logging/tracking
4. **search_sheet** - Search across all cells
5. **create_spreadsheet** - Create new spreadsheets
6. **get_sheet_summary** - Get sheet info (rows, columns, headers)

## 📁 Files Created

```
agent/tools/
├── sheets_tool.py          # Main Sheets tool (500+ lines)
├── setup_sheets.py         # Token update script
└── SHEETS_SETUP.md         # Complete setup guide
```

## 🎯 Key Features

### 1. Token Reuse
- ✅ Shares Gmail OAuth token
- ✅ Adds Sheets scope to existing token
- ✅ One token for both APIs
- ✅ Auto-refresh preserved

### 2. Voice-Optimized
- ✅ All functions as `@function_tool()`
- ✅ Natural language commands
- ✅ Formatted output for TTS

### 3. Flexible Input
- ✅ Accepts full Google Sheets URLs
- ✅ Accepts spreadsheet IDs
- ✅ Auto-extracts IDs from URLs

### 4. Smart Formatting
- ✅ Tables formatted for voice readout
- ✅ Limits rows/columns for brevity
- ✅ Clear row/column labels

### 5. Comprehensive Operations
- ✅ Read any range (A1 notation)
- ✅ Write single cells or ranges
- ✅ Append rows (perfect for logging)
- ✅ Search all sheets
- ✅ Create new spreadsheets
- ✅ Get metadata/summaries

## 🚀 Quick Setup (3 minutes)

```bash
# 1. Enable Sheets API
Visit: https://console.cloud.google.com/apis/library
Search "Google Sheets API" → Enable

# 2. Add Sheets scope to OAuth
Visit: https://console.cloud.google.com/apis/credentials/consent
Edit app → Scopes → Add:
☑ https://www.googleapis.com/auth/spreadsheets

# 3. Update token
python agent/tools/setup_sheets.py

# Done! Both Gmail and Sheets work now.
```

## 🎤 Voice Command Examples

### Read
```
"Read my expenses sheet"
"Show me the data in my tracker"
```

### Append
```
"Add a row to my tracker: today, exercise, done"
"Log this to my expenses: groceries, 45.50"
```

### Search
```
"Search my sheet for Nivora"
"Find Alice in my spreadsheet"
```

### Create
```
"Create a new spreadsheet called Project Tracker"
```

### Summary
```
"How many rows are in my sheet?"
"What sheets are in my spreadsheet?"
```

## 🔗 Integration

**Add to agents:**
```python
from agent.tools.sheets_tool import SHEETS_TOOLS

INFIN_TOOLS = [*existing_tools, *SHEETS_TOOLS]
```

**Update instructions:**
```python
"""
## Google Sheets
- Read: "Read my expenses sheet"
- Append: "Add row: date, task, done"
- Search: "Search my sheet for X"
- Create: "Create spreadsheet Y"
- Summary: "How many rows?"
"""
```

## 📊 Function Details

### read_sheet(spreadsheet_id, range="Sheet1!A1:Z100")
```python
# Read entire sheet
read_sheet("1abc123...")

# Read specific range
read_sheet("1abc123...", "Sheet1!A1:B10")

# Read by URL
read_sheet("https://docs.google.com/spreadsheets/d/1abc123...")
```

**Returns:** Formatted table with row numbers

---

### write_to_sheet(spreadsheet_id, range, values)
```python
# Write headers
write_to_sheet(
    "1abc123...",
    "Sheet1!A1",
    [["Name", "Score", "Grade"]]
)

# Write multiple rows
write_to_sheet(
    "1abc123...",
    "Sheet1!A2",
    [
        ["Alice", 95, "A"],
        ["Bob", 87, "B"]
    ]
)
```

**Returns:** Success message with cells updated

---

### append_row(spreadsheet_id, values, sheet_name="Sheet1")
```python
# Log habit
append_row(
    "1abc123...",
    ["2024-03-30", "Exercise", "Yes", "30 min"]
)

# Track expense
append_row(
    "1abc123...",
    ["2024-03-30", "Coffee", 5.50, "Starbucks"]
)
```

**Returns:** Success message with row number

**Perfect for:**
- Daily habit tracking
- Expense logging
- Task completion logs
- Time tracking
- Journal entries

---

### search_sheet(spreadsheet_id, query)
```python
search_sheet("1abc123...", "Alice")
```

**Returns:** Matching rows with sheet names and row numbers

---

### create_spreadsheet(title)
```python
create_spreadsheet("Habit Tracker 2024")
```

**Returns:** Spreadsheet ID and URL

---

### get_sheet_summary(spreadsheet_id)
```python
get_sheet_summary("1abc123...")
```

**Returns:**
```
Spreadsheet: My Tracker

Sheet: Habits
  Rows: 100, Columns: 5
  Headers: Date, Activity, Completed

Sheet: Goals
  Rows: 20, Columns: 3
  Headers: Goal, Status, Due Date
```

## 🎨 Common Use Cases

### 1. Habit Tracker

**Voice:**
```
User: "Log today's habits: exercise yes, reading yes"

Agent: append_row(
    habits_id,
    ["2024-03-30", "Yes", "Yes", "Good day"]
)
```

### 2. Expense Tracking

**Voice:**
```
User: "Add expense: groceries, 45 dollars"

Agent: append_row(
    expenses_id,
    ["2024-03-30", "Groceries", 45.00, "Food"]
)
```

### 3. Project Tracking

**Voice:**
```
User: "Add project task: API integration, in progress, Alice"

Agent: append_row(
    projects_id,
    ["API integration", "In Progress", "Alice", "2024-04-15"]
)
```

### 4. Meeting Notes

**Voice:**
```
User: "Log meeting: team standup, discussed Q2 goals"

Agent: append_row(
    meetings_id,
    ["2024-03-30", "Team Standup", "Q2 goals discussion"]
)
```

### 5. Daily Journal

**Voice:**
```
User: "Add journal entry: productive day, finished 3 tasks"

Agent: append_row(
    journal_id,
    ["2024-03-30", "Productive day, finished 3 tasks", "Happy"]
)
```

## 🔧 Configuration

**No extra env vars needed!** Uses existing Gmail token.

**Optional** - Store common sheet IDs:
```env
HABITS_SHEET_ID=1abc123...
EXPENSES_SHEET_ID=1def456...
PROJECTS_SHEET_ID=1ghi789...
```

## 🔑 OAuth Scopes

Setup script adds Sheets scope to existing Gmail token:

```python
SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',      # NEW
    'https://www.googleapis.com/auth/gmail.send',        # Existing
    'https://www.googleapis.com/auth/gmail.readonly',    # Existing
    'https://www.googleapis.com/auth/gmail.modify'       # Existing
]
```

One token, multiple APIs! 🎉

## 📋 Range Notation

### Examples:
```
"Sheet1!A1"           → Single cell
"Sheet1!A1:B10"       → Rectangle
"Sheet1!A:A"          → Entire column
"Sheet1!1:1"          → Entire row
"Sheet1!A:C"          → Multiple columns
"Data!A1:Z100"        → Range in "Data" sheet
```

## 🔗 Integration with Other Tools

### Gmail + Sheets
```python
# Log important emails
emails = read_emails(query="is:important")
append_row(log_id, ["2024-03-30", "Email check", emails])
```

### Calendar + Sheets
```python
# Log today's meetings
events = get_calendar_events(days=1)
for event in events:
    append_row(meetings_id, [event['date'], event['title']])
```

### Notion + Sheets
```python
# Backup Notion to Sheets
notion_data = read_notion_page(page_id)
write_to_sheet(backup_id, "A1", [[notion_data]])
```

## ⚠️ Troubleshooting

### "Sheets API has not been enabled"
**Fix**: Enable in Google Cloud Console
- https://console.cloud.google.com/apis/library
- Search "Google Sheets API" → Enable

### "Insufficient permissions"
**Fix**: Add scope to OAuth consent screen
1. https://console.cloud.google.com/apis/credentials/consent
2. Edit app → Scopes
3. Add: `https://www.googleapis.com/auth/spreadsheets`
4. Run setup script again

### "Invalid spreadsheet ID"
**Fix**: Use full URL or correct ID format
- Tool auto-extracts from URLs!
- From URL: 44-char ID between `/d/` and `/edit`

### Gmail stops working
**Fix**: Shouldn't happen! Setup preserves Gmail scopes
- Run setup script again to verify

## 🧪 Testing

```bash
python agent/tools/setup_sheets.py
```

Tests:
1. ✅ Prerequisites check
2. ✅ Token update
3. ✅ Sheets API access
4. ✅ Gmail still works
5. ✅ Creates test spreadsheet

## 📚 Documentation

- **SHEETS_SETUP.md** - Complete setup guide with examples

## 🎉 Ready to Use!

Everything is production-ready:
1. ✅ 6 voice-enabled functions
2. ✅ Token reuse (Gmail + Sheets)
3. ✅ Auto token refresh
4. ✅ URL handling
5. ✅ Error handling
6. ✅ Complete documentation

**Total setup time**: ~3 minutes ⚡

---

## 📖 Quick Start

1. Enable Sheets API in Google Cloud Console
2. Add Sheets scope to OAuth consent screen:
   ```
   https://www.googleapis.com/auth/spreadsheets
   ```
3. Run: `python agent/tools/setup_sheets.py`
4. Add `*SHEETS_TOOLS` to agent config
5. Try: *"Create a spreadsheet called Test"*
6. Try: *"Add a row: test data"*

---

## 🔄 Token Flow

```
Existing Gmail Token
       ↓
Add Sheets Scope
       ↓
Re-authenticate (browser opens)
       ↓
New Token with Both APIs
       ↓
Saved to ~/.nivora/gmail_token.json
       ↓
Both Gmail and Sheets work!
```

## ✨ Advanced Features

### Formulas
```python
write_to_sheet(id, "D10", [["=SUM(D2:D9)"]])
```

### Batch Operations
```python
write_to_sheet(id, "A2", [
    ["Alice", 95],
    ["Bob", 87],
    ["Charlie", 92]
])
```

### Multiple Sheets
```python
append_row(id, ["Data"], sheet_name="January")
append_row(id, ["Data"], sheet_name="February")
```

---

**Built for**: Nivora Multi-Agent Voice Assistant
**Framework**: LiveKit + AWS Bedrock + ElevenLabs
**API**: Google Sheets API v4
**Language**: Python 3.8+
**Token**: Shared with Gmail OAuth

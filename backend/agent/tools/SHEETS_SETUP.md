# Google Sheets Tool Setup Guide

## Overview
Complete Google Sheets integration for Nivora voice agent. Reuses existing Gmail OAuth token by adding Sheets scope.

## Features
- ✅ Read sheet data with voice commands
- ✅ Write to specific cells
- ✅ Append rows for logging/tracking
- ✅ Search across all cells
- ✅ Create new spreadsheets
- ✅ Get sheet summaries
- ✅ Reuses Gmail OAuth token
- ✅ Auto token refresh

## Quick Setup (3 minutes)

### 1. Enable Google Sheets API

1. **Go to Google Cloud Console**:
   - https://console.cloud.google.com/apis/library
   - Use same project as Gmail

2. **Enable Sheets API**:
   - Search for "Google Sheets API"
   - Click on it
   - Click **"Enable"**

### 2. Add Sheets Scope to OAuth Consent

**CRITICAL**: Must add scope to consent screen!

1. **Go to OAuth Consent Screen**:
   - https://console.cloud.google.com/apis/credentials/consent

2. **Edit your app** (the one you created for Gmail)

3. **Go to "Scopes" page**:
   - Click "Add or Remove Scopes"
   - Search for "sheets"
   - Check:
     ```
     ☑ .../auth/spreadsheets
     ```
   - Click "Update"
   - Click "Save and Continue"

4. **Keep existing Gmail scopes** too:
   - .../auth/gmail.send
   - .../auth/gmail.readonly
   - .../auth/gmail.modify

### 3. Run Setup Script

```bash
python agent/tools/setup_sheets.py
```

This will:
1. ✅ Check prerequisites
2. ✅ Update your OAuth token with Sheets scope
3. ✅ Test Sheets API access
4. ✅ Verify Gmail still works
5. ✅ Create a test spreadsheet

**Note**: Browser will open for re-authorization (quick, just click "Allow")

### 4. Integration Complete!

Both Gmail and Sheets now share the same token in `~/.nivora/gmail_token.json`

---

## Voice Command Examples

### Read Sheets
```
"Read my expenses sheet"
"Show me the data in my tracker"
"What's in my project sheet?"
```

### Append Rows
```
"Add a row to my tracker: today, finish report, done"
"Log this to my expenses: groceries, 45.50, food"
"Append to my habit tracker: March 30, exercise, yes"
```

### Search
```
"Search my sheet for Nivora"
"Find Alice in my spreadsheet"
"Look for expenses over 100"
```

### Create
```
"Create a new spreadsheet called Project Tracker"
"Make a new sheet for my expenses"
```

### Summary
```
"How many rows are in my sheet?"
"What sheets are in my spreadsheet?"
"Give me a summary of my tracker"
```

---

## Integration with Agents

### Add to multi_agent_livekit.py

```python
from agent.tools.sheets_tool import SHEETS_TOOLS

class AgentConfig:
    # Add to Infin (life management assistant)
    INFIN_TOOLS = [
        # ... existing tools ...
        *SHEETS_TOOLS,
    ]

    # Or add to Nivora (technical companion)
    NIVORA_TOOLS = [
        # ... existing tools ...
        *SHEETS_TOOLS,
    ]
```

### Update Agent Instructions

Add to `infin_prompts.py`:

```python
"""
## Google Sheets Integration

You can manage spreadsheets with voice commands:

### Available Commands:
- Read: "Read my expenses sheet"
- Append: "Add row to my tracker: date, task, status"
- Search: "Search my sheet for X"
- Create: "Create spreadsheet called Y"
- Summary: "How many rows in my sheet?"
- Write: "Update cell A1 with total"

### Examples:
User: "Add to my habit tracker: today, exercise, done"
You: append_row(spreadsheet_id, ["2024-03-30", "exercise", "done"])

User: "How many rows in my expenses?"
You: get_sheet_summary(spreadsheet_id)

User: "Search my sheet for coffee"
You: search_sheet(spreadsheet_id, "coffee")
"""
```

---

## Function Reference

### 1. read_sheet(spreadsheet_id, range="Sheet1!A1:Z100")

Read data from a spreadsheet.

**Parameters:**
- `spreadsheet_id` (str): Sheet ID or full URL
- `range` (str): A1 notation range (default: "Sheet1!A1:Z100")

**Returns:** Formatted table as string

**Examples:**
```python
# Read entire sheet
read_sheet("abc123...")

# Read specific range
read_sheet("abc123...", "Sheet1!A1:B10")

# Read by URL
read_sheet("https://docs.google.com/spreadsheets/d/abc123...")

# Read specific columns
read_sheet("abc123...", "Data!A:C")
```

**Output:**
```
Spreadsheet: My Expenses
Range: Sheet1!A1:Z100

Row 1: Date, Category, Amount, Notes
Row 2: 2024-03-29, Food, 45.50, Groceries
Row 3: 2024-03-29, Transport, 12.00, Uber
...
```

---

### 2. write_to_sheet(spreadsheet_id, range, values)

Write data to specific cells.

**Parameters:**
- `spreadsheet_id` (str): Sheet ID or URL
- `range` (str): Target range in A1 notation
- `values` (list): 2D array of values

**Returns:** Success message with cells updated

**Examples:**
```python
# Write headers
write_to_sheet(
    "abc123...",
    "Sheet1!A1",
    [["Name", "Score", "Grade"]]
)

# Write multiple rows
write_to_sheet(
    "abc123...",
    "Sheet1!A2",
    [
        ["Alice", 95, "A"],
        ["Bob", 87, "B"]
    ]
)

# Update single cell
write_to_sheet(
    "abc123...",
    "Sheet1!D10",
    [[sum_total]]
)
```

---

### 3. append_row(spreadsheet_id, values, sheet_name="Sheet1")

Append a new row at the bottom of data.

**Parameters:**
- `spreadsheet_id` (str): Sheet ID or URL
- `values` (list): List of values for new row
- `sheet_name` (str): Sheet name (default: "Sheet1")

**Returns:** Success message with row number

**Examples:**
```python
# Log habit
append_row(
    "abc123...",
    ["2024-03-30", "Exercise", "Yes", "30 min"]
)

# Track expense
append_row(
    "abc123...",
    ["2024-03-30", "Coffee", 5.50, "Starbucks"]
)

# Add to specific sheet
append_row(
    "abc123...",
    ["Data entry"],
    sheet_name="March"
)
```

**Perfect for:**
- Daily habit tracking
- Expense logging
- Task completion logs
- Time tracking
- Journal entries

---

### 4. search_sheet(spreadsheet_id, query)

Search for a value across all cells.

**Parameters:**
- `spreadsheet_id` (str): Sheet ID or URL
- `query` (str): Search term

**Returns:** Matching rows with row numbers

**Examples:**
```python
# Find by name
search_sheet("abc123...", "Alice")

# Find by category
search_sheet("abc123...", "Food")

# Find by amount
search_sheet("abc123...", "100")
```

**Output:**
```
Found 3 match(es) for 'Food':

Sheet: Expenses, Row 2: 2024-03-29, Food, 45.50
Sheet: Expenses, Row 5: 2024-03-30, Food, 23.00
Sheet: March, Row 12: Food budget: $500
```

---

### 5. create_spreadsheet(title)

Create a new Google Spreadsheet.

**Parameters:**
- `title` (str): Spreadsheet title

**Returns:** Success message with ID and URL

**Examples:**
```python
# Create new tracker
create_spreadsheet("Habit Tracker 2024")

# Create project sheet
create_spreadsheet("Q2 Project Plan")
```

**Output:**
```
Created spreadsheet 'Habit Tracker 2024'
ID: 1abc123def456...
URL: https://docs.google.com/spreadsheets/d/1abc123...
```

---

### 6. get_sheet_summary(spreadsheet_id)

Get summary information about a spreadsheet.

**Parameters:**
- `spreadsheet_id` (str): Sheet ID or URL

**Returns:** Sheet names, row counts, headers

**Examples:**
```python
get_sheet_summary("abc123...")
```

**Output:**
```
Spreadsheet: My Tracker

Sheet: Habits
  Rows: 100, Columns: 5
  Headers: Date, Activity, Completed, Duration, Notes

Sheet: Goals
  Rows: 20, Columns: 3
  Headers: Goal, Status, Due Date
```

---

## Common Use Cases

### 1. Habit Tracker

**Setup:**
```python
# Create tracker
create_spreadsheet("Daily Habits")

# Add headers
write_to_sheet(
    id,
    "Sheet1!A1",
    [["Date", "Exercise", "Reading", "Meditation", "Notes"]]
)
```

**Daily logging:**
```
User: "Log today's habits: exercise yes, reading yes, meditation no"

Agent: [Parses and calls]
append_row(id, ["2024-03-30", "Yes", "Yes", "No", "Busy day"])
```

---

### 2. Expense Tracking

**Voice command:**
```
User: "Add expense: groceries, 45.50, food category"

Agent: append_row(
    expenses_id,
    ["2024-03-30", "Groceries", 45.50, "Food"]
)
```

**Monthly review:**
```
User: "How much did I spend on food this month?"

Agent: [Reads sheet, filters for "Food", sums amounts]
search_sheet(expenses_id, "Food")
```

---

### 3. Project Tracking

**Create project sheet:**
```python
create_spreadsheet("Q2 Projects")

write_to_sheet(
    id,
    "Sheet1!A1",
    [["Project", "Status", "Owner", "Due Date", "Priority"]]
)
```

**Add tasks:**
```
User: "Add project: API integration, in progress, Alice, April 15, high"

Agent: append_row(
    id,
    ["API integration", "In Progress", "Alice", "2024-04-15", "High"]
)
```

---

### 4. Meeting Notes Logger

**Voice flow:**
```
User: [After meeting] "Log this meeting: Team standup, discussed Q2 goals"

Agent: append_row(
    meeting_notes_id,
    ["2024-03-30", "Team Standup", "Discussed Q2 goals, action items assigned"]
)
```

---

### 5. Daily Journal

**Setup:**
```python
create_spreadsheet("Daily Journal 2024")
write_to_sheet(id, "A1", [["Date", "Entry", "Mood", "Highlights"]])
```

**Voice logging:**
```
User: "Add journal entry: Today was productive, finished 3 tasks, feeling good"

Agent: append_row(
    id,
    ["2024-03-30", "Productive day, finished 3 tasks", "Good", "Completed project milestone"]
)
```

---

## Getting Spreadsheet IDs

### Method 1: From URL

```
https://docs.google.com/spreadsheets/d/1abc123def456ghi789/edit
                                      ↑ This is the ID
```

Tool auto-extracts from full URLs!

### Method 2: Create with Voice

```
User: "Create a new spreadsheet called My Tracker"

Agent: [Returns]
"Created spreadsheet 'My Tracker'
ID: 1abc123def456ghi789
URL: https://docs.google.com/spreadsheets/d/..."

User: "Save that ID as my tracker"

Agent: [Stores in context or env var]
```

### Method 3: Store in .env

```env
# Common spreadsheets
HABITS_SHEET_ID=1abc123...
EXPENSES_SHEET_ID=1def456...
PROJECTS_SHEET_ID=1ghi789...
```

Then reference by variable name in code.

---

## Range Notation (A1 Format)

### Single Cell
```
"Sheet1!A1"           → Cell A1
"Data!B5"             → Cell B5 in "Data" sheet
```

### Cell Ranges
```
"Sheet1!A1:B10"       → Rectangle A1 to B10
"Sheet1!A:A"          → Entire column A
"Sheet1!1:1"          → Entire row 1
"Sheet1!A:C"          → Columns A through C
"Sheet1!1:10"         → Rows 1 through 10
```

### Multiple Sheets
```
"Sheet1!A1:B10"       → Range in Sheet1
"Data!A:C"            → Columns in Data sheet
```

### Pro Tips
- Use `!A:Z` for "all data"
- Use `!A1:Z100` to limit rows for voice readout
- Use `!1:1` to read just headers

---

## Troubleshooting

### "Sheets API has not been enabled"
**Fix**: Enable Google Sheets API in Google Cloud Console
- Go to: https://console.cloud.google.com/apis/library
- Search "Google Sheets API"
- Click "Enable"

### "Insufficient permissions" or "Access not granted"
**Fix**: Add Sheets scope to OAuth consent screen
1. Go to: https://console.cloud.google.com/apis/credentials/consent
2. Edit app > Scopes
3. Add: `https://www.googleapis.com/auth/spreadsheets`
4. Save
5. Run setup script again

### "Invalid spreadsheet ID"
**Fix**: Verify ID format
- From URL: Extract 44-character ID between `/d/` and `/edit`
- Tool handles both URLs and IDs automatically

### "Range not found" or "Sheet not found"
**Fix**: Check sheet names
- Sheet names are case-sensitive
- Default is "Sheet1" not "sheet1"
- Use `get_sheet_summary()` to see available sheets

### Gmail stops working after Sheets setup
**Fix**: Shouldn't happen! Setup preserves Gmail scopes
- Run: `python agent/tools/setup_sheets.py` again
- Verify both APIs work in setup output

---

## Integration with Other Tools

### Gmail + Sheets
```python
# Save email summary to sheet
emails = read_emails(query="is:important", max_results=5)
append_row(log_sheet_id, ["2024-03-30", "Email check", emails])
```

### Calendar + Sheets
```python
# Log today's meetings to sheet
events = get_calendar_events(days=1)
for event in events:
    append_row(meetings_sheet_id, [
        event['date'],
        event['title'],
        event['duration']
    ])
```

### Notion + Sheets
```python
# Export Notion data to Sheets
notion_data = read_notion_page(page_id)
write_to_sheet(backup_sheet_id, "A1", [[notion_data]])
```

---

## Advanced Usage

### Batch Operations

```python
# Write multiple rows at once
rows = [
    ["Alice", 95, "A"],
    ["Bob", 87, "B"],
    ["Charlie", 92, "A"]
]
write_to_sheet(sheet_id, "Sheet1!A2", rows)
```

### Formulas

```python
# Write formula to calculate sum
write_to_sheet(
    sheet_id,
    "D10",
    [["=SUM(D2:D9)"]]
)
```

### Multiple Sheets

```python
# Append to different sheets
append_row(sheet_id, ["Data 1"], sheet_name="January")
append_row(sheet_id, ["Data 2"], sheet_name="February")
```

---

## Security Notes

✅ **OAuth Token:**
- Shared with Gmail (one token for both)
- Stored in `~/.nivora/gmail_token.json`
- Auto-refreshes when expired
- Never commit to git

✅ **Permissions:**
- Full read/write access to your sheets
- Can create new spreadsheets
- Cannot access other Google services (Drive, Docs, etc.)

✅ **Revoke Access:**
1. Go to: https://myaccount.google.com/permissions
2. Find your integration
3. Click "Remove Access"

---

## Testing

### Test Suite
```bash
# Test connection and functions
python agent/tools/test_sheets.py
```

### Manual Test
```python
from agent.tools.sheets_tool import create_spreadsheet, append_row

# Create test sheet
result = create_spreadsheet("Test Sheet")
print(result)

# Get ID from result, then append
sheet_id = "1abc123..."
append_row(sheet_id, ["Test", "Data"])
```

---

## Dependencies

Already included in requirements.txt!

```txt
google-api-python-client>=2.100.0
google-auth>=2.23.0
google-auth-oauthlib>=1.1.0
google-auth-httplib2>=0.1.1
```

---

## Next Steps

1. ✅ Enable Sheets API
2. ✅ Add scope to OAuth consent
3. ✅ Run: `python agent/tools/setup_sheets.py`
4. ✅ Add SHEETS_TOOLS to agent config
5. ✅ Try: *"Create a spreadsheet called Test"*
6. ✅ Try: *"Add a row: test data"*

---

**Built for**: Nivora Multi-Agent Voice Assistant
**Framework**: LiveKit + AWS Bedrock + ElevenLabs
**API**: Google Sheets API v4
**Language**: Python 3.8+

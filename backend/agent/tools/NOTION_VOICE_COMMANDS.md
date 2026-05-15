# Notion Voice Commands Quick Reference

## 📝 Create Pages

```
"Create a Notion page about project ideas"
"Make a new Notion page called Meeting Notes"
"Create a page in Notion for today's standup"
```

**With Content:**
```
"Create a Notion page called TODO with these tasks:
finish report, review code, send emails"
```

**With Markdown:**
```
"Create a Notion page with:
heading one Project Plan
bullet point Research phase
bullet point Development phase
checkbox Review documentation"
```

---

## 🔍 Search

```
"Search Notion for my project notes"
"Find my meeting notes in Notion"
"Search Notion for todo list"
"Look up customer feedback in Notion"
"Find pages about Q1 planning"
```

---

## 📖 Read Pages

```
"Read my Notion page about project plan"
"What's in my Notion meeting notes?"
"Show me the content of my Notion journal"
"Read the Notion page about API documentation"
```

**After Search:**
```
User: "Search Notion for project plan"
Agent: [Returns search results with URLs]

User: "Read the first one"
Agent: [Reads page content]
```

---

## 📊 Add to Database

```
"Add task 'Finish quarterly report' to my Notion database"
"Add a new project entry to Notion"
"Create a task in Notion: Review pull requests, high priority"
```

**With Properties:**
```
"Add to my Notion database:
Name: Complete presentation
Status: In Progress
Priority: High
Due date: March 31"
```

---

## ✏️ Update/Append

```
"Add this to my Notion journal"
"Update my Notion notes with this info"
"Append this to my project notes in Notion"
```

**Daily Logging:**
```
"Add to my daily log:
Completed 3 tasks today,
had productive meeting with team,
need to follow up on bug reports"
```

---

## 💾 Save Agent Output

```
"Save this to Notion"
"Remember this in Notion"
"Log this to my Nivora notes"
"Store this conversation in Notion"
```

**Auto-timestamped entries perfect for:**
- Saving AI-generated content
- Logging research findings
- Recording voice commands
- Keeping conversation history

---

## 🎯 Combined Workflows

### Morning Routine
```
User: "Give me my email summary"
Agent: [Provides summary]

User: "Save that to Notion"
Agent: [Logs to Nivora Notes with timestamp]
```

### Meeting Notes
```
User: "Create a Notion page for today's team meeting"
Agent: [Creates page]

User: "Add these action items:
Alice review PR,
Bob fix navigation bug,
Charlie write tests"
Agent: [Adds to page]
```

### Research Workflow
```
User: "Search the web for latest React trends"
Agent: [Web search results]

User: "Save this to Notion as React Research"
Agent: [Creates page with findings]
```

### Task Management
```
User: "What are my Notion tasks?"
Agent: [Searches for task database]

User: "Add task: Prepare Q1 presentation, due Friday"
Agent: [Adds to database]
```

---

## 📋 Markdown Formatting

### Headers
```
"Create page with heading one Overview"  → # Overview
"Add heading two Goals"                  → ## Goals
"Add heading three Q1"                   → ### Q1
```

### Lists
```
"Add bullet Research phase"              → - Research phase
"Add bullet Design phase"                → - Design phase

"Add numbered item First step"           → 1. First step
"Add numbered item Second step"          → 2. Second step
```

### Checkboxes
```
"Add checkbox Review code"               → [ ] Review code
"Add completed checkbox Send emails"     → [x] Send emails
```

### Dividers
```
"Add a divider"                          → ---
```

---

## 🎨 Example Use Cases

### 1. Daily Journaling
```
User: "Update my Notion journal with today's entry"

Agent: "What would you like to add?"

User: "Today was productive. Completed the API integration,
had a great meeting with the design team, and planned next
week's sprint. Need to follow up on the database optimization
task tomorrow."

Agent: [Appends to journal with today's date as heading]
```

### 2. Project Planning
```
User: "Create a Notion page for Q2 Project Plan"

Agent: [Creates page]

User: "Add these sections:
heading Overview
heading Goals
bullet Launch new features
bullet Increase user base
heading Timeline
April Research
May Development
June Testing"

Agent: [Adds structured content]
```

### 3. Meeting Minutes
```
User: "Create meeting notes for client call"

Agent: [Creates page]

User: "Add:
heading Attendees
Me, Client, Project Manager

heading Discussion Points
bullet Project timeline
bullet Budget review
bullet Next steps

heading Action Items
checkbox Send proposal by Friday
checkbox Schedule follow-up meeting
checkbox Update project tracker"

Agent: [Creates formatted meeting notes]
```

### 4. Knowledge Base
```
User: "Search Notion for API documentation"

Agent: [Shows search results]

User: "Update that page with:
heading Authentication
New OAuth2 flow implemented.
Use bearer tokens for all requests."

Agent: [Appends to existing docs]
```

### 5. Quick Capture
```
User: "I just had an idea for improving the onboarding flow"

Agent: "Tell me more"

User: "We could add a guided tour with tooltips,
save user progress, and send a welcome email series"

Agent: [Listening]

User: "Save that to Notion"

Agent: [Saves to Nivora Notes with timestamp]
```

---

## 💡 Pro Tips

### 1. Use Natural Language
```
✓ "Create a page about project ideas"
✓ "Add this to my notes"
✓ "Search for meeting notes"
```

### 2. Reference by Name
```
✓ "Read my page about API docs"
✓ "Update my journal"
✓ "Add to my task database"
```

### 3. Chain Commands
```
User: "Search Notion for project plan"
Agent: [Results]
User: "Read the first one"
Agent: [Content]
User: "Add a note that we're ahead of schedule"
Agent: [Updates]
```

### 4. Specify Structure
```
"Create a page with:
heading one Main Topic
heading two Subtopic
bullet Point 1
bullet Point 2"
```

### 5. Use Save for Quick Capture
```
User: [Asks agent something]
Agent: [Provides detailed answer]
User: "Save that to Notion"
Agent: [Auto-logs with timestamp]
```

---

## 🔧 Common Patterns

### Template Creation
```
"Create a Notion template for weekly reviews with:
heading What Went Well
heading What Could Improve
heading Goals for Next Week
heading Action Items"
```

### Status Updates
```
"Add to project status page:
heading Update March 30
bullet Completed API integration
bullet Started frontend work
bullet Blocked on design assets"
```

### Research Notes
```
"Create research notes about X with:
heading Overview
[AI explanation]
heading Key Points
bullet [point 1]
bullet [point 2]
heading Resources
[links]"
```

### Daily Logs
```
"Update my daily log:
heading Today's Accomplishments
bullet Finished 3 tasks
bullet Had productive meeting

heading Tomorrow's Plan
checkbox Start new feature
checkbox Review team's PRs"
```

---

## 🚫 What Not to Do

### ❌ Don't Use Without Setup
```
Need to share pages with integration first!
```

### ❌ Don't Assume Database Schema
```
Bad:  "Add task with custom field X"
Good: "Add task with name, status, and priority"
```

### ❌ Don't Use Complex Nested Structures
```
Bad:  "Create page with nested databases and linked pages"
Good: "Create page with simple content, then build up"
```

### ❌ Don't Forget Parent Pages
```
If creating pages fails, provide parent_page_id
```

---

## 🎓 Learning Path

### Beginner
1. Search existing pages
2. Read page content
3. Update existing pages
4. Use "Save to Notion" for quick capture

### Intermediate
5. Create new pages with markdown
6. Add entries to databases
7. Structure content with headings
8. Use templates

### Advanced
9. Chain multiple operations
10. Build workflows (email → Notion → calendar)
11. Auto-log agent outputs
12. Create project documentation

---

## 📚 Quick Reference Table

| Action | Voice Command | Function Called |
|--------|---------------|----------------|
| Create | "Create Notion page about X" | `create_notion_page()` |
| Search | "Search Notion for X" | `search_notion()` |
| Read | "Read my Notion page about X" | `read_notion_page()` |
| Add DB | "Add task X to Notion" | `add_to_notion_database()` |
| Update | "Add this to my Notion notes" | `update_notion_page()` |
| Save | "Save this to Notion" | `save_agent_output()` |

---

## 🔗 Integration Examples

### With Gmail
```
User: "Read my important emails"
Agent: [Email summary]
User: "Save that to Notion"
Agent: [Logs to Nivora Notes]
```

### With Calendar
```
User: "What are my meetings today?"
Agent: [Meeting list]
User: "Create Notion pages for each meeting"
Agent: [Creates meeting notes]
```

### With Web Search
```
User: "Search for React best practices"
Agent: [Web results]
User: "Save top 3 findings to Notion"
Agent: [Creates page with research]
```

### With Screen Share
```
User: [Shares screen]
Agent: "I see your code editor with X"
User: "Save this analysis to Notion"
Agent: [Logs screenshot analysis]
```

---

**Tip**: Start simple with search and save, then explore creating and updating pages as you get comfortable! 🚀

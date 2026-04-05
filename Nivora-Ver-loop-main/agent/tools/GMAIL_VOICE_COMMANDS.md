# Gmail Voice Commands Quick Reference

## 📧 Send Email
```
"Send an email to john@example.com about tomorrow's meeting"
"Email my professor saying I'll be late"
"Send email to team@company.com with subject Project Update"
```

## 📬 Read Emails
```
"Read my unread emails"
"Show me my emails"
"What are my recent emails?"
"Read emails from today"
```

## 🔍 Search
```
"Search emails from my professor"
"Find emails with attachments from last week"
"Search for emails about the project deadline"
"Find emails from boss@company.com"
"Show me important emails from yesterday"
```

## ↩️ Reply
```
"Reply to that thread saying thanks"
"Reply to the last email with 'I'll be there'"
"Send a reply saying I received it"
```
**Note**: Works after reading an email (thread context is stored)

## 📊 Summary
```
"Give me my email summary"
"What's my inbox status?"
"Anything important in my email?"
"Morning email briefing"
```

## Advanced Search Queries

### By Sender/Recipient
```
"Search emails from john@example.com"
"Find emails to me from my boss"
```

### By Date
```
"Show emails from last week"
"Find emails after March 1st"
"Search emails from yesterday"
```

### By Attachment
```
"Find emails with attachments"
"Show me PDFs from professor"
```

### By Label/Status
```
"Read my important emails"
"Show starred emails"
"Find unread emails from today"
```

### Combined Queries
```
"Search unread emails from boss with attachments"
"Find important emails from last week"
"Show emails about 'meeting' from john after March 20th"
```

## Gmail Query Syntax

| Voice Command | Gmail Query |
|---------------|-------------|
| "from professor" | `from:professor@university.edu` |
| "emails with attachments" | `has:attachment` |
| "unread emails" | `is:unread` |
| "important emails" | `is:important` |
| "starred emails" | `is:starred` |
| "from last week" | `newer_than:7d` |
| "from yesterday" | `newer_than:1d` |
| "after March 1st" | `after:2024/03/01` |
| "before today" | `before:2024/03/30` |
| "about meeting" | `subject:meeting` |
| "larger than 5MB" | `larger:5M` |

## Integration with Daily Routine

### Morning Briefing
```
User: "Good morning Infin"

Infin: [Checks calendar, weather, email]
"Good morning! Here's your briefing:

📧 Email Summary:
• 12 unread emails
• 2 important emails today:
  - From Boss: Q1 Review Meeting
  - From HR: Benefits Update

📅 Calendar: You have 3 meetings today...
☀️ Weather: Sunny, 72°F..."
```

### Pre-Meeting Check
```
User: "Any emails about today's 2pm meeting?"

Infin: [Searches emails with 'meeting' from today]
"Found 2 emails:
- From John: Meeting agenda attached
- From Sarah: Running 5 minutes late"
```

## Tips for Voice Commands

1. **Be specific with recipients**: Say full name or email
   - ✅ "Send email to john@example.com"
   - ❌ "Send email to John" (agent needs full address)

2. **Natural date references work**:
   - "from today", "from yesterday", "from last week"
   - Agent converts to Gmail query syntax

3. **Reply context**: Agent remembers last read email
   - Read email first, then say "reply to that"

4. **Query flexibility**: Agent understands natural language
   - "emails with attachments from professor"
   - Agent converts to: `from:professor has:attachment`

5. **Summary for overview**: Use before diving into specifics
   - Start with "email summary"
   - Then: "read those important emails"

## Error Handling

If you hear these responses:

| Response | Meaning | Solution |
|----------|---------|----------|
| "No emails found" | Search returned empty | Try broader query |
| "No recent email to reply to" | No thread context | Read an email first |
| "Gmail API error" | API issue | Check internet connection |
| "Authentication failed" | Token expired | Run setup script again |

## Example Conversation Flow

```
User: "Good morning, give me my email summary"

Infin: "📧 Email Summary:
• 8 unread emails
• 1 important email today:
  - From Boss: Urgent: Review needed
• Recent senders: Boss, HR, John"

User: "Read that important email"

Infin: "From boss@company.com on March 30 at 9:15 AM:
Subject: Urgent: Review needed
Can you review the Q1 report by EOD? Thanks.
[Thread ID: abc123]"

User: "Reply saying I'll have it done by 3pm"

Infin: "Reply sent successfully to thread 'Urgent: Review needed'"

User: "Also send an email to john@company.com saying meeting moved to 4pm"

Infin: "Email sent successfully to john@company.com. Message ID: xyz789"

User: "Thanks, anything else urgent?"

Infin: "Let me check... [searches recent emails]
No other urgent emails. You're all set!"
```

## Voice Command Best Practices

### ✅ DO:
- Use full email addresses when sending
- Let agent read emails before replying
- Use summary first for quick overview
- Be specific with search terms
- Ask follow-up questions naturally

### ❌ DON'T:
- Use incomplete email addresses
- Try to reply without reading first
- Ask to "read all emails" (agent has max limits)
- Expect agent to guess sender addresses
- Worry about exact Gmail syntax (agent handles it)

## Quick Start Workflow

1. **Morning routine**:
   ```
   "Give me my email summary"
   "Read my important emails"
   ```

2. **Throughout day**:
   ```
   "Any new emails?"
   "Search emails about [topic]"
   ```

3. **Responding**:
   ```
   "Reply to that saying..."
   "Send email to X about Y"
   ```

4. **Before meetings**:
   ```
   "Search emails about the 2pm meeting"
   ```

5. **End of day**:
   ```
   "What's my inbox status?"
   "Any unread emails from my boss?"
   ```

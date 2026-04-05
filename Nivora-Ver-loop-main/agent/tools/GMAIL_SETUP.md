# Gmail Tool Integration Guide

## Overview
Complete Gmail integration for Nivora voice agent with OAuth2 authentication.

## Features
- ✅ Send emails via voice command
- ✅ Read unread/filtered emails
- ✅ Search inbox with Gmail query syntax
- ✅ Reply to email threads
- ✅ Get morning email summary
- ✅ Automatic OAuth2 token refresh
- ✅ Thread context preservation for replies

## Setup Instructions

### 1. Enable Gmail API

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable **Gmail API**:
   - Navigate to "APIs & Services" > "Library"
   - Search for "Gmail API"
   - Click "Enable"

### 2. Create OAuth2 Credentials

1. Go to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "OAuth client ID"
3. Application type: **Desktop app**
4. Name: "Nivora Gmail Tool"
5. Click "Create"
6. Download JSON file as `credentials.json`
7. Place `credentials.json` in project root:
   ```
   Nivora-Ver-loop-main/
   ├── credentials.json  ← here
   ├── multi_agent_livekit.py
   ├── agent/
   │   └── tools/
   │       ├── gmail_tool.py
   │       └── setup_gmail.py
   └── ...
   ```

### 3. Configure OAuth Consent Screen

1. Go to "APIs & Services" > "OAuth consent screen"
2. User Type: **External** (for personal use) or **Internal** (for workspace)
3. Add scopes:
   - `https://www.googleapis.com/auth/gmail.send`
   - `https://www.googleapis.com/auth/gmail.readonly`
   - `https://www.googleapis.com/auth/gmail.modify`
4. Add your email as test user (if External)

### 4. Install Dependencies

```bash
pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client
```

Or add to `requirements.txt`:
```txt
google-auth>=2.23.0
google-auth-oauthlib>=1.1.0
google-auth-httplib2>=0.1.1
google-api-python-client>=2.100.0
```

### 5. Authenticate

Run the setup script once:

```bash
python agent/tools/setup_gmail.py
```

This will:
1. Open browser for Google OAuth consent
2. Generate token and save to `~/.nivora/gmail_token.json`
3. Verify authentication by fetching your email address

**Token location**: `C:\Users\<YourName>\.nivora\gmail_token.json` (Windows) or `~/.nivora/gmail_token.json` (Unix)

### 6. Integrate with Agents

Add Gmail tools to both Infin and Nivora agents in `multi_agent_livekit.py`:

```python
from agent.tools.gmail_tool import GMAIL_TOOLS

class AgentConfig:
    # ... existing code ...

    # Add to Infin's tools (life management assistant)
    INFIN_TOOLS = [
        # ... existing tools ...
        *GMAIL_TOOLS,  # ← Add Gmail tools
    ]

    # Optionally add to Nivora as well
    NIVORA_TOOLS = [
        # ... existing tools ...
        *GMAIL_TOOLS,  # ← If you want Nivora to handle emails too
    ]
```

### 7. Update Agent Instructions

Add Gmail capabilities to agent prompts:

**infin_prompts.py** (recommended location for email tools):
```python
def build_agent_instruction():
    return f"""
    ... existing instructions ...

    ## Email Management (Gmail)
    - Send emails: "Send email to john@example.com about meeting tomorrow"
    - Read inbox: "Read my unread emails" or "Show me emails from yesterday"
    - Search emails: "Search emails from my professor" or "Find emails with attachments"
    - Reply to threads: "Reply to that email saying thanks" (works after reading an email)
    - Morning briefing: "Give me my email summary" (perfect for daily routine)

    Gmail Query Syntax:
    - from:sender@example.com
    - to:me subject:meeting
    - has:attachment is:unread
    - after:2024/01/01 before:2024/12/31
    - larger:5M

    ... rest of instructions ...
    """
```

## Voice Command Examples

### Send Email
```
User: "Send an email to my professor at prof@university.edu saying I'll be late to office hours"

Agent: "I'll send that email now."
[Calls send_email with parsed parameters]
Agent: "Email sent successfully to prof@university.edu. Message ID: abc123"
```

### Read Unread Emails
```
User: "What are my unread emails?"

Agent: [Calls read_emails(max_results=5, query="is:unread")]
Agent: "Found 3 emails:

From john@example.com on March 29 at 2:30 PM:
Subject: Project Update
Quick update on the project status...
[Thread ID: abc123]

..."
```

### Search Emails
```
User: "Find emails from my boss last week"

Agent: [Calls search_emails(query="from:boss@company.com after:2024/03/22")]
Agent: "Search results for 'from:boss@company.com after:2024/03/22' (2 found): ..."
```

### Reply to Email
```
User: "Reply to that thread saying thanks, I received it"

Agent: [Calls reply_to_email(thread_id="last", body="Thanks, I received it")]
Agent: "Reply sent successfully to thread 'Project Update'"
```

### Morning Summary
```
User: "Give me my email summary"

Agent: [Calls get_email_summary()]
Agent: "📧 Email Summary:
• 12 unread emails
• 2 important emails today:
  - From Boss: Q1 Review Meeting
  - From HR: Benefits Update
• Recent senders: John, Sarah, Mike, Lisa"
```

## Function Reference

### send_email(to: str, subject: str, body: str) -> str
Sends an email via Gmail API.
- **to**: Recipient email address
- **subject**: Email subject line
- **body**: Email body text
- **Returns**: Confirmation with message ID

### read_emails(max_results: int = 5, query: str = "is:unread") -> str
Reads emails matching query.
- **max_results**: Max emails to fetch (default: 5)
- **query**: Gmail search query (default: unread emails)
- **Returns**: Formatted email list with sender, subject, snippet, date

### search_emails(query: str, max_results: int = 10) -> str
Searches inbox with Gmail query syntax.
- **query**: Gmail search query (supports full Gmail syntax)
- **max_results**: Max results to return (default: 10)
- **Returns**: Formatted search results

### reply_to_email(thread_id: str, body: str) -> str
Replies to an email thread.
- **thread_id**: Thread ID (shown when reading emails) or "last" for most recent
- **body**: Reply message body
- **Returns**: Confirmation message

### get_email_summary() -> str
Gets inbox summary for morning briefing.
- **Returns**: Unread count, important emails today, recent senders

## Token Management

### Automatic Refresh
The tool automatically refreshes expired OAuth tokens. No manual intervention needed.

### Re-authenticate
If token becomes invalid:
```bash
rm ~/.nivora/gmail_token.json
python agent/tools/setup_gmail.py
```

### Token Location
- **Windows**: `C:\Users\<YourName>\.nivora\gmail_token.json`
- **Linux/Mac**: `~/.nivora/gmail_token.json`

## Troubleshooting

### "Missing credentials.json" Error
- Ensure `credentials.json` is in project root (same directory as `multi_agent_livekit.py`)
- Verify it's valid OAuth2 credentials (Desktop app type)

### OAuth Consent Screen Warning
If using External user type with unverified app:
1. Click "Advanced" in browser warning
2. Click "Go to Nivora Gmail Tool (unsafe)"
3. This is normal for personal projects

### "Access blocked" Error
- Verify Gmail API is enabled in Google Cloud Console
- Check OAuth scopes match those in code
- Ensure your email is added as test user (External apps)

### Token Refresh Failed
Delete token and re-authenticate:
```bash
rm ~/.nivora/gmail_token.json
python agent/tools/setup_gmail.py
```

### "Thread not found" for Replies
- Ensure you've read an email first (stores thread ID)
- Or provide explicit thread ID from email list
- Thread IDs shown in brackets when reading: `[Thread ID: abc123]`

## Security Notes

- ✅ OAuth2 tokens stored locally in `~/.nivora/`
- ✅ Never commit `credentials.json` or `token.json` to git
- ✅ Add to `.gitignore`:
  ```
  credentials.json
  ~/.nivora/
  token.json
  gmail_token.json
  ```
- ✅ Tokens auto-refresh - no password storage needed
- ✅ Revoke access anytime: [Google Account Permissions](https://myaccount.google.com/permissions)

## Gmail Query Syntax Reference

| Query | Description |
|-------|-------------|
| `is:unread` | Unread emails |
| `is:starred` | Starred emails |
| `is:important` | Important emails |
| `from:email@example.com` | From specific sender |
| `to:email@example.com` | To specific recipient |
| `subject:meeting` | Subject contains "meeting" |
| `has:attachment` | Has attachments |
| `after:2024/03/01` | After date |
| `before:2024/03/31` | Before date |
| `larger:5M` | Larger than 5MB |
| `smaller:1M` | Smaller than 1MB |
| `label:work` | Has label "work" |

Combine queries: `from:boss is:unread has:attachment`

## Integration with Daily Routines

Add to morning routine automation:
```python
# In tools.py or morning_routine.py
def morning_briefing():
    summary = get_email_summary()
    # Combine with calendar, weather, etc.
    return f"{summary}\n\n{calendar_summary()}\n\n{weather_summary()}"
```

Perfect for: "Good morning Infin, give me my daily briefing"

## Next Steps

1. ✅ Complete setup above
2. Test each function individually
3. Add to agent instructions
4. Create custom email workflows (e.g., filter important senders)
5. Integrate with calendar for meeting invites
6. Add email templates for common responses

## Support

For issues:
1. Check troubleshooting section above
2. Verify Gmail API is enabled
3. Review OAuth consent screen settings
4. Check logs for specific error messages

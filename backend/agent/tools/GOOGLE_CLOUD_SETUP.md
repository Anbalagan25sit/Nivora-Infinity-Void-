# Google Cloud Console Setup - Step by Step Guide

## Part 1: Enable Gmail API

### Step 1: Go to Google Cloud Console
1. Visit: https://console.cloud.google.com/
2. Sign in with your Google account
3. Create a new project or select existing one:
   - Click the project dropdown at the top
   - Click "New Project"
   - Name it "Nivora Gmail Tool" (or any name)
   - Click "Create"

### Step 2: Enable Gmail API
1. In the left sidebar, click **"APIs & Services"** > **"Library"**
2. Search for **"Gmail API"**
3. Click on it
4. Click the blue **"Enable"** button
5. Wait for it to enable (takes a few seconds)

---

## Part 2: Create OAuth2 Credentials

### Step 3: Configure OAuth Consent Screen

**IMPORTANT: Do this BEFORE creating credentials**

1. Go to **"APIs & Services"** > **"OAuth consent screen"** (left sidebar)

2. **Choose User Type**:
   - **External** - If using personal Gmail account (most users)
   - **Internal** - If using Google Workspace account
   - Click **"Create"**

3. **Fill in App Information** (Page 1):
   ```
   App name: Nivora Gmail Tool
   User support email: your-email@gmail.com
   Developer contact: your-email@gmail.com
   ```
   - Leave other fields optional
   - Click **"Save and Continue"**

4. **Add Scopes** (Page 2):
   - Click **"Add or Remove Scopes"**
   - In the filter box, search for **"gmail"**
   - Check these 3 scopes:
     ```
     ☑ .../auth/gmail.send
     ☑ .../auth/gmail.readonly
     ☑ .../auth/gmail.modify
     ```
   - Scroll down and click **"Update"**
   - Click **"Save and Continue"**

5. **Add Test Users** (Page 3) - **ONLY if you selected External**:
   - Click **"+ Add Users"**
   - Enter your Gmail address: `your-email@gmail.com`
   - Click **"Add"**
   - Click **"Save and Continue"**

6. **Summary** (Page 4):
   - Review everything
   - Click **"Back to Dashboard"**

### Step 4: Create OAuth Client ID

1. Go to **"APIs & Services"** > **"Credentials"** (left sidebar)

2. Click **"+ Create Credentials"** at the top

3. Select **"OAuth client ID"**

4. **Application type**: Select **"Desktop app"**

5. **Name**: Enter `Nivora Gmail Desktop Client` (or any name)

6. Click **"Create"**

7. **Download Credentials**:
   - A popup appears: "OAuth client created"
   - Click **"Download JSON"** button
   - Save the file
   - **Rename it to `credentials.json`** (IMPORTANT!)

### Step 5: Place credentials.json

1. Move/copy `credentials.json` to your project root:
   ```
   C:\Users\Nivorichi\Downloads\Nivora-Ver-loop-main\Nivora-Ver-loop-main\
   ```

2. The file should be in the same folder as:
   - `multi_agent_livekit.py`
   - `requirements.txt`
   - `agent/` folder

---

## Part 3: Run Setup Script

Now that you have `credentials.json`, run:

```bash
python agent/tools/setup_gmail.py
```

This will:
1. Open your browser for Google OAuth
2. Show you a warning screen (normal for unverified apps)
3. Generate and save your token to `~/.nivora/gmail_token.json`

### Handling the OAuth Warning

When you authorize, you might see:
```
"Google hasn't verified this app"
```

This is **NORMAL** for personal projects. To proceed:
1. Click **"Advanced"** (bottom left)
2. Click **"Go to Nivora Gmail Tool (unsafe)"**
3. Click **"Allow"** to grant permissions

**Why this happens**: Your app isn't verified by Google (which costs money and requires review). For personal use, this is completely fine.

---

## Troubleshooting

### "App not verified" in OAuth screen
- **Solution**: This is normal. Click "Advanced" > "Go to [App Name] (unsafe)"
- **Why**: Personal projects aren't verified by Google
- **Safe?**: Yes, you created this app yourself

### "Access blocked: This app's request is invalid"
- **Cause**: OAuth consent screen not configured
- **Solution**: Go back to Step 3 and complete consent screen setup
- **Check**: Make sure you added the 3 Gmail scopes

### "The OAuth client was deleted"
- **Cause**: Downloaded wrong credentials or client was deleted
- **Solution**: Create a new OAuth client ID in Step 4

### "redirect_uri_mismatch" error
- **Cause**: Wrong application type selected
- **Solution**: Must be **"Desktop app"**, not "Web application"
- **Fix**: Delete the credential and create new one as Desktop app

### "Gmail API has not been used in project"
- **Cause**: Forgot to enable Gmail API
- **Solution**: Go to Step 2 and enable Gmail API
- **Wait**: Give it 1-2 minutes after enabling

### Can't find credentials.json
- **Check location**: Must be in project root:
  ```
  C:\Users\Nivorichi\Downloads\Nivora-Ver-loop-main\Nivora-Ver-loop-main\credentials.json
  ```
- **Check name**: Must be exactly `credentials.json` (not `credentials (1).json`)
- **Check format**: Must be the OAuth client JSON (starts with `{"installed":{...}`)

---

## Quick Checklist

Before running `setup_gmail.py`, verify:

- [ ] Gmail API is enabled
- [ ] OAuth consent screen is configured
- [ ] 3 Gmail scopes are added to consent screen
- [ ] Test user added (if External app)
- [ ] OAuth client ID created (Desktop app type)
- [ ] credentials.json downloaded
- [ ] credentials.json renamed correctly
- [ ] credentials.json in project root folder

---

## What Each Scope Does

| Scope | Permission | Used For |
|-------|-----------|----------|
| `gmail.send` | Send emails on your behalf | `send_email()`, `reply_to_email()` |
| `gmail.readonly` | Read emails | `read_emails()`, `search_emails()`, `get_email_summary()` |
| `gmail.modify` | Mark as read/unread, apply labels | Future features |

---

## Security Notes

✅ **Safe**:
- Your credentials stay on your computer
- Token is stored locally in `~/.nivora/`
- Google OAuth is industry standard
- You can revoke access anytime

✅ **Revoke Access**:
1. Go to https://myaccount.google.com/permissions
2. Find "Nivora Gmail Tool"
3. Click "Remove Access"

✅ **Token Location**:
- Windows: `C:\Users\<YourName>\.nivora\gmail_token.json`
- Linux/Mac: `~/.nivora/gmail_token.json`

---

## Next Steps After Setup

Once `setup_gmail.py` completes successfully:

1. **Test the tool**:
   ```bash
   python agent/tools/test_gmail.py
   ```

2. **Integrate with agent**:
   - Edit `multi_agent_livekit.py`
   - Add `GMAIL_TOOLS` to agent configuration

3. **Try voice commands**:
   - "Give me my email summary"
   - "Read my unread emails"
   - "Send email to..."

---

## Visual Flow

```
Google Cloud Console
        ↓
1. Create Project
        ↓
2. Enable Gmail API
        ↓
3. Configure OAuth Consent Screen
   - App name
   - Add Gmail scopes ← IMPORTANT
   - Add test users
        ↓
4. Create OAuth Client ID (Desktop app)
        ↓
5. Download JSON → Rename to credentials.json
        ↓
6. Move to project root
        ↓
7. Run: python agent/tools/setup_gmail.py
        ↓
8. Browser opens for OAuth
        ↓
9. Click "Advanced" → "Go to [App] (unsafe)"
        ↓
10. Grant permissions
        ↓
11. Token saved to ~/.nivora/gmail_token.json
        ↓
DONE! ✓
```

---

## Still Stuck?

Check these common mistakes:

1. **Forgot to add scopes** in OAuth consent screen
2. **Selected wrong application type** (must be Desktop app)
3. **Didn't add test user** (for External apps)
4. **credentials.json in wrong location** (must be project root)
5. **Gmail API not enabled** (check in APIs & Services)

Run the setup script - it will tell you exactly what's wrong!
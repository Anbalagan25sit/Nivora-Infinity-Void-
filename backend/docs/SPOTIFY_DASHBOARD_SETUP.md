# 🎯 How to Add Redirect URI to Spotify Dashboard - Step by Step

## 🚨 The Solution

Use **`http://127.0.0.1:8888/callback`** instead of `http://localhost:8888/callback`

**Why?** Spotify often accepts IP addresses (127.0.0.1) even though it shows warnings for "localhost".

---

## 📋 Step-by-Step Guide

### **Step 1: Go to Spotify Developer Dashboard**

Open: https://developer.spotify.com/dashboard/applications

Log in with your Spotify account.

---

### **Step 2: Find Your App**

You'll see a list of your apps. Click on the app you created for Nivora.

```
┌─────────────────────────────────────────┐
│  My Apps                                │
├─────────────────────────────────────────┤
│  📱 Nivora                              │
│     Client ID: 552c0a4...               │
│     [Click here] ←────────────────────  │
└─────────────────────────────────────────┘
```

---

### **Step 3: Click "Edit Settings"**

On your app page, look for the **"Edit Settings"** button (usually green) in the top right.

```
┌─────────────────────────────────────────────────┐
│  Nivora                          [Edit Settings]│ ← Click here
│  Client ID: 552c0a4acea3460ca43ee6d649b72aff   │
│  Client Secret: ••••••••••••••••               │
└─────────────────────────────────────────────────┘
```

---

### **Step 4: Find Redirect URIs Section**

Scroll down in the settings modal until you see **"Redirect URIs"**

```
┌────────────────────────────────────────┐
│  Edit Settings                    [X]  │
├────────────────────────────────────────┤
│  App Name: Nivora                      │
│  Description: Voice Assistant          │
│                                        │
│  ↓ Scroll down ↓                      │
│                                        │
│  Redirect URIs *                       │ ← Here!
│  ┌──────────────────────────────────┐ │
│  │                                  │ │
│  └──────────────────────────────────┘ │
└────────────────────────────────────────┘
```

---

### **Step 5: Add the Redirect URI**

**IMPORTANT:** Type **EXACTLY** this (copy-paste recommended):

```
http://127.0.0.1:8888/callback
```

**NOT:**
- ❌ `http://localhost:8888/callback` (won't work - shows as "not secure")
- ❌ `https://127.0.0.1:8888/callback` (wrong protocol)
- ❌ `http://127.0.0.1:8888` (missing /callback)

**Type it in the text box:**

```
┌────────────────────────────────────────────┐
│  Redirect URIs *                           │
│  ┌──────────────────────────────────────┐ │
│  │ http://127.0.0.1:8888/callback      │ │ ← Type here
│  └──────────────────────────────────────┘ │
│             [Add] ←─────── Click this     │
└────────────────────────────────────────────┘
```

---

### **Step 6: Click "Add" Button**

After typing the URI, click the **"Add"** button next to the text box.

You should see it appear in the list:

```
┌────────────────────────────────────────────┐
│  Redirect URIs *                           │
│                                            │
│  ✓ http://127.0.0.1:8888/callback    [X]  │ ← Added!
│                                            │
│  ┌──────────────────────────────────────┐ │
│  │                                      │ │
│  └──────────────────────────────────────┘ │
│             [Add]                          │
└────────────────────────────────────────────┘
```

---

### **Step 7: SAVE at the Bottom**

**CRITICAL:** Scroll to the bottom and click the **"SAVE"** button!

```
┌────────────────────────────────────────┐
│  Edit Settings                         │
│                                        │
│  ... other settings ...                │
│                                        │
│         [Cancel]        [SAVE] ←── CLICK THIS!
└────────────────────────────────────────┘
```

---

## ✅ Verification

After saving, you should see:

```
✓ Settings saved successfully
```

Your redirect URI list should show:

```
Redirect URIs:
  • http://127.0.0.1:8888/callback
```

---

## 🚀 Now Run the Script

```bash
python get_spotify_token_fixed.py
```

The script will:
1. ✓ Detect your credentials
2. ✓ Remind you about the redirect URI (done!)
3. ✓ Start local server on 127.0.0.1:8888
4. ✓ Open browser
5. ✓ You click "Agree"
6. ✓ Redirect works (no error!)
7. ✓ Token saved to .env

---

## 🐛 Troubleshooting

### Issue: Still shows "redirect_uri: Not matching configuration"

**Solutions:**

1. **Check the URI is EXACTLY:**
   ```
   http://127.0.0.1:8888/callback
   ```
   (No extra spaces, correct spelling, correct port)

2. **Make sure you clicked SAVE**
   - It's easy to forget!
   - The setting won't apply until you save

3. **Wait a few seconds**
   - Spotify may take 10-30 seconds to update
   - Close and reopen the dashboard to verify

4. **Check you're editing the right app**
   - Make sure Client ID matches your .env file

---

### Issue: Dashboard won't let me add the URI

**Alternative URIs to try:**

**Option 1:** Different localhost IP
```
http://0.0.0.0:8888/callback
```

**Option 2:** Different port
```
http://127.0.0.1:3000/callback
```
(Then edit the script to use port 3000)

**Option 3:** Use actual external IP
```bash
# Find your local IP
ipconfig  # Windows
ifconfig  # Mac/Linux

# Add to dashboard: http://192.168.X.X:8888/callback
```

---

### Issue: "This redirect URI is not secure"

**That's OK!** Spotify shows this warning but often still accepts 127.0.0.1 URIs.

**Try:**
1. Add it anyway and click Save
2. If it truly won't save, use Option 2 from troubleshooting above

---

## 🎯 Quick Checklist

Before running the script, verify:

```
□ Logged into Spotify Developer Dashboard
□ Opened your app settings
□ Clicked "Edit Settings"
□ Found "Redirect URIs" section
□ Added: http://127.0.0.1:8888/callback
□ Clicked "Add" button
□ Clicked "SAVE" at bottom
□ Saw "Settings saved" confirmation
□ Waited 10 seconds for update
```

---

## 💡 Pro Tips

### Tip 1: Copy-Paste the URI
Don't type it manually - copy from here:
```
http://127.0.0.1:8888/callback
```

### Tip 2: Verify After Adding
After saving, reopen settings to confirm it's there.

### Tip 3: Multiple URIs OK
You can have multiple redirect URIs. Add both if you want:
```
http://127.0.0.1:8888/callback
http://localhost:8888/callback
```

### Tip 4: Keep Dashboard Open
Keep the dashboard tab open while running the script in case you need to check settings.

---

## 🎉 Success!

Once the redirect URI is added:

1. **Run:** `python get_spotify_token_fixed.py`
2. **Click:** "Agree" in browser
3. **See:** Success page ✓
4. **Get:** Token saved to .env
5. **Start:** `python agent.py start`
6. **Test:** "Play Blinding Lights" 🎵

**Done!** 🚀

---

## 📞 Still Stuck?

If you still can't add the redirect URI:

1. **Screenshot the error** you're seeing
2. **Verify your Spotify account type** (Free vs Premium)
3. **Try creating a new app** from scratch
4. **Check Spotify Status:** https://status.spotify.com
5. **Contact Spotify Support** (rare, but sometimes dashboard has issues)

---

**Most common mistake:** Forgetting to click SAVE at the bottom! ⚠️

**Remember:** Use `127.0.0.1` not `localhost` - it works better! ✓

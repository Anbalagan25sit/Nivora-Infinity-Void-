# Extension Permission Fix Guide

## What Was Fixed

✅ **Content Security Policy**: Added `https://*.livekit.cloud` to allow HTTPS requests to LiveKit
✅ **Host Permissions**: Added `https://*.livekit.cloud` to manifest permissions

## New Manifest Features

The updated `manifest.json` now allows:
- HTTPS connections to LiveKit cloud services
- WebSocket connections (WSS) to LiveKit
- HTTP connections to localhost (token server)

## Next Steps

### 1. Reload the Extension
1. Go to `chrome://extensions/`
2. Find the "Nivora Voice Assistant" extension
3. Click the **"Reload"** button 🔄

### 2. Test Connection
1. Click the extension icon (or Alt+N)
2. Click "Wanna Talk?" button
3. **Allow microphone access** when Chrome asks
4. Should now connect successfully!

## If You Still Get Permission Errors

### Microphone Permission Issue
If you see "Permission dismissed":
1. Check Chrome's site settings for the extension
2. Go to Settings → Privacy and security → Site settings → Microphone
3. Make sure the extension has microphone access

### CSP Errors Persist
If you still see CSP errors:
1. Make sure you **reloaded the extension** after rebuilding
2. Try removing and re-adding the extension:
   - Go to `chrome://extensions/`
   - Remove Nivora extension
   - Click "Load unpacked" again
   - Select the `dist` folder

## Debug Console Commands

If you want to test the connection manually in the extension console:

```javascript
// Test token endpoint
fetch('http://localhost:8080/api/token?room=test&participant=user123')
  .then(r => r.json())
  .then(console.log)

// Test LiveKit connectivity
fetch('https://nivora-5opea2lo.livekit.cloud/settings/regions')
  .then(r => r.json())
  .then(console.log)
```

These should both work without CSP errors now!
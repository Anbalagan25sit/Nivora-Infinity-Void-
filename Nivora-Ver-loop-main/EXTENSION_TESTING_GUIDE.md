# Nivora Extension Testing Guide

## Quick Setup & Test

Follow these steps to test the extension connection:

### 1. Start the Backend Services

```bash
# Terminal 1: Start token server (runs on port 8080)
python start_extension_setup.py

# Terminal 2: Start the agent
python agent.py
```

### 2. Build & Install Extension

```bash
# Windows
build_extension.bat

# Linux/Mac
./build_extension.sh
```

### 3. Load in Chrome

1. Go to `chrome://extensions/`
2. Enable "Developer mode"
3. Click "Load unpacked"
4. Select the `nivora-extension/dist` folder

### 4. Test Connection

1. Click the Nivora extension icon (or press Alt+N)
2. The popup should open without CSP errors
3. You should see the LiveKit connection interface
4. Try connecting - it should get a token from localhost:8080

## What Was Fixed

✅ **CSP Error**: Updated Content Security Policy to allow local scripts and WebSocket connections
✅ **Asset Paths**: Changed from absolute (`/assets/`) to relative (`./assets/`) paths
✅ **Manifest**: Updated popup reference from `popup.html` to `index.html`
✅ **Build Config**: Optimized Vite config for Chrome extension compatibility
✅ **Host Permissions**: Limited to localhost instead of all URLs for security

## Troubleshooting

### Extension Won't Load
- Check if `dist/manifest.json` exists after building
- Verify all icon files are present in `dist/icons/`

### CSP Errors Still Appear
- Make sure you rebuilt the extension after the manifest changes
- Try reloading the extension in chrome://extensions/

### Connection Fails
- Ensure token server is running on port 8080
- Check that agent.py is running and connected to LiveKit
- Verify your .env has correct LIVEKIT_* credentials

### LiveKit Connection Issues
- Check browser console for WebSocket errors
- Ensure LIVEKIT_URL in token server matches your LiveKit cloud project
- Verify API keys are correct in .env file

## Architecture

```
Browser Extension (Chrome)
    ↓ HTTP Request (token)
Token Server (localhost:8080)
    ↓ LiveKit Token
Extension ←→ LiveKit Cloud ←→ Agent (agent.py)
```

The extension now properly:
1. Requests tokens from the local server
2. Connects to LiveKit using those tokens
3. Communicates with your Python agent for AI responses
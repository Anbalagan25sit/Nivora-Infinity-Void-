# Nivora Chrome Extension

A Chrome extension that provides a Perplexity Comet-like AI voice assistant powered by LiveKit.

## Features

- Voice-activated AI assistant
- Real-time audio visualization
- Page context awareness (can analyze current webpage)
- Text input support
- LiveKit integration for real-time communication
- Dark mode UI with smooth animations

## Installation

### 1. Load Extension in Chrome

1. Open Chrome and go to `chrome://extensions/`
2. Enable "Developer mode" (toggle in top right)
3. Click "Load unpacked"
4. Select the `chrome-extension` folder

### 2. Generate Icons (if needed)

```bash
cd chrome-extension
python generate_icons.py
```

### 3. Start the Token Server

The token server is required for LiveKit authentication:

```bash
# Install dependencies
pip install fastapi uvicorn livekit python-dotenv

# Or with Flask
pip install flask flask-cors livekit python-dotenv

# Start the server
python token_server.py
```

The server runs at `http://localhost:8080`

### 4. Configure the Extension

1. Click the Nivora extension icon
2. Click the settings gear icon
3. Enter your LiveKit server URL (e.g., `wss://your-project.livekit.cloud`)
4. Enter the token API endpoint (default: `http://localhost:8080/api/token`)
5. Save settings

## Usage

### Voice Mode
- Click the floating microphone button to open the assistant
- Click the mic button to start speaking
- Click again or the X button to stop

### Text Mode
- Type your message in the input field
- Press Enter or click the send button

### Page Context
- Click the + button to attach current page context
- The assistant can then answer questions about the page

### Keyboard Shortcut
- Press `Alt+N` to toggle the assistant

## Architecture

```
chrome-extension/
├── manifest.json          # Extension manifest
├── background.js          # Service worker (handles LiveKit tokens)
├── content.js             # Main UI injection script
├── src/
│   └── livekit-integration.js  # LiveKit SDK wrapper
├── styles/
│   └── content.css        # UI styles
├── icons/
│   ├── icon.svg           # SVG source
│   ├── icon16.png         # 16x16 icon
│   ├── icon32.png         # 32x32 icon
│   ├── icon48.png         # 48x48 icon
│   └── icon128.png        # 128x128 icon
└── generate_icons.py      # Icon generator script
```

## Environment Variables

Create a `.env` file in the project root:

```env
LIVEKIT_URL=wss://your-project.livekit.cloud
LIVEKIT_API_KEY=your-api-key
LIVEKIT_API_SECRET=your-api-secret
```

## API Endpoints

### GET /api/token

Generate a LiveKit access token.

Query parameters:
- `room` - Room name (default: "nivora-assistant")
- `participant` - Participant identity (auto-generated if not provided)

Response:
```json
{
  "token": "eyJ...",
  "room": "nivora-assistant",
  "participant": "user-abc123",
  "serverUrl": "wss://your-project.livekit.cloud"
}
```

### GET /api/health

Health check endpoint.

## Connecting to Nivora Agent

The extension connects to your Nivora LiveKit agent. Make sure:

1. The agent is running (`python multi_agent_livekit.py`)
2. LiveKit credentials are configured in `.env`
3. The token server is running
4. Extension settings point to correct endpoints

## Troubleshooting

### Extension not loading
- Check `chrome://extensions/` for errors
- Ensure all files are present in the extension folder

### Voice not working
- Allow microphone permissions when prompted
- Check browser console for errors
- Verify LiveKit connection in settings

### Token errors
- Ensure token server is running
- Check CORS settings if accessing from different origin
- Verify LiveKit credentials in `.env`

## Development

### Rebuilding Icons

```bash
pip install pillow cairosvg
python generate_icons.py
```

### Testing LiveKit Connection

```bash
curl "http://localhost:8080/api/token?room=test&participant=test-user"
```

## License

MIT License - Same as Nivora main project.

# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Nivora is a static marketing website for an AI chat application with **real-time voice chat capabilities** powered by LiveKit. The site showcases product features, pricing, blog content, and includes functional voice-enabled chat interfaces.

## Technology Stack

- **Framework**: Pure HTML with no build system
- **Styling**: Tailwind CSS via CDN (`cdn.tailwindcss.com`)
- **Fonts**: Google Fonts (Noto Serif for headlines, Inter for body)
- **Icons**: Google Material Symbols Outlined
- **Voice/WebRTC**: LiveKit Client SDK via CDN
- **Backend (required for voice)**: Token endpoint for LiveKit authentication

## Development

No build commands required. Open any HTML file directly in a browser to preview.

## Architecture

### Design System

All pages share a consistent Tailwind configuration defined inline in each file's `<script>` block:

**Color Palette** (dark theme):
- `primary`: #b1c5ff (soft blue)
- `tertiary`: #ffb59e (coral accent)
- `background`: #131313 (near black)
- `surface-container-*`: graduated dark grays (#0e0e0e to #353535)
- `on-surface`: #e5e2e1 (light text)

**Typography**:
- `font-headline`: Noto Serif (serif, used for titles)
- `font-body`: Inter (sans-serif, used for body text)

**Common CSS Classes**:
- `.gradient-cta`: Primary gradient for call-to-action buttons
- `.nav-link`: Navigation links with animated underline on hover
- `.custom-scrollbar`: Styled webkit scrollbars
- `.glass-effect`: Backdrop blur with transparency

### Page Structure

| File | Purpose |
|------|---------|
| `index.html` | Landing page with hero, features preview, CTA |
| `features.html` | Detailed feature breakdown |
| `pricing.html` | Subscription tiers |
| `about.html` | Company story, values, team |
| `blog.html` | Article listings |
| `login.html` | Authentication form |
| `chat.html` | New chat interface (app mockup) |
| `conversation.html` | Active conversation view with AI response |
| `library.html` | Search and browse saved content |
| `archive.html` | Historical chat archive |
| `settings.html` | User preferences and account management |
| `active-session.html` | Voice/vision AI session with orb visualization |
| `tool-dashboard.html` | Bento grid dashboard with integrations (Spotify, calendar) |
| `capabilities-directory.html` | AI capabilities/modules directory |
| `technical-core.html` | Technical settings and voice stack configuration |

### Layout Patterns

**Marketing Pages** (index, features, pricing, about, blog):
- Fixed top navigation with backdrop blur
- Full-width sections with `max-w-6xl` content containers
- Consistent footer with site links

**App Interface Pages** (chat, conversation, settings, library, archive):
- Fixed 288px (`w-72`) left sidebar with navigation
- Main content area fills remaining space
- No traditional header/footer

### Navigation

All internal links use relative paths (e.g., `href="chat.html"`). The sidebar navigation in app pages links to:
- New Chat (`chat.html`)
- Library (`library.html`)
- Archive (`archive.html`)
- Settings (`settings.html`)

## Voice Integration Architecture

### JavaScript Modules

Located in `js/`:

| File | Purpose |
|------|---------|
| `nivora-voice.js` | Core LiveKit client, room connection, track handling |
| `voice-ui.js` | UI bindings and state management |
| `audio-visualizer.js` | Orb/waveform audio visualization |

### CSS

Located in `css/`:

| File | Purpose |
|------|---------|
| `voice-states.css` | Animations for connection, mic, agent states |

### Voice-Enabled Pages

| Page | Voice Elements |
|------|----------------|
| `chat.html` | `#mic-btn`, `#chat-input`, `#send-btn`, `#voice-indicator` |
| `conversation.html` | `#mic-btn`, `#chat-input`, `#send-btn`, `#messages-container`, `#voice-indicator` |
| `active-session.html` | `#mic-btn`, `#videocam-btn`, `#end-session-btn`, `#orb-container`, `#audio-canvas`, `#voice-status` |

### State Management

**Voice States** (`VoiceState`): `DISCONNECTED`, `CONNECTING`, `CONNECTED`, `RECONNECTING`, `ERROR`

**Mic States** (`MicState`): `MUTED`, `UNMUTED`, `UNAVAILABLE`

**Agent States** (`AgentState`): `IDLE`, `LISTENING`, `THINKING`, `SPEAKING`

### Configuration

The voice module requires a token endpoint. Configure in `js/nivora-voice.js`:

```javascript
const NIVORA_CONFIG = {
    livekitUrl: 'wss://your-project.livekit.cloud',
    tokenEndpoint: '/api/livekit-token',
    agentName: 'nivora-agent'
};
```

### Backend Requirements

A token endpoint must return:
```json
{ "token": "jwt-token-string", "room": "room-name" }
```

The Python agent runs on LiveKit Cloud using: Sarvam STT, Edge TTS, Silero VAD, AWS Nova Pro LLM.

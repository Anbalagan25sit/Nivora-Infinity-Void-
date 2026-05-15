# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Nivora Personal Assistant - A real-time voice agent frontend built with Next.js 15 and LiveKit. This is a React starter template for LiveKit Agents with voice interaction, video streaming, screen sharing, and multiple audio visualizer styles.

## Commands

```bash
# Install dependencies
pnpm install

# Development server (with Turbopack)
pnpm dev

# Production build
pnpm build

# Start production server
pnpm start

# Linting
pnpm lint

# Format code
pnpm format
pnpm format:check

# Update Agents UI components to latest
pnpm shadcn:install
```

## Environment Setup

Copy `.env.example` to `.env.local` and configure:

- `LIVEKIT_API_KEY` - LiveKit API key
- `LIVEKIT_API_SECRET` - LiveKit API secret
- `LIVEKIT_URL` - LiveKit server URL (wss://...)
- `AGENT_NAME` - Optional: explicit agent dispatch name (leave blank for automatic)

## Architecture

### Key Directories

- `app/` - Next.js App Router pages and API routes
- `components/agents-ui/` - LiveKit Agents UI components (shadcn-style, customizable)
- `components/app/` - Application-specific components with business logic
- `components/ui/` - Primitive shadcn/ui components
- `components/ai-elements/` - AI-related UI elements (shimmer, conversation, message)
- `hooks/` - Custom React hooks including Agents UI hooks
- `lib/` - Utilities and configuration helpers

### Component Architecture

**Session Flow:**

1. `App` (`components/app/app.tsx`) - Root component, creates LiveKit session via `TokenSource`, wraps everything in `AgentSessionProvider`
2. `ViewController` - Manages transitions between `WelcomeView` (disconnected) and `SessionView` (connected)
3. `SessionView` - Main session UI with chat transcript, media tiles, and control bar
4. `TileLayout` - Manages media tile layout and transitions

**Token Flow:**

- Local dev: `TokenSource.endpoint('/api/connection-details')` hits `app/api/connection-details/route.ts`
- Sandbox: Uses `getSandboxTokenSource()` from `lib/utils.ts` with `NEXT_PUBLIC_CONN_DETAILS_ENDPOINT`

### Configuration

App branding and features are configured in `app-config.ts`:

- `AppConfig` interface defines all configurable options
- `APP_CONFIG_DEFAULTS` provides default values
- Supports audio visualizer types: `bar`, `grid`, `radial`, `wave`, `aura`
- Dynamic theming via CSS custom properties (`--primary`, `--primary-hover`)

### Path Aliases

Uses `@/*` path alias mapped to project root (configured in `tsconfig.json`).

## Key Patterns

- All client components use `'use client'` directive
- Animations use `motion/react` (Framer Motion)
- Session state accessed via `useSessionContext()` from `@livekit/components-react`
- Shadcn components extend HTML attributes for easy styling with Tailwind classes
- Agents UI components can be modified directly in `components/agents-ui/`

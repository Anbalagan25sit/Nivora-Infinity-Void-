"""
Central configuration loader.
Reads all secrets/settings from .env and exposes them as module-level constants.

Required .env keys:
  N8N_MCP_URL (or N8N_MCP_SERVER_URL) — Full SSE URL of the n8n MCP server
  N8N_BEARER_TOKEN (optional)         — Bearer token for n8n MCP authentication
"""

import os
from dotenv import load_dotenv

load_dotenv(".env")

# ---------------------------------------------------------------------------
# n8n MCP
# ---------------------------------------------------------------------------
N8N_MCP_URL: str = os.getenv("N8N_MCP_URL", "") or os.getenv("N8N_MCP_SERVER_URL", "")
N8N_BEARER_TOKEN: str = os.getenv("N8N_BEARER_TOKEN", "")

# ---------------------------------------------------------------------------
# GitHub
# ---------------------------------------------------------------------------
GITHUB_USERNAME: str = os.getenv("GITHUB_USERNAME", "")
GITHUB_TOKEN: str = os.getenv("GITHUB_TOKEN", "")  # optional — enables private repo listing

# ---------------------------------------------------------------------------
# LiveKit
# ---------------------------------------------------------------------------
LIVEKIT_URL: str = os.getenv("LIVEKIT_URL", "")
LIVEKIT_API_KEY: str = os.getenv("LIVEKIT_API_KEY", "")
LIVEKIT_API_SECRET: str = os.getenv("LIVEKIT_API_SECRET", "")

# ---------------------------------------------------------------------------
# OpenAI
# ---------------------------------------------------------------------------
OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")

# ---------------------------------------------------------------------------
# Deepgram
# ---------------------------------------------------------------------------
DEEPGRAM_API_KEY: str = os.getenv("DEEPGRAM_API_KEY", "")

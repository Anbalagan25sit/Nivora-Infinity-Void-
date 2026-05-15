"""
bridge.py — Local FastAPI HTTP server.
Lets n8n (and any other caller) control the browser, OS, Spotify, and GitHub
from Docker or a remote host.

Endpoints
---------
Browser / OS:
  POST /youtube          — search YouTube by query
  POST /youtube/url      — open an exact YouTube URL
  POST /open_app         — launch a Windows app
  POST /open_website     — open any URL in the browser
  POST /open_github      — open the configured GitHub profile

Spotify:
  POST /spotify/play     — search and play a track
  POST /spotify/pause    — pause playback
  POST /spotify/search   — search tracks (returns list)
  POST /spotify/shuffle  — set shuffle on/off

GitHub:
  POST /github/open      — open GitHub profile
  POST /github/repos     — list repos
  POST /github/open_repo — open a specific repo
  POST /github/latest    — open the most recently pushed repo

Health:
  GET  /health           — liveness check

Run:
  python bridge.py
  (or)  uvicorn bridge:app --host 0.0.0.0 --port 8001
"""

import logging
import subprocess
import urllib.parse
import webbrowser
from typing import Any

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

import github_tool
import spotify_tool
from config import GITHUB_USERNAME

# ---------------------------------------------------------------------------
# Bootstrap
# ---------------------------------------------------------------------------

load_dotenv(".env")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI(title="Nivora Bridge", version="1.0.0")

# CORS — allow all origins so n8n (Docker) can reach this server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Pydantic models
# ---------------------------------------------------------------------------

class SearchQuery(BaseModel):
    query: str


class UrlInput(BaseModel):
    url: str


class AppInput(BaseModel):
    app: str


class ShuffleInput(BaseModel):
    state: bool


class RepoInput(BaseModel):
    repo_name: str


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def _error(e: Exception, status_code: int = 500):
    logger.error("Request error: %s", e, exc_info=True)
    raise HTTPException(status_code=status_code, detail=str(e))


# ===========================================================================
# Browser / OS endpoints
# ===========================================================================

@app.post("/youtube")
def youtube_search(body: SearchQuery) -> dict[str, Any]:
    """Open a YouTube search results page for *query*."""
    logger.info("POST /youtube query=%r", body.query)
    try:
        encoded = urllib.parse.quote_plus(body.query)
        url = f"https://www.youtube.com/results?search_query={encoded}"
        webbrowser.open(url)
        return {"status": "ok", "opened": url}
    except Exception as e:
        _error(e)


@app.post("/youtube/url")
def youtube_open_url(body: UrlInput) -> dict[str, Any]:
    """Open an exact YouTube URL directly."""
    logger.info("POST /youtube/url url=%r", body.url)
    try:
        webbrowser.open(body.url)
        return {"status": "ok", "opened": body.url}
    except Exception as e:
        _error(e)


@app.post("/open_app")
def open_app(body: AppInput) -> dict[str, Any]:
    """Launch a Windows application by name (uses 'start' shell command)."""
    logger.info("POST /open_app app=%r", body.app)
    try:
        subprocess.Popen(["start", body.app], shell=True)
        return {"status": "ok", "app": body.app}
    except Exception as e:
        _error(e)


@app.post("/open_website")
def open_website(body: UrlInput) -> dict[str, Any]:
    """Open any URL in the default browser."""
    logger.info("POST /open_website url=%r", body.url)
    try:
        webbrowser.open(body.url)
        return {"status": "ok", "url": body.url}
    except Exception as e:
        _error(e)


@app.post("/open_github")
def open_github() -> dict[str, Any]:
    """Open the configured GitHub profile in the default browser."""
    logger.info("POST /open_github username=%r", GITHUB_USERNAME)
    try:
        result = github_tool.open_github_profile()
        if result["status"] == "error":
            raise HTTPException(status_code=500, detail=result["message"])
        return result
    except HTTPException:
        raise
    except Exception as e:
        _error(e)


# ===========================================================================
# Spotify endpoints
# ===========================================================================

@app.post("/spotify/play")
def spotify_play(body: SearchQuery) -> dict[str, Any]:
    """Search Spotify and play the best matching track."""
    logger.info("POST /spotify/play query=%r", body.query)
    try:
        result = spotify_tool.spotify_play(body.query)
        if result["status"] == "error":
            raise HTTPException(status_code=500, detail=result.get("message", "Unknown error"))
        return result
    except HTTPException:
        raise
    except Exception as e:
        _error(e)


@app.post("/spotify/pause")
def spotify_pause() -> dict[str, Any]:
    """Pause Spotify playback."""
    logger.info("POST /spotify/pause")
    try:
        result = spotify_tool.spotify_pause()
        if result["status"] == "error":
            raise HTTPException(status_code=500, detail=result.get("message", "Unknown error"))
        return result
    except HTTPException:
        raise
    except Exception as e:
        _error(e)


@app.post("/spotify/search")
def spotify_search(body: SearchQuery) -> list[dict[str, Any]]:
    """Search Spotify for tracks and return a list of results."""
    logger.info("POST /spotify/search query=%r", body.query)
    try:
        return spotify_tool.spotify_search(body.query)
    except Exception as e:
        _error(e)


@app.post("/spotify/shuffle")
def spotify_shuffle(body: ShuffleInput) -> dict[str, Any]:
    """Enable or disable Spotify shuffle mode."""
    logger.info("POST /spotify/shuffle state=%s", body.state)
    try:
        result = spotify_tool.spotify_shuffle(body.state)
        if result["status"] == "error":
            raise HTTPException(status_code=500, detail=result.get("message", "Unknown error"))
        return result
    except HTTPException:
        raise
    except Exception as e:
        _error(e)


# ===========================================================================
# GitHub endpoints
# ===========================================================================

@app.post("/github/open")
def github_open() -> dict[str, Any]:
    """Open the configured GitHub profile in the browser."""
    logger.info("POST /github/open")
    try:
        result = github_tool.open_github_profile()
        if result["status"] == "error":
            raise HTTPException(status_code=500, detail=result["message"])
        return result
    except HTTPException:
        raise
    except Exception as e:
        _error(e)


@app.post("/github/repos")
def github_repos() -> list[dict[str, Any]]:
    """Return the list of repos for the configured GitHub user."""
    logger.info("POST /github/repos")
    try:
        return github_tool.list_repos()
    except Exception as e:
        _error(e)


@app.post("/github/open_repo")
def github_open_repo(body: RepoInput) -> dict[str, Any]:
    """Open a specific repository page in the browser."""
    logger.info("POST /github/open_repo repo=%r", body.repo_name)
    try:
        result = github_tool.open_repo(body.repo_name)
        if result["status"] == "error":
            raise HTTPException(status_code=500, detail=result["message"])
        return result
    except HTTPException:
        raise
    except Exception as e:
        _error(e)


@app.post("/github/latest")
def github_latest() -> dict[str, Any]:
    """Open the most recently pushed repository in the browser."""
    logger.info("POST /github/latest")
    try:
        result = github_tool.open_latest_repo()
        if result["status"] == "error":
            raise HTTPException(status_code=500, detail=result["message"])
        return result
    except HTTPException:
        raise
    except Exception as e:
        _error(e)


# ===========================================================================
# Health check
# ===========================================================================

@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "bridge"}


# ===========================================================================
# Entrypoint
# ===========================================================================

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)

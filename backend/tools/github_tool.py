"""
GitHub tool layer — open profile/repos in the browser and list repos via the GitHub API.
Reads GITHUB_USERNAME and optional GITHUB_TOKEN from config.py (.env).
"""

import logging
import webbrowser
from typing import Any

import requests

from config import GITHUB_USERNAME, GITHUB_TOKEN

logger = logging.getLogger(__name__)

_GITHUB_API = "https://api.github.com"


def _api_headers() -> dict[str, str]:
    headers = {"Accept": "application/vnd.github+json"}
    if GITHUB_TOKEN:
        headers["Authorization"] = f"Bearer {GITHUB_TOKEN}"
    return headers


# ---------------------------------------------------------------------------
# Browser helpers
# ---------------------------------------------------------------------------

def open_github_profile() -> dict[str, Any]:
    """Open the configured GitHub profile in the default browser."""
    if not GITHUB_USERNAME:
        return {"status": "error", "message": "GITHUB_USERNAME not set in .env"}
    url = f"https://github.com/{GITHUB_USERNAME}"
    try:
        webbrowser.open(url)
        logger.info("Opened GitHub profile: %s", url)
        return {"status": "ok", "url": url}
    except Exception as e:
        logger.error("open_github_profile failed: %s", e)
        return {"status": "error", "message": str(e)}


def open_repo(repo_name: str) -> dict[str, Any]:
    """Open a specific repository page in the default browser."""
    if not GITHUB_USERNAME:
        return {"status": "error", "message": "GITHUB_USERNAME not set in .env"}
    url = f"https://github.com/{GITHUB_USERNAME}/{repo_name}"
    try:
        webbrowser.open(url)
        logger.info("Opened repo: %s", url)
        return {"status": "ok", "url": url}
    except Exception as e:
        logger.error("open_repo failed: %s", e)
        return {"status": "error", "message": str(e)}


# ---------------------------------------------------------------------------
# API helpers
# ---------------------------------------------------------------------------

def list_repos(per_page: int = 30) -> list[dict[str, Any]]:
    """
    Return a list of public (and private if GITHUB_TOKEN set) repos for the
    configured user, sorted by last push descending.
    """
    if not GITHUB_USERNAME:
        logger.warning("GITHUB_USERNAME not set — cannot list repos.")
        return []
    try:
        resp = requests.get(
            f"{_GITHUB_API}/users/{GITHUB_USERNAME}/repos",
            headers=_api_headers(),
            params={"per_page": per_page, "sort": "pushed", "direction": "desc"},
            timeout=10,
        )
        resp.raise_for_status()
        repos = resp.json()
        return [
            {
                "name": r.get("name", ""),
                "description": r.get("description") or "",
                "url": r.get("html_url", ""),
                "language": r.get("language") or "",
                "pushed_at": r.get("pushed_at", ""),
                "private": r.get("private", False),
            }
            for r in repos
        ]
    except Exception as e:
        logger.error("list_repos failed: %s", e)
        return []


def open_latest_repo() -> dict[str, Any]:
    """Open the most recently pushed repository in the default browser."""
    repos = list_repos(per_page=1)
    if not repos:
        return {"status": "error", "message": "No repos found or GitHub API unavailable."}
    repo = repos[0]
    url = repo["url"]
    try:
        webbrowser.open(url)
        logger.info("Opened latest repo: %s", url)
        return {"status": "ok", "url": url, "name": repo["name"]}
    except Exception as e:
        logger.error("open_latest_repo failed: %s", e)
        return {"status": "error", "message": str(e)}

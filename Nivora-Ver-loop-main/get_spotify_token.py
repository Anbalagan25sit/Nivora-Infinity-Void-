"""
One-time script to get SPOTIFY_REFRESH_TOKEN for the Spotify Web API.

1. Create an app at https://developer.spotify.com/dashboard
2. Add Redirect URI: http://localhost:8765/callback
3. Set SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET in .env
4. Run: python get_spotify_token.py
5. Open the URL in browser, log in to Spotify, approve
6. Copy the printed refresh_token into .env as SPOTIFY_REFRESH_TOKEN
"""

import os
import urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler

try:
    from dotenv import load_dotenv
    load_dotenv(".env")
except ImportError:
    pass

CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID", "").strip()
CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET", "").strip()
REDIRECT_URI = "https://localhost:8765/callback"
SCOPES = (
    "user-modify-playback-state user-read-playback-state user-read-currently-playing "
    "playlist-modify-public playlist-modify-private user-library-read user-library-modify user-read-email"
)
TOKEN_URL = "https://accounts.spotify.com/api/token"
AUTH_URL = "https://accounts.spotify.com/authorize"

auth_code: str | None = None


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        global auth_code
        if self.path.startswith("/callback"):
            query = self.path.split("?", 1)[-1]
            params = urllib.parse.parse_qs(query)
            auth_code = (params.get("code") or [None])[0]
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(
                b"<h1>Done</h1><p>You can close this tab and return to the terminal.</p>"
            )
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        pass


def main():
    if not CLIENT_ID or not CLIENT_SECRET:
        print("Set SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET in .env first.")
        print("Get them from https://developer.spotify.com/dashboard")
        return
    params = {
        "client_id": CLIENT_ID,
        "response_type": "code",
        "redirect_uri": REDIRECT_URI,
        "scope": SCOPES,
    }
    url = AUTH_URL + "?" + urllib.parse.urlencode(params)
    print("Open this URL in your browser, log in, and approve:")
    print(url)
    print("\nWaiting for callback on https://localhost:8765 ...")
    server = HTTPServer(("localhost", 8765), Handler)
    server.handle_request()
    if not auth_code:
        print("No authorization code received. Try again.")
        return
    import requests
    r = requests.post(
        TOKEN_URL,
        data={
            "grant_type": "authorization_code",
            "code": auth_code,
            "redirect_uri": REDIRECT_URI,
        },
        auth=(CLIENT_ID, CLIENT_SECRET),
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    r.raise_for_status()
    data = r.json()
    refresh = data.get("refresh_token")
    if refresh:
        print("\nAdd this to your .env file:\n")
        print(f"SPOTIFY_REFRESH_TOKEN={refresh}")
        print()
    else:
        print("Response:", data)


if __name__ == "__main__":
    main()

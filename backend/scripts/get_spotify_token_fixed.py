"""
Spotify Token Generator - Works with Dashboard URI Restrictions
----------------------------------------------------------------
Uses http://127.0.0.1:8888/callback instead of localhost
This IP address format is often accepted by Spotify dashboard.

Steps:
1. Go to https://developer.spotify.com/dashboard/applications
2. Click on your app
3. Click "Edit Settings"
4. Under "Redirect URIs" add EXACTLY: http://127.0.0.1:8888/callback
5. Click "Add"
6. Click "Save" at the bottom
7. Run this script

Usage:
    python get_spotify_token_fixed.py
"""

import os
import webbrowser
from urllib.parse import urlencode, parse_qs
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
from dotenv import load_dotenv, set_key

# Load environment
load_dotenv()

SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")

# Use 127.0.0.1 instead of localhost - often accepted by Spotify dashboard
REDIRECT_URI = "http://127.0.0.1:8888/callback"

# Required scopes
SCOPES = (
    "user-modify-playback-state "
    "user-read-playback-state "
    "user-read-currently-playing "
    "playlist-modify-public "
    "playlist-modify-private "
    "user-library-read "
    "user-library-modify "
    "user-read-email"
)

# Global to store authorization code
auth_code = None
server_running = True


class CallbackHandler(BaseHTTPRequestHandler):
    """Handles the OAuth callback from Spotify."""

    def log_message(self, format, *args):
        """Suppress server logs."""
        pass

    def do_GET(self):
        """Handle GET request from Spotify redirect."""
        global auth_code, server_running

        # Parse URL
        if self.path.startswith("/callback"):
            # Extract authorization code
            query = self.path.split("?")[1] if "?" in self.path else ""
            params = parse_qs(query)

            if "code" in params:
                auth_code = params["code"][0]

                # Send success page
                self.send_response(200)
                self.send_header("Content-type", "text/html")
                self.end_headers()

                success_html = """
                <!DOCTYPE html>
                <html>
                <head>
                    <title>Nivora - Success!</title>
                    <meta charset="UTF-8">
                    <style>
                        * { margin: 0; padding: 0; box-sizing: border-box; }
                        body {
                            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                            background: linear-gradient(135deg, #1DB954 0%, #1ed760 100%);
                            display: flex;
                            justify-content: center;
                            align-items: center;
                            min-height: 100vh;
                            padding: 20px;
                        }
                        .container {
                            background: white;
                            padding: 60px 40px;
                            border-radius: 20px;
                            text-align: center;
                            max-width: 500px;
                            box-shadow: 0 10px 40px rgba(0,0,0,0.3);
                        }
                        .icon {
                            font-size: 80px;
                            margin-bottom: 20px;
                            animation: bounce 0.5s ease;
                        }
                        @keyframes bounce {
                            0%, 100% { transform: translateY(0); }
                            50% { transform: translateY(-20px); }
                        }
                        h1 {
                            font-size: 32px;
                            color: #1DB954;
                            margin-bottom: 15px;
                        }
                        p {
                            font-size: 18px;
                            color: #666;
                            margin: 10px 0;
                            line-height: 1.6;
                        }
                        .success {
                            background: #1DB954;
                            color: white;
                            padding: 15px 30px;
                            border-radius: 10px;
                            margin: 20px 0;
                            font-weight: bold;
                        }
                        .note {
                            font-size: 14px;
                            color: #999;
                            margin-top: 30px;
                            padding-top: 20px;
                            border-top: 1px solid #eee;
                        }
                    </style>
                </head>
                <body>
                    <div class="container">
                        <div class="icon">🎵</div>
                        <h1>Authorization Successful!</h1>
                        <div class="success">✓ Connected to Spotify</div>
                        <p>Nivora can now control your Spotify playback.</p>
                        <p><strong>You can close this window.</strong></p>
                        <div class="note">
                            Return to your terminal to complete the setup.
                        </div>
                    </div>
                </body>
                </html>
                """

                self.wfile.write(success_html.encode())
                server_running = False

            elif "error" in params:
                # User denied authorization
                error = params["error"][0]

                self.send_response(200)
                self.send_header("Content-type", "text/html")
                self.end_headers()

                error_html = f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <title>Nivora - Authorization Required</title>
                    <meta charset="UTF-8">
                    <style>
                        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
                        body {{
                            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
                            display: flex;
                            justify-content: center;
                            align-items: center;
                            min-height: 100vh;
                            padding: 20px;
                        }}
                        .container {{
                            background: white;
                            padding: 60px 40px;
                            border-radius: 20px;
                            text-align: center;
                            max-width: 500px;
                            box-shadow: 0 10px 40px rgba(0,0,0,0.3);
                        }}
                        .icon {{ font-size: 80px; margin-bottom: 20px; }}
                        h1 {{ font-size: 32px; color: #f5576c; margin-bottom: 15px; }}
                        p {{ font-size: 18px; color: #666; margin: 10px 0; line-height: 1.6; }}
                        .error {{
                            background: #fee;
                            color: #c33;
                            padding: 15px;
                            border-radius: 10px;
                            margin: 20px 0;
                            font-family: monospace;
                        }}
                        .note {{
                            font-size: 14px;
                            color: #999;
                            margin-top: 30px;
                            padding-top: 20px;
                            border-top: 1px solid #eee;
                        }}
                    </style>
                </head>
                <body>
                    <div class="container">
                        <div class="icon">⚠️</div>
                        <h1>Authorization Denied</h1>
                        <p>Nivora needs permission to control Spotify.</p>
                        <div class="error">Error: {error}</div>
                        <p>Please run the script again and click <strong>"Agree"</strong>.</p>
                        <div class="note">
                            Without authorization, Spotify features won't work.
                        </div>
                    </div>
                </body>
                </html>
                """

                self.wfile.write(error_html.encode())
                server_running = False


def run_server():
    """Run the callback server."""
    server = HTTPServer(("127.0.0.1", 8888), CallbackHandler)
    while server_running:
        server.handle_request()


print("=" * 80)
print(" 🎵 Spotify Refresh Token Generator - Fixed for Dashboard Restrictions")
print("=" * 80)
print()

# Check credentials
if not SPOTIFY_CLIENT_ID or not SPOTIFY_CLIENT_SECRET:
    print("❌ ERROR: Missing Spotify credentials in .env file!")
    print()
    print("Add these to your .env file:")
    print("  SPOTIFY_CLIENT_ID=your_client_id_here")
    print("  SPOTIFY_CLIENT_SECRET=your_client_secret_here")
    print()
    print("Get them from: https://developer.spotify.com/dashboard")
    input("\nPress ENTER to exit...")
    exit(1)

print(f"✓ Client ID: {SPOTIFY_CLIENT_ID[:15]}...")
print(f"✓ Client Secret: {SPOTIFY_CLIENT_SECRET[:15]}...")
print()

print("=" * 80)
print(" ⚠️  IMPORTANT: Dashboard Configuration Required")
print("=" * 80)
print()
print("You MUST add the redirect URI to your Spotify app settings:")
print()
print("1. Go to: https://developer.spotify.com/dashboard/applications")
print(f"2. Click on your app (Client ID: {SPOTIFY_CLIENT_ID})")
print("3. Click 'Edit Settings'")
print("4. Under 'Redirect URIs', add EXACTLY this:")
print()
print("   ┌─────────────────────────────────────────┐")
print("   │  http://127.0.0.1:8888/callback         │")
print("   └─────────────────────────────────────────┘")
print()
print("5. Click 'Add'")
print("6. Click 'Save' at the bottom")
print()
print("NOTE: Use 127.0.0.1 (NOT localhost) - it's often accepted by Spotify!")
print()

input("Press ENTER after you've added the redirect URI...")
print()

print("=" * 80)
print(" 🚀 Starting Authorization Process")
print("=" * 80)
print()

# Start server
print("🌐 Starting callback server on http://127.0.0.1:8888...")
server_thread = threading.Thread(target=run_server, daemon=True)
server_thread.start()
print("✓ Server is running and waiting for callback")
print()

# Build authorization URL
auth_params = {
    "client_id": SPOTIFY_CLIENT_ID,
    "response_type": "code",
    "redirect_uri": REDIRECT_URI,
    "scope": SCOPES,
    "show_dialog": "true"
}

auth_url = f"https://accounts.spotify.com/authorize?{urlencode(auth_params)}"

# Open browser
print("🌍 Opening Spotify authorization page in your browser...")
print()
print(f"URL: {auth_url[:80]}...")
print()
webbrowser.open(auth_url)
print("✓ Browser opened")
print()
print("📋 Instructions:")
print("   1. Review the permissions Nivora is requesting")
print("   2. Click the green 'Agree' button")
print("   3. Wait for the success page")
print("   4. Come back here")
print()
print("⏳ Waiting for your authorization...")
print()

# Wait for callback
import time
timeout = 180  # 3 minutes
elapsed = 0
dots = 0

while auth_code is None and elapsed < timeout:
    time.sleep(1)
    elapsed += 1
    dots = (dots + 1) % 4
    print(f"\r   Waiting{'.' * dots}{' ' * (3 - dots)} ({elapsed}s)", end="", flush=True)

print()  # New line after waiting
print()

if auth_code is None:
    print("❌ ERROR: Authorization timeout!")
    print()
    print("Possible issues:")
    print("  • You didn't click 'Agree'")
    print("  • Browser blocked the redirect")
    print("  • Redirect URI not added to dashboard")
    print()
    print("Please verify the redirect URI is added correctly and try again.")
    input("\nPress ENTER to exit...")
    exit(1)

print("✓ Authorization code received!")
print(f"   Code: {auth_code[:20]}...")
print()

# Exchange code for tokens
print("🔄 Exchanging authorization code for tokens...")

import requests

token_data = {
    "grant_type": "authorization_code",
    "code": auth_code,
    "redirect_uri": REDIRECT_URI,
    "client_id": SPOTIFY_CLIENT_ID,
    "client_secret": SPOTIFY_CLIENT_SECRET,
}

try:
    response = requests.post(
        "https://accounts.spotify.com/api/token",
        data=token_data,
        timeout=10
    )

    if response.status_code != 200:
        print(f"❌ ERROR: Token exchange failed!")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text}")
        print()
        print("This usually means:")
        print("  • Redirect URI in dashboard doesn't match exactly")
        print("  • Authorization code already used or expired")
        print()
        input("Press ENTER to exit...")
        exit(1)

    tokens = response.json()

    access_token = tokens.get("access_token")
    refresh_token = tokens.get("refresh_token")
    expires_in = tokens.get("expires_in")

    if not refresh_token:
        print("❌ ERROR: No refresh token in response!")
        print(f"   Response: {tokens}")
        input("\nPress ENTER to exit...")
        exit(1)

    print("✓ Tokens received successfully!")
    print()

except Exception as e:
    print(f"❌ ERROR: Token exchange failed: {e}")
    input("\nPress ENTER to exit...")
    exit(1)

# Save to .env
print("💾 Saving refresh token to .env file...")

env_path = os.path.join(os.path.dirname(__file__), ".env")

try:
    set_key(env_path, "SPOTIFY_REFRESH_TOKEN", refresh_token)
    print("✓ Token saved to .env file!")
    print()
except Exception as e:
    print(f"⚠️  Warning: Could not auto-save to .env: {e}")
    print()
    print("Please manually add this line to your .env:")
    print()
    print(f"SPOTIFY_REFRESH_TOKEN={refresh_token}")
    print()

print("=" * 80)
print(" 🎉 SUCCESS! Setup Complete!")
print("=" * 80)
print()
print("Your Spotify Refresh Token:")
print("─" * 80)
print(refresh_token)
print("─" * 80)
print()
print("Token Details:")
print(f"  • Access Token:  {access_token[:30]}...")
print(f"  • Refresh Token: {refresh_token[:30]}...")
print(f"  • Expires in:    {expires_in // 60} minutes (will auto-refresh)")
print()
print("=" * 80)
print(" 🎯 Next Steps")
print("=" * 80)
print()
print("1. ✓ Refresh token saved to .env")
print("2. ▶  Start Nivora:  python agent.py start")
print("3. 🎤 Test command:  'Play Blinding Lights'")
print()
print("The refresh token never expires unless you revoke access.")
print("Nivora will automatically get new access tokens as needed.")
print()
print("=" * 80)
print(" ✅ All Done! Enjoy voice-controlled Spotify! 🎵")
print("=" * 80)
print()

input("Press ENTER to exit...")

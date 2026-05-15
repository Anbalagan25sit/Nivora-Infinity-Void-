"""
Spotify Token Generator - Local Server Method
----------------------------------------------
Runs a temporary local web server to catch the OAuth callback.
This is the EASIEST method - fully automated!

This script:
1. Starts a local web server on port 8888
2. Opens browser for Spotify authorization
3. Catches the redirect automatically
4. Gets your refresh token
5. Saves it to .env file

Usage:
    python get_spotify_token_server.py
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
REDIRECT_URI = "http://localhost:8888/callback"

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
                    <title>Nivora - Authorization Success</title>
                    <style>
                        body {
                            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                            display: flex;
                            justify-content: center;
                            align-items: center;
                            height: 100vh;
                            margin: 0;
                            color: white;
                        }
                        .container {
                            background: rgba(255, 255, 255, 0.1);
                            backdrop-filter: blur(10px);
                            padding: 50px;
                            border-radius: 20px;
                            text-align: center;
                            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
                        }
                        h1 { font-size: 48px; margin: 0 0 20px 0; }
                        p { font-size: 20px; margin: 10px 0; }
                        .check { font-size: 80px; color: #4ade80; }
                    </style>
                </head>
                <body>
                    <div class="container">
                        <div class="check">✓</div>
                        <h1>Authorization Successful!</h1>
                        <p>Nivora has been authorized to access your Spotify.</p>
                        <p><strong>You can close this window now.</strong></p>
                        <p style="font-size: 16px; margin-top: 30px; opacity: 0.8;">
                            Return to your terminal to complete setup.
                        </p>
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
                    <title>Nivora - Authorization Failed</title>
                    <style>
                        body {{
                            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
                            display: flex;
                            justify-content: center;
                            align-items: center;
                            height: 100vh;
                            margin: 0;
                            color: white;
                        }}
                        .container {{
                            background: rgba(255, 255, 255, 0.1);
                            backdrop-filter: blur(10px);
                            padding: 50px;
                            border-radius: 20px;
                            text-align: center;
                            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
                        }}
                        h1 {{ font-size: 48px; margin: 0 0 20px 0; }}
                        p {{ font-size: 20px; margin: 10px 0; }}
                        .cross {{ font-size: 80px; color: #fca5a5; }}
                    </style>
                </head>
                <body>
                    <div class="container">
                        <div class="cross">✗</div>
                        <h1>Authorization Denied</h1>
                        <p>You need to authorize Nivora to use Spotify features.</p>
                        <p>Error: {error}</p>
                        <p style="font-size: 16px; margin-top: 30px;">
                            Please run the script again and click "Agree".
                        </p>
                    </div>
                </body>
                </html>
                """

                self.wfile.write(error_html.encode())
                server_running = False


def run_server():
    """Run the callback server."""
    server = HTTPServer(("localhost", 8888), CallbackHandler)
    while server_running:
        server.handle_request()


print("=" * 70)
print(" 🎵 Spotify Refresh Token Generator - Automated Method")
print("=" * 70)
print()

# Check credentials
if not SPOTIFY_CLIENT_ID or not SPOTIFY_CLIENT_SECRET:
    print("❌ ERROR: Missing Spotify credentials in .env file!")
    print()
    print("Please add these to your .env file:")
    print("  SPOTIFY_CLIENT_ID=your_client_id")
    print("  SPOTIFY_CLIENT_SECRET=your_client_secret")
    print()
    print("Get them from: https://developer.spotify.com/dashboard")
    exit(1)

print(f"✓ Client ID found: {SPOTIFY_CLIENT_ID[:10]}...")
print(f"✓ Client Secret found: {SPOTIFY_CLIENT_SECRET[:10]}...")
print()

print("=" * 70)
print(" 📝 Instructions")
print("=" * 70)
print()
print("This script will:")
print("1. Start a local web server on port 8888")
print("2. Open Spotify authorization in your browser")
print("3. Automatically catch the callback")
print("4. Get your refresh token")
print("5. Save it to your .env file")
print()
print("When the browser opens:")
print("  → Click 'Agree' to authorize Nivora")
print("  → The page will show 'Authorization Successful!'")
print("  → Come back here to see your token")
print()

input("Press ENTER to start...")
print()

# Start server in background
print("🌐 Starting local server on http://localhost:8888...")
server_thread = threading.Thread(target=run_server, daemon=True)
server_thread.start()
print("✓ Server is running")
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
print("🌍 Opening Spotify authorization page...")
webbrowser.open(auth_url)
print("✓ Browser opened")
print()
print("⏳ Waiting for authorization...")
print("   (Click 'Agree' in your browser)")
print()

# Wait for callback
import time
timeout = 120  # 2 minutes
elapsed = 0

while auth_code is None and elapsed < timeout:
    time.sleep(1)
    elapsed += 1

if auth_code is None:
    print()
    print("❌ ERROR: Authorization timeout!")
    print("   No callback received within 2 minutes.")
    print()
    print("Please try again and make sure to click 'Agree'.")
    exit(1)

print("✓ Authorization received!")
print()

# Exchange code for tokens
print("🔄 Exchanging authorization code for refresh token...")

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
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        exit(1)

    tokens = response.json()

    access_token = tokens.get("access_token")
    refresh_token = tokens.get("refresh_token")
    expires_in = tokens.get("expires_in")

    if not refresh_token:
        print("❌ ERROR: No refresh token received!")
        print(f"Response: {tokens}")
        exit(1)

    print("✓ Tokens obtained successfully!")
    print()

except Exception as e:
    print(f"❌ ERROR: Failed to exchange code for tokens: {e}")
    exit(1)

# Save to .env file
print("💾 Saving refresh token to .env file...")

env_path = os.path.join(os.path.dirname(__file__), ".env")

try:
    # Update or add SPOTIFY_REFRESH_TOKEN
    set_key(env_path, "SPOTIFY_REFRESH_TOKEN", refresh_token)
    print("✓ Refresh token saved to .env!")
    print()

except Exception as e:
    print(f"⚠ Warning: Could not auto-save to .env: {e}")
    print()
    print("Please manually add this line to your .env file:")
    print()
    print(f"SPOTIFY_REFRESH_TOKEN={refresh_token}")
    print()

print("=" * 70)
print(" 🎉 SUCCESS! Setup Complete!")
print("=" * 70)
print()
print("Your Spotify Refresh Token:")
print("─" * 70)
print(refresh_token)
print("─" * 70)
print()
print("Token Details:")
print(f"  ✓ Access Token: {access_token[:30]}... (expires in {expires_in // 60} minutes)")
print(f"  ✓ Refresh Token: {refresh_token[:30]}... (never expires)")
print()
print("=" * 70)
print(" 🚀 Next Steps:")
print("=" * 70)
print()
print("1. ✓ Refresh token is already saved to .env")
print("2. Start Nivora: python agent.py start")
print("3. Connect to LiveKit room")
print("4. Test: Say 'Play Blinding Lights'")
print()
print("The refresh token never expires unless you revoke it.")
print("Nivora will automatically refresh the access token when needed.")
print()
print("=" * 70)
print(" ✓ All Done! You're ready to control Spotify with your voice! 🎵")
print("=" * 70)

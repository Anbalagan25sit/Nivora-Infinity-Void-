"""
Spotify Token Generator - Updated for Local Development
--------------------------------------------------------
Uses Spotify's Authorization Code Flow with manual code entry.
No redirect URI needed - works around HTTPS requirement.

This script helps you get a Spotify refresh token for use in Nivora.
Run this ONCE to get your refresh token, then add it to .env

Usage:
    python get_spotify_token_manual.py
"""

import os
import webbrowser
from urllib.parse import urlencode
from dotenv import load_dotenv

# Load environment
load_dotenv()

SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")

# Required scopes for Nivora
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

print("=" * 70)
print(" Spotify Refresh Token Generator - Manual Method")
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

print(f"✓ Client ID found: {SPOTIFY_CLIENT_ID[:8]}...")
print(f"✓ Client Secret found: {SPOTIFY_CLIENT_SECRET[:8]}...")
print()

print("=" * 70)
print(" STEP 1: Authorize with Spotify")
print("=" * 70)
print()
print("Instructions:")
print("1. A browser will open with Spotify authorization page")
print("2. Click 'Agree' to authorize Nivora")
print("3. You'll be redirected to a page that may show an error")
print("4. COPY THE ENTIRE URL from your browser address bar")
print("5. Come back here and paste it")
print()

input("Press ENTER to open browser...")
print()

# Build authorization URL
auth_params = {
    "client_id": SPOTIFY_CLIENT_ID,
    "response_type": "code",
    "redirect_uri": "http://localhost:8888/callback",
    "scope": SCOPES,
    "show_dialog": "true"
}

auth_url = f"https://accounts.spotify.com/authorize?{urlencode(auth_params)}"

# Open browser
print(f"Opening: {auth_url}")
print()
webbrowser.open(auth_url)

print("=" * 70)
print(" STEP 2: Get Authorization Code")
print("=" * 70)
print()
print("After authorizing, you'll be redirected to:")
print("  http://localhost:8888/callback?code=XXXXXXX")
print()
print("The page might show an error - THAT'S OK!")
print("Just copy the FULL URL from your browser's address bar.")
print()

redirect_url = input("Paste the full redirect URL here: ").strip()
print()

# Extract code from URL
if "code=" not in redirect_url:
    print("❌ ERROR: Invalid URL. The URL should contain 'code='")
    print()
    print("Example of what it should look like:")
    print("  http://localhost:8888/callback?code=AQBx7...")
    exit(1)

# Parse code
try:
    code = redirect_url.split("code=")[1].split("&")[0]
    print(f"✓ Authorization code extracted: {code[:20]}...")
    print()
except Exception as e:
    print(f"❌ ERROR: Could not parse authorization code: {e}")
    exit(1)

print("=" * 70)
print(" STEP 3: Exchange Code for Refresh Token")
print("=" * 70)
print()

# Exchange code for tokens
import requests

token_data = {
    "grant_type": "authorization_code",
    "code": code,
    "redirect_uri": "http://localhost:8888/callback",
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

    print("✓ Successfully obtained tokens!")
    print()

except Exception as e:
    print(f"❌ ERROR: Failed to exchange code for tokens: {e}")
    exit(1)

print("=" * 70)
print(" SUCCESS! 🎉")
print("=" * 70)
print()
print("Your Spotify Refresh Token:")
print()
print("─" * 70)
print(refresh_token)
print("─" * 70)
print()
print("=" * 70)
print(" NEXT STEPS:")
print("=" * 70)
print()
print("1. Copy the refresh token above")
print("2. Open your .env file")
print("3. Add this line (or update if it exists):")
print()
print(f"   SPOTIFY_REFRESH_TOKEN={refresh_token}")
print()
print("4. Save the .env file")
print("5. Start Nivora: python agent.py start")
print("6. Test: Say 'Play Blinding Lights'")
print()
print("=" * 70)
print()
print("Token Details:")
print(f"  Access Token: {access_token[:30]}... (expires in {expires_in}s)")
print(f"  Refresh Token: {refresh_token[:30]}... (never expires)")
print()
print("The refresh token is what you need - it never expires!")
print("Nivora will automatically refresh the access token when needed.")
print()
print("=" * 70)
print(" Setup Complete! ✓")
print("=" * 70)

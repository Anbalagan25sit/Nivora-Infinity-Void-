"""
Gmail Tool Setup Script
========================
One-time setup to authenticate Gmail API access.

Prerequisites:
1. Enable Gmail API in Google Cloud Console
2. Create OAuth2 credentials (Desktop app)
3. Download credentials.json to project root

Usage (from project root):
    python agent/tools/setup_gmail.py
"""

import os
from pathlib import Path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Gmail API scopes
SCOPES = [
    'https://www.googleapis.com/auth/gmail.send',
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.modify'
]

# Token storage paths
TOKEN_DIR = Path.home() / ".nivora"
TOKEN_FILE = TOKEN_DIR / "gmail_token.json"
CREDENTIALS_FILE = Path("credentials.json")


def authenticate_gmail():
    """Perform Gmail OAuth2 authentication."""
    try:
        if not CREDENTIALS_FILE.exists():
            raise FileNotFoundError(f"Missing {CREDENTIALS_FILE}")

        # Start OAuth flow
        flow = InstalledAppFlow.from_client_secrets_file(
            str(CREDENTIALS_FILE), SCOPES
        )
        creds = flow.run_local_server(port=0)

        # Save token
        TOKEN_DIR.mkdir(exist_ok=True)
        TOKEN_FILE.write_text(creds.to_json())

        # Test connection
        service = build('gmail', 'v1', credentials=creds)
        profile = service.users().getProfile(userId='me').execute()
        email = profile.get('emailAddress', 'Unknown')

        return f"[OK] Gmail authentication successful for {email}\nToken saved to {TOKEN_FILE}"

    except Exception as e:
        return f"Authentication failed: {str(e)}"


def main():
    print("=" * 60)
    print("Gmail API Authentication Setup for Nivora")
    print("=" * 60)
    print()

    # Check for credentials file
    if not CREDENTIALS_FILE.exists():
        print("[X] ERROR: credentials.json not found!")
        print()
        print("Setup instructions:")
        print("1. Go to https://console.cloud.google.com/")
        print("2. Enable Gmail API for your project")
        print("3. Create OAuth2 credentials (Desktop app)")
        print("4. Download credentials.json to project root")
        print(f"5. Expected location: {CREDENTIALS_FILE.absolute()}")
        print()
        print("See GMAIL_SETUP.md for detailed instructions")
        return 1

    print(f"[OK] Found credentials file: {CREDENTIALS_FILE}")
    print()
    print("Starting OAuth2 flow...")
    print("Your browser will open for Google account authorization.")
    print()

    # Authenticate
    result = authenticate_gmail()
    print()
    print(result)
    print()

    if TOKEN_FILE.exists():
        print(f"[OK] Token saved to: {TOKEN_FILE}")
        print()
        print("=" * 60)
        print("[SUCCESS] Setup complete! Gmail tools are ready to use.")
        print("=" * 60)
        print()
        print("Next steps:")
        print("1. Run tests: python agent/tools/test_gmail.py")
        print("2. Add GMAIL_TOOLS to your agent configuration")
        print("3. Try voice command: 'Give me my email summary'")
        return 0
    else:
        print("[X] Authentication failed - token not created")
        return 1


if __name__ == "__main__":
    import sys
    sys.exit(main())

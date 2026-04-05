"""
Google Sheets Tool Setup Script
================================
Adds Sheets API scope to existing Gmail OAuth token.

Prerequisites:
1. Gmail tool already set up (credentials.json exists)
2. Enable Google Sheets API in Google Cloud Console
3. Add Sheets scope to OAuth consent screen

Usage (from project root):
    python agent/tools/setup_sheets.py
"""

import os
import sys
from pathlib import Path

# Add to Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow


TOKEN_DIR = Path.home() / ".nivora"
TOKEN_FILE = TOKEN_DIR / "gmail_token.json"
CREDENTIALS_FILE = Path("credentials.json")

# Scopes including both Gmail and Sheets
SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/gmail.send',
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.modify'
]


def check_prerequisites():
    """Check if prerequisites are met."""
    print("\n" + "=" * 60)
    print("Checking Prerequisites")
    print("=" * 60)

    all_good = True

    # Check credentials.json
    if not CREDENTIALS_FILE.exists():
        print("[X] credentials.json not found")
        print(f"    Expected: {CREDENTIALS_FILE.absolute()}")
        all_good = False
    else:
        print(f"[OK] Found credentials.json")

    # Check if Gmail token exists
    if TOKEN_FILE.exists():
        print(f"[OK] Found existing token at {TOKEN_FILE}")
        print("    Will update with Sheets scope")
    else:
        print("[!] No existing token found")
        print("    Will create new token with both Gmail and Sheets")

    return all_good


def update_token():
    """Update token with Sheets scope."""
    print("\n" + "=" * 60)
    print("Updating OAuth Token")
    print("=" * 60)

    try:
        creds = None

        # Try to load existing token
        if TOKEN_FILE.exists():
            print("Loading existing token...")
            creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)

        # Check if we need to re-authenticate
        need_reauth = False

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    print("Refreshing expired token...")
                    creds.refresh(Request())
                except Exception as e:
                    print(f"[!] Refresh failed: {e}")
                    need_reauth = True
            else:
                need_reauth = True

        # Re-authenticate if needed
        if need_reauth:
            print("\nStarting OAuth flow...")
            print("Your browser will open for authorization.")
            print()

            flow = InstalledAppFlow.from_client_secrets_file(
                str(CREDENTIALS_FILE), SCOPES
            )
            creds = flow.run_local_server(port=0)

        # Save token
        TOKEN_DIR.mkdir(exist_ok=True)
        TOKEN_FILE.write_text(creds.to_json())

        print(f"[OK] Token saved to {TOKEN_FILE}")
        return creds

    except Exception as e:
        print(f"[X] Failed to update token: {e}")
        return None


def test_sheets_access(creds):
    """Test Sheets API access."""
    print("\n" + "=" * 60)
    print("Testing Sheets API Access")
    print("=" * 60)

    try:
        service = build('sheets', 'v4', credentials=creds)

        # Create a test spreadsheet
        print("Creating test spreadsheet...")
        spreadsheet = {
            'properties': {
                'title': 'Nivora Test Sheet (You can delete this)'
            }
        }

        result = service.spreadsheets().create(
            body=spreadsheet,
            fields='spreadsheetId,spreadsheetUrl'
        ).execute()

        spreadsheet_id = result.get('spreadsheetId')
        spreadsheet_url = result.get('spreadsheetUrl')

        print(f"[OK] Successfully created test spreadsheet!")
        print(f"    ID: {spreadsheet_id}")
        print(f"    URL: {spreadsheet_url}")
        print()
        print("    You can delete this test sheet from Google Drive")

        return True

    except Exception as e:
        print(f"[X] Sheets API test failed: {e}")
        return False


def test_gmail_access(creds):
    """Verify Gmail still works."""
    print("\n" + "=" * 60)
    print("Verifying Gmail Access")
    print("=" * 60)

    try:
        service = build('gmail', 'v1', credentials=creds)

        # Get profile to test access
        profile = service.users().getProfile(userId='me').execute()
        email = profile.get('emailAddress', 'Unknown')

        print(f"[OK] Gmail access still works!")
        print(f"    Account: {email}")

        return True

    except Exception as e:
        print(f"[X] Gmail access test failed: {e}")
        return False


def main():
    print("\n")
    print("=" * 60)
    print("Google Sheets API Setup for Nivora")
    print("=" * 60)

    # Check prerequisites
    if not check_prerequisites():
        print("\n[X] Prerequisites not met")
        print("\nRequired:")
        print("1. Run Gmail setup first: python agent/tools/setup_gmail.py")
        print("2. Enable Sheets API in Google Cloud Console")
        print("3. Add Sheets scope to OAuth consent screen")
        return 1

    # Update token with Sheets scope
    creds = update_token()
    if not creds:
        return 1

    # Test both APIs
    sheets_ok = test_sheets_access(creds)
    gmail_ok = test_gmail_access(creds)

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)

    if sheets_ok and gmail_ok:
        print("[OK] Sheets API: Working")
        print("[OK] Gmail API: Working")
        print()
        print("=" * 60)
        print("[SUCCESS] Setup complete!")
        print("=" * 60)
        print()
        print("Next steps:")
        print("1. Add SHEETS_TOOLS to your agent configuration")
        print("2. Try voice command: 'Create a spreadsheet called Test'")
        print("3. Try: 'Read my expenses sheet'")
        return 0
    else:
        print("[X] Some tests failed")
        print()
        print("Troubleshooting:")
        if not sheets_ok:
            print("- Enable Sheets API in Google Cloud Console")
            print("- Add scope to OAuth consent screen:")
            print("  https://www.googleapis.com/auth/spreadsheets")
        if not gmail_ok:
            print("- Verify Gmail API is still enabled")
            print("- Check OAuth scopes include Gmail")

        return 1


if __name__ == "__main__":
    sys.exit(main())

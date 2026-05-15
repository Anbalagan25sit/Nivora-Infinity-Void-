"""
test_google_tools.py — Test Google Sheets read/write and Calendar tools.
Run:  python test_google_tools.py

Requirements:
  - GOOGLE_APPLICATION_CREDENTIALS set in .env (path to service account JSON)
  - gspread installed: pip install gspread
  - The service account must have access to the sheet you're testing
  - For Calendar: token.json must exist (run OAuth flow once)
"""
import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# Force UTF-8 on Windows
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

_env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=_env_path, override=True)

SEP = "=" * 60
print(SEP)
print("  NIVORA — Google Tools Test")
print(SEP)

CREDS_FILE = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "gcp-credentials.json")
print(f"  Credentials file : {CREDS_FILE}")
print(f"  Credentials exist: {os.path.exists(CREDS_FILE)}")
print(SEP)


# ─── 1. GOOGLE SHEETS READ ────────────────────────────────────────────────────
print("\n[1/3] Testing Google Sheets READ ...")

# <<< Set this to the exact name of a Google Sheet your service acc can access >>>
TEST_SHEET_NAME = "Nivora Test"  # Your actual Google Sheet name

try:
    import gspread
    gc = gspread.service_account(filename=CREDS_FILE)
    sh = gc.open(TEST_SHEET_NAME)
    worksheet = sh.sheet1
    records = worksheet.get_all_records()
    print(f"  [OK] READ passed — {len(records)} row(s) found.")
    if records:
        print(f"  First row: {records[0]}")
    else:
        print("  (Sheet is empty — that's OK for a fresh sheet)")
except FileNotFoundError:
    print(f"  [SKIP] Credentials file not found: {CREDS_FILE}")
    print("         → Set GOOGLE_APPLICATION_CREDENTIALS in .env")
except gspread.exceptions.SpreadsheetNotFound:
    print(f"  [FAIL] Sheet '{TEST_SHEET_NAME}' not found.")
    print("         → Make sure the sheet exists AND is shared with the service account email.")
    print("         → Or change TEST_SHEET_NAME in this script.")
except Exception as e:
    print(f"  [FAIL] READ error: {e}")


# ─── 2. GOOGLE SHEETS WRITE ───────────────────────────────────────────────────
print("\n[2/3] Testing Google Sheets WRITE ...")
try:
    import gspread
    from datetime import datetime

    gc = gspread.service_account(filename=CREDS_FILE)
    sh = gc.open(TEST_SHEET_NAME)
    worksheet = sh.sheet1
    test_row = ["Nivora Test", datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "Auto-written by test_google_tools.py"]
    worksheet.append_row(test_row)
    print(f"  [OK] WRITE passed — Appended row: {test_row}")
except FileNotFoundError:
    print(f"  [SKIP] Credentials file not found: {CREDS_FILE}")
except gspread.exceptions.SpreadsheetNotFound:
    print(f"  [FAIL] Sheet '{TEST_SHEET_NAME}' not found (same as READ — fix READ first).")
except Exception as e:
    print(f"  [FAIL] WRITE error: {e}")


# ─── 3. GOOGLE CALENDAR ───────────────────────────────────────────────────────
print("\n[3/3] Testing Google Calendar (via Service Account) ...")
try:
    from google.oauth2 import service_account
    from googleapiclient.discovery import build
    import datetime

    SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]
    creds = service_account.Credentials.from_service_account_file(CREDS_FILE, scopes=SCOPES)
    service = build("calendar", "v3", credentials=creds)

    # "primary" = service account's own calendar (empty)
    # Use the actual Gmail address of the calendar owner
    calendar_id = os.getenv("GMAIL_USER") or os.getenv("EMAIL_USER") or "primary"
    now = datetime.datetime.utcnow().isoformat() + "Z"
    events_result = service.events().list(
        calendarId=calendar_id, timeMin=now, maxResults=5,
        singleEvents=True, orderBy="startTime"
    ).execute()
    events = events_result.get("items", [])
    if not events:
        print("  [OK] Calendar connected — no upcoming events.")
        print("       (If you expected events, share your personal calendar with the service account email)")
    else:
        print(f"  [OK] Calendar connected — {len(events)} upcoming event(s):")
        for ev in events:
            start = ev["start"].get("dateTime", ev["start"].get("date"))
            print(f"       • {start}: {ev.get('summary', '(no title)')}")
except FileNotFoundError:
    print(f"  [SKIP] Credentials file not found: {CREDS_FILE}")
except Exception as e:
    print(f"  [FAIL] Calendar error: {e}")
    if "CalendarNotFound" in str(e) or "notFound" in str(e):
        print("         → Share your Google Calendar with the service account:")
        print(f"           {CREDS_FILE.split('//')[-1]} → client_email field")
    elif "accessNotConfigured" in str(e):
        print("         → Enable the Google Calendar API in your GCP project:")
        print("           https://console.cloud.google.com/apis/library/calendar-json.googleapis.com")

print("\n" + SEP)
print("  Done. Fix any [FAIL] items above before enabling tools in ALL_TOOLS.")
print(SEP)

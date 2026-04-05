"""
test_gmail.py — Quick test for send_email (SMTP) and read_emails (IMAP).
Run:  python test_gmail.py
"""
import sys
import os
import imaplib
import smtplib
import email as _email
from email.header import decode_header as _decode_header
from email.mime.text import MIMEText
from pathlib import Path
from dotenv import load_dotenv

# Force UTF-8 on Windows console so output doesn't crash
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# Load .env from THIS script's directory (not cwd)
_env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=_env_path, override=True)

USER     = os.getenv("EMAIL_USER") or os.getenv("GMAIL_USER", "")
PASSWORD = os.getenv("EMAIL_PASS") or os.getenv("GMAIL_APP_PASSWORD", "")

SEP = "=" * 55
print(SEP)
print("  FRIDAY JARVIS - Gmail Tool Test")
print(SEP)
print(f"  .env path : {_env_path}")
print(f"  Account   : {USER or 'NOT SET'}")
print(f"  Password  : {'OK (' + str(len(PASSWORD)) + ' chars)' if PASSWORD else 'NOT SET'}")
print(SEP)

if not USER or not PASSWORD:
    print("\n  ERROR: Credentials not loaded. Check your .env file.")
    sys.exit(1)

# ─── 1. SEND TEST (SMTP / TLS port 587) ──────────────────────
print("\n[1/2] Testing SEND (SMTP port 587 / STARTTLS) ...")
try:
    msg = MIMEText("Automated test from Friday JARVIS. Safe to delete.")
    msg["Subject"] = "Friday JARVIS - SMTP test"
    msg["From"]    = USER
    msg["To"]      = USER   # send to yourself

    with smtplib.SMTP("smtp.gmail.com", 587, timeout=15) as server:
        server.ehlo()
        server.starttls()
        server.login(USER, PASSWORD)
        server.sendmail(USER, USER, msg.as_string())

    print("  [OK] SEND passed - check your inbox for the test email.")
except smtplib.SMTPAuthenticationError as e:
    print(f"  [FAIL] Auth error: {e}")
    print("         -> Regenerate App Password: myaccount.google.com/apppasswords")
    print("            Paste the 16 chars with NO hyphens into .env EMAIL_PASS")
except Exception as e:
    print(f"  [FAIL] SEND error: {e}")

# ─── 2. READ TEST (IMAP / SSL port 993) ──────────────────────
print("\n[2/2] Testing READ (IMAP port 993 / SSL) ...")
try:
    mail = imaplib.IMAP4_SSL("imap.gmail.com", 993)
    mail.login(USER, PASSWORD)
    mail.select("inbox")

    _, data = mail.search(None, "ALL")
    ids = data[0].split() if data and data[0] else []
    print(f"  [OK] READ passed - {len(ids)} email(s) in inbox.")

    if ids:
        print("\n  3 most recent subjects:")
        for mid in reversed(ids[-3:]):
            _, msg_data = mail.fetch(mid, "(RFC822)")
            if not msg_data or not msg_data[0]:
                continue
            raw = msg_data[0][1]
            if not isinstance(raw, bytes):
                continue
            msg = _email.message_from_bytes(raw)
            parts = _decode_header(msg.get("Subject", "(no subject)"))
            subject = ""
            for part, enc in parts:
                if isinstance(part, bytes):
                    subject += part.decode(enc or "utf-8", errors="replace")
                else:
                    subject += str(part)
            frm = msg.get("From", "?")
            print(f"    - {subject[:55]}")
            print(f"      from: {frm[:50]}")
    mail.logout()
except imaplib.IMAP4.error as e:
    print(f"  [FAIL] IMAP auth error: {e}")
    print("         -> Enable IMAP: Gmail -> Settings -> Forwarding and POP/IMAP")
except Exception as e:
    print(f"  [FAIL] READ error: {e}")

print("\n" + SEP)


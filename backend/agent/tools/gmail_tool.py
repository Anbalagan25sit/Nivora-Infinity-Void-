"""
Gmail Tool for Nivora Voice Agent
==================================
Provides Gmail integration via Google API with OAuth2 authentication.
All functions are registered as LiveKit AI callables for voice commands.

Voice Commands Supported:
- "Send email to X about Y"
- "Read my unread emails"
- "Search emails from professor"
- "Reply to that thread saying..."
- "Give me my email summary"

Setup:
1. Enable Gmail API in Google Cloud Console
2. Download credentials.json to project root
3. Run authenticate_gmail() once to get token
4. Token cached in ~/.nivora/gmail_token.json
"""

import os
import base64
import json
from pathlib import Path
from typing import Optional, List, Dict
from datetime import datetime, timedelta
from email.mime.text import MIMEText

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Try to import LiveKit agents - gracefully handle if not installed (for testing)
try:
    from livekit.agents.llm import function_tool
    LIVEKIT_AVAILABLE = True
except ImportError:
    LIVEKIT_AVAILABLE = False
    # Create a dummy decorator for testing without LiveKit
    def function_tool(func):
        return func

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


class GmailService:
    """Gmail API service wrapper with OAuth2 authentication."""

    def __init__(self):
        self._service = None
        self._last_thread_id = None  # Store last mentioned thread for replies

    def _get_credentials(self) -> Optional[Credentials]:
        """Get valid credentials, refreshing if necessary."""
        creds = None

        # Load cached token if exists
        if TOKEN_FILE.exists():
            creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)

        # Refresh expired credentials
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception as e:
                print(f"Token refresh failed: {e}")
                creds = None

        # No valid credentials - need to authenticate
        if not creds or not creds.valid:
            if not CREDENTIALS_FILE.exists():
                raise FileNotFoundError(
                    f"Missing {CREDENTIALS_FILE}. Download from Google Cloud Console."
                )

            flow = InstalledAppFlow.from_client_secrets_file(
                str(CREDENTIALS_FILE), SCOPES
            )
            creds = flow.run_local_server(port=0)

            # Save token for future use
            TOKEN_DIR.mkdir(exist_ok=True)
            TOKEN_FILE.write_text(creds.to_json())

        return creds

    def get_service(self):
        """Get or create Gmail API service instance."""
        if self._service is None:
            creds = self._get_credentials()
            self._service = build('gmail', 'v1', credentials=creds)
        return self._service


# Singleton service instance
gmail_service = GmailService()


def _create_message(to: str, subject: str, body: str) -> Dict:
    """Create email message in Gmail API format."""
    message = MIMEText(body)
    message['to'] = to
    message['subject'] = subject

    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
    return {'raw': raw_message}


def _create_reply(original_message: Dict, reply_body: str) -> Dict:
    """Create reply message preserving thread context."""
    headers = {h['name']: h['value'] for h in original_message['payload']['headers']}

    message = MIMEText(reply_body)
    message['to'] = headers.get('From', '')
    message['subject'] = headers.get('Subject', '')

    # Add threading headers
    if 'Message-ID' in headers:
        message['In-Reply-To'] = headers['Message-ID']
        message['References'] = headers['Message-ID']

    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
    return {
        'raw': raw_message,
        'threadId': original_message['threadId']
    }


def _format_email(msg: Dict) -> str:
    """Format email message for voice readout."""
    headers = {h['name']: h['value'] for h in msg['payload']['headers']}

    sender = headers.get('From', 'Unknown')
    subject = headers.get('Subject', 'No subject')
    date_str = headers.get('Date', '')

    # Parse date
    try:
        date_obj = datetime.strptime(date_str, '%a, %d %b %Y %H:%M:%S %z')
        formatted_date = date_obj.strftime('%B %d at %I:%M %p')
    except:
        formatted_date = date_str

    # Get snippet
    snippet = msg.get('snippet', '')

    # Store thread ID for potential replies
    thread_id = msg.get('threadId', '')

    return f"From {sender} on {formatted_date}:\nSubject: {subject}\n{snippet}\n[Thread ID: {thread_id}]"


@function_tool()
def send_email(
    to: str,
    subject: str,
    body: str
) -> str:
    """
    Send an email via Gmail.

    Args:
        to: Recipient email address
        subject: Email subject line
        body: Email body text

    Returns:
        Confirmation message with email ID

    Voice command examples:
        "Send email to john@example.com about meeting tomorrow"
        "Email my professor saying I'll be late"
    """
    try:
        service = gmail_service.get_service()
        message = _create_message(to, subject, body)

        result = service.users().messages().send(
            userId='me',
            body=message
        ).execute()

        return f"Email sent successfully to {to}. Message ID: {result['id']}"

    except HttpError as e:
        return f"Gmail API error: {e.reason}"
    except Exception as e:
        return f"Failed to send email: {str(e)}"


@function_tool()
def read_emails(
    max_results: int = 5,
    query: str = "is:unread"
) -> str:
    """
    Read emails from inbox matching query.

    Args:
        max_results: Maximum number of emails to fetch (default: 5)
        query: Gmail search query (default: "is:unread")
               Examples: "from:boss@company.com", "has:attachment", "is:starred"

    Returns:
        Formatted list of emails with sender, subject, snippet, and date

    Voice command examples:
        "Read my unread emails"
        "Show me emails from yesterday"
        "What are my important emails?"
    """
    try:
        service = gmail_service.get_service()

        # Search for messages
        results = service.users().messages().list(
            userId='me',
            q=query,
            maxResults=max_results
        ).execute()

        messages = results.get('messages', [])

        if not messages:
            return f"No emails found matching '{query}'."

        # Fetch full message details
        formatted_emails = []
        for msg in messages:
            full_msg = service.users().messages().get(
                userId='me',
                id=msg['id'],
                format='full'
            ).execute()

            formatted_emails.append(_format_email(full_msg))

            # Store last thread ID for potential replies
            gmail_service._last_thread_id = full_msg.get('threadId')

        header = f"Found {len(messages)} email(s):\n\n"
        return header + "\n\n---\n\n".join(formatted_emails)

    except HttpError as e:
        return f"Gmail API error: {e.reason}"
    except Exception as e:
        return f"Failed to read emails: {str(e)}"


@function_tool()
def search_emails(
    query: str,
    max_results: int = 10
) -> str:
    """
    Search emails using Gmail query syntax.

    Args:
        query: Gmail search query
               Syntax examples:
               - "from:sender@example.com" - emails from specific sender
               - "to:me subject:meeting" - emails to you with "meeting" in subject
               - "has:attachment is:unread" - unread emails with attachments
               - "after:2024/01/01 before:2024/12/31" - date range
               - "larger:5M" - emails larger than 5MB
        max_results: Maximum emails to return (default: 10)

    Returns:
        Formatted search results

    Voice command examples:
        "Search emails from my professor"
        "Find emails with attachments from last week"
        "Search for emails about the project deadline"
    """
    try:
        service = gmail_service.get_service()

        results = service.users().messages().list(
            userId='me',
            q=query,
            maxResults=max_results
        ).execute()

        messages = results.get('messages', [])

        if not messages:
            return f"No emails found for query: '{query}'"

        # Fetch message details
        formatted_emails = []
        for msg in messages:
            full_msg = service.users().messages().get(
                userId='me',
                id=msg['id'],
                format='full'
            ).execute()

            formatted_emails.append(_format_email(full_msg))

        header = f"Search results for '{query}' ({len(messages)} found):\n\n"
        return header + "\n\n---\n\n".join(formatted_emails)

    except HttpError as e:
        return f"Gmail API error: {e.reason}"
    except Exception as e:
        return f"Failed to search emails: {str(e)}"


@function_tool()
def reply_to_email(
    thread_id: str,
    body: str
) -> str:
    """
    Reply to an email thread.

    Args:
        thread_id: Thread ID of the email to reply to
                   (shown in brackets when reading emails)
                   Use "last" to reply to the most recently read email
        body: Reply message body

    Returns:
        Confirmation message

    Voice command examples:
        "Reply to that thread saying I'll be there"
        "Reply to the last email with thanks"
    """
    try:
        service = gmail_service.get_service()

        # Handle "last" keyword
        if thread_id.lower() == "last":
            if not gmail_service._last_thread_id:
                return "No recent email thread to reply to. Please read an email first."
            thread_id = gmail_service._last_thread_id

        # Get original message
        thread = service.users().threads().get(
            userId='me',
            id=thread_id
        ).execute()

        original_message = thread['messages'][0]

        # Create and send reply
        reply_message = _create_reply(original_message, body)

        result = service.users().messages().send(
            userId='me',
            body=reply_message
        ).execute()

        # Get subject for confirmation
        headers = {h['name']: h['value'] for h in original_message['payload']['headers']}
        subject = headers.get('Subject', 'the email')

        return f"Reply sent successfully to thread '{subject}'. Message ID: {result['id']}"

    except HttpError as e:
        return f"Gmail API error: {e.reason}"
    except Exception as e:
        return f"Failed to send reply: {str(e)}"


@function_tool()
def get_email_summary() -> str:
    """
    Get summary of inbox status.

    Returns:
        Summary with:
        - Total unread count
        - Important emails today
        - Recent senders

    Perfect for morning briefing voice command:
        "Give me my email summary"
        "What's my inbox status?"
        "Anything important in my email?"
    """
    try:
        service = gmail_service.get_service()

        # Get unread count
        unread_results = service.users().messages().list(
            userId='me',
            q='is:unread',
            maxResults=100
        ).execute()
        unread_count = len(unread_results.get('messages', []))

        # Get important emails from today
        today = datetime.now().strftime('%Y/%m/%d')
        important_results = service.users().messages().list(
            userId='me',
            q=f'is:important after:{today}',
            maxResults=5
        ).execute()

        important_messages = important_results.get('messages', [])

        summary_parts = [
            f"📧 Email Summary:",
            f"• {unread_count} unread emails"
        ]

        if important_messages:
            summary_parts.append(f"• {len(important_messages)} important emails today:")

            for msg in important_messages:
                full_msg = service.users().messages().get(
                    userId='me',
                    id=msg['id'],
                    format='full'
                ).execute()

                headers = {h['name']: h['value'] for h in full_msg['payload']['headers']}
                sender = headers.get('From', 'Unknown').split('<')[0].strip()
                subject = headers.get('Subject', 'No subject')

                summary_parts.append(f"  - From {sender}: {subject}")
        else:
            summary_parts.append("• No important emails today")

        # Get recent senders (last 10 emails)
        recent_results = service.users().messages().list(
            userId='me',
            maxResults=10
        ).execute()

        recent_messages = recent_results.get('messages', [])
        if recent_messages:
            senders = set()
            for msg in recent_messages:
                full_msg = service.users().messages().get(
                    userId='me',
                    id=msg['id'],
                    format='metadata',
                    metadataHeaders=['From']
                ).execute()

                headers = {h['name']: h['value'] for h in full_msg['payload']['headers']}
                sender = headers.get('From', '').split('<')[0].strip()
                if sender:
                    senders.add(sender)

            if senders:
                summary_parts.append(f"• Recent senders: {', '.join(list(senders)[:5])}")

        return "\n".join(summary_parts)

    except HttpError as e:
        return f"Gmail API error: {e.reason}"
    except Exception as e:
        return f"Failed to get email summary: {str(e)}"


def authenticate_gmail() -> str:
    """
    One-time authentication setup.
    Run this manually to generate token.json.

    Returns:
        Success message or error details
    """
    try:
        gmail_service._service = None  # Force re-authentication
        service = gmail_service.get_service()

        # Test the connection
        profile = service.users().getProfile(userId='me').execute()
        email = profile.get('emailAddress', 'Unknown')

        return f"✓ Gmail authentication successful for {email}\nToken saved to {TOKEN_FILE}"

    except Exception as e:
        return f"Authentication failed: {str(e)}"


# Export all AI callable functions for LiveKit agent registration
GMAIL_TOOLS = [
    send_email,
    read_emails,
    search_emails,
    reply_to_email,
    get_email_summary
]


if __name__ == "__main__":
    # Manual authentication test
    print("Starting Gmail authentication...")
    print(authenticate_gmail())

"""
Google Sheets Tool for Nivora Voice Agent
==========================================
Provides Google Sheets integration via Sheets API v4.
All functions are registered as LiveKit function tools for voice commands.

Voice Commands Supported:
- "Read my expenses sheet"
- "Add a row to my tracker: date, task, done"
- "Search my sheet for Nivora"
- "Create a new spreadsheet called Project Tracker"
- "How many rows are in my sheet?"

Setup:
1. Enable Google Sheets API in Google Cloud Console
2. Add sheets scope to OAuth consent screen
3. Reuses existing Gmail OAuth token from ~/.nivora/gmail_token.json
4. Token refreshes automatically
"""

import os
import re
from pathlib import Path
from typing import Optional, List, Dict, Any

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Try to import LiveKit function_tool
try:
    from livekit.agents.llm import function_tool
    LIVEKIT_AVAILABLE = True
except ImportError:
    LIVEKIT_AVAILABLE = False
    def function_tool(func):
        return func

# Google Sheets API scopes (includes Gmail scopes for token reuse)
SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/gmail.send',
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.modify'
]

# Token storage paths (reuse Gmail token)
TOKEN_DIR = Path.home() / ".nivora"
TOKEN_FILE = TOKEN_DIR / "gmail_token.json"
CREDENTIALS_FILE = Path("credentials.json")


class SheetsService:
    """Google Sheets API service wrapper with OAuth2 authentication."""

    def __init__(self):
        self._service = None

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
                # Save refreshed token
                TOKEN_DIR.mkdir(exist_ok=True)
                TOKEN_FILE.write_text(creds.to_json())
            except Exception as e:
                print(f"Token refresh failed: {e}")
                creds = None

        # No valid credentials - need to re-authenticate
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
        """Get or create Sheets API service instance."""
        if self._service is None:
            creds = self._get_credentials()
            self._service = build('sheets', 'v4', credentials=creds)
        return self._service

    def _extract_spreadsheet_id(self, url_or_id: str) -> str:
        """Extract spreadsheet ID from URL or return ID as-is."""
        # If it's a URL, extract the ID
        if "docs.google.com/spreadsheets" in url_or_id:
            match = re.search(r'/d/([a-zA-Z0-9-_]+)', url_or_id)
            if match:
                return match.group(1)

        # Return as-is (assume it's already an ID)
        return url_or_id

    def _format_table(self, values: List[List[Any]], max_cols: int = 10) -> str:
        """Format sheet data as a readable table."""
        if not values:
            return "(Empty sheet)"

        # Limit columns for voice readout
        formatted_rows = []
        for i, row in enumerate(values[:20], 1):  # Limit to 20 rows
            # Pad row to consistent length
            row_data = row[:max_cols] + [''] * (max_cols - len(row))
            row_data = row_data[:max_cols]

            # Format row
            formatted_row = f"Row {i}: " + ", ".join([str(cell) for cell in row_data if cell])
            formatted_rows.append(formatted_row)

        if len(values) > 20:
            formatted_rows.append(f"... and {len(values) - 20} more rows")

        return "\n".join(formatted_rows)


# Singleton service instance
sheets_service = SheetsService()


@function_tool()
def read_sheet(
    spreadsheet_id: str,
    range: str = "Sheet1!A1:Z100"
) -> str:
    """
    Read data from a Google Sheet.

    Args:
        spreadsheet_id: Spreadsheet ID or full URL
        range: Range in A1 notation (default: "Sheet1!A1:Z100")
               Examples: "Sheet1!A1:B10", "Data!A:C"

    Returns:
        Formatted table as string

    Voice command examples:
        "Read my expenses sheet"
        "Show me the data in my tracker"
        "What's in my sheet?"
    """
    try:
        service = sheets_service.get_service()
        spreadsheet_id = sheets_service._extract_spreadsheet_id(spreadsheet_id)

        # Read values
        result = service.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id,
            range=range
        ).execute()

        values = result.get('values', [])

        if not values:
            return f"No data found in range {range}"

        # Get spreadsheet title
        sheet_metadata = service.spreadsheets().get(
            spreadsheetId=spreadsheet_id
        ).execute()
        title = sheet_metadata.get('properties', {}).get('title', 'Spreadsheet')

        # Format output
        formatted_data = sheets_service._format_table(values)

        return f"Spreadsheet: {title}\nRange: {range}\n\n{formatted_data}"

    except HttpError as e:
        return f"Sheets API error: {e.reason if hasattr(e, 'reason') else str(e)}"
    except Exception as e:
        return f"Failed to read sheet: {str(e)}"


@function_tool()
def write_to_sheet(
    spreadsheet_id: str,
    range: str,
    values: List[List[Any]]
) -> str:
    """
    Write data to specific cells in a Google Sheet.

    Args:
        spreadsheet_id: Spreadsheet ID or URL
        range: Target range in A1 notation (e.g., "Sheet1!A1")
        values: 2D array of values to write
                Example: [["Name", "Score"], ["Alice", 95], ["Bob", 87]]

    Returns:
        Success message with cells updated

    Voice command examples:
        "Write headers Name and Score to my sheet"
        "Update cell A1 with total expenses"
    """
    try:
        service = sheets_service.get_service()
        spreadsheet_id = sheets_service._extract_spreadsheet_id(spreadsheet_id)

        body = {
            'values': values
        }

        result = service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range=range,
            valueInputOption='USER_ENTERED',
            body=body
        ).execute()

        cells_updated = result.get('updatedCells', 0)

        return f"Successfully updated {cells_updated} cells in range {range}"

    except HttpError as e:
        return f"Sheets API error: {e.reason if hasattr(e, 'reason') else str(e)}"
    except Exception as e:
        return f"Failed to write to sheet: {str(e)}"


@function_tool()
def append_row(
    spreadsheet_id: str,
    values: List[Any],
    sheet_name: str = "Sheet1"
) -> str:
    """
    Append a new row at the bottom of the data in a sheet.

    Args:
        spreadsheet_id: Spreadsheet ID or URL
        values: List of values for the new row
                Example: ["2024-03-30", "Completed task", "Yes"]
        sheet_name: Sheet name (default: "Sheet1")

    Returns:
        Success message with row number

    Voice command examples:
        "Add a row to my tracker: today, finish report, done"
        "Log this to my expenses: groceries, 45.50, food"
        "Append to my sheet: John, Developer, hired"
    """
    try:
        service = sheets_service.get_service()
        spreadsheet_id = sheets_service._extract_spreadsheet_id(spreadsheet_id)

        # Format as 2D array
        body = {
            'values': [values]
        }

        result = service.spreadsheets().values().append(
            spreadsheetId=spreadsheet_id,
            range=f"{sheet_name}!A:A",
            valueInputOption='USER_ENTERED',
            insertDataOption='INSERT_ROWS',
            body=body
        ).execute()

        # Get updated range to find row number
        updated_range = result.get('updates', {}).get('updatedRange', '')
        row_match = re.search(r'!A(\d+)', updated_range)
        row_number = row_match.group(1) if row_match else '?'

        return f"Added row {row_number} to {sheet_name}: {', '.join([str(v) for v in values])}"

    except HttpError as e:
        return f"Sheets API error: {e.reason if hasattr(e, 'reason') else str(e)}"
    except Exception as e:
        return f"Failed to append row: {str(e)}"


@function_tool()
def search_sheet(
    spreadsheet_id: str,
    query: str
) -> str:
    """
    Search for a value across all cells in a spreadsheet.

    Args:
        spreadsheet_id: Spreadsheet ID or URL
        query: Search term to find

    Returns:
        Matching rows with row numbers

    Voice command examples:
        "Search my sheet for Nivora"
        "Find Alice in my spreadsheet"
        "Look for expenses over 100"
    """
    try:
        service = sheets_service.get_service()
        spreadsheet_id = sheets_service._extract_spreadsheet_id(spreadsheet_id)

        # Get all sheets
        sheet_metadata = service.spreadsheets().get(
            spreadsheetId=spreadsheet_id
        ).execute()

        sheets = sheet_metadata.get('sheets', [])
        matches = []

        # Search each sheet
        for sheet in sheets:
            sheet_title = sheet['properties']['title']

            # Read all data from this sheet
            result = service.spreadsheets().values().get(
                spreadsheetId=spreadsheet_id,
                range=f"{sheet_title}!A:Z"
            ).execute()

            values = result.get('values', [])

            # Search rows
            for i, row in enumerate(values, 1):
                row_str = ' '.join([str(cell) for cell in row])
                if query.lower() in row_str.lower():
                    matches.append({
                        'sheet': sheet_title,
                        'row': i,
                        'data': row
                    })

        if not matches:
            return f"No matches found for '{query}'"

        # Format results
        result_lines = [f"Found {len(matches)} match(es) for '{query}':\n"]

        for match in matches[:10]:  # Limit to 10 results
            sheet = match['sheet']
            row_num = match['row']
            data = ', '.join([str(cell) for cell in match['data'] if cell])

            result_lines.append(f"Sheet: {sheet}, Row {row_num}: {data}")

        if len(matches) > 10:
            result_lines.append(f"\n... and {len(matches) - 10} more matches")

        return '\n'.join(result_lines)

    except HttpError as e:
        return f"Sheets API error: {e.reason if hasattr(e, 'reason') else str(e)}"
    except Exception as e:
        return f"Search failed: {str(e)}"


@function_tool()
def create_spreadsheet(title: str) -> str:
    """
    Create a new Google Spreadsheet.

    Args:
        title: Spreadsheet title

    Returns:
        Success message with spreadsheet ID and URL

    Voice command examples:
        "Create a new spreadsheet called Project Tracker"
        "Make a new sheet for my expenses"
    """
    try:
        service = sheets_service.get_service()

        spreadsheet = {
            'properties': {
                'title': title
            }
        }

        result = service.spreadsheets().create(
            body=spreadsheet,
            fields='spreadsheetId,spreadsheetUrl,properties/title'
        ).execute()

        spreadsheet_id = result.get('spreadsheetId')
        spreadsheet_url = result.get('spreadsheetUrl')
        created_title = result.get('properties', {}).get('title')

        return (
            f"Created spreadsheet '{created_title}'\n"
            f"ID: {spreadsheet_id}\n"
            f"URL: {spreadsheet_url}"
        )

    except HttpError as e:
        return f"Sheets API error: {e.reason if hasattr(e, 'reason') else str(e)}"
    except Exception as e:
        return f"Failed to create spreadsheet: {str(e)}"


@function_tool()
def get_sheet_summary(spreadsheet_id: str) -> str:
    """
    Get summary information about a spreadsheet.

    Args:
        spreadsheet_id: Spreadsheet ID or URL

    Returns:
        Sheet names, row counts, and column headers

    Voice command examples:
        "How many rows are in my sheet?"
        "What sheets are in my spreadsheet?"
        "Give me a summary of my tracker"
    """
    try:
        service = sheets_service.get_service()
        spreadsheet_id = sheets_service._extract_spreadsheet_id(spreadsheet_id)

        # Get spreadsheet metadata
        sheet_metadata = service.spreadsheets().get(
            spreadsheetId=spreadsheet_id
        ).execute()

        title = sheet_metadata.get('properties', {}).get('title', 'Unknown')
        sheets = sheet_metadata.get('sheets', [])

        summary_lines = [f"Spreadsheet: {title}\n"]

        for sheet in sheets:
            sheet_props = sheet['properties']
            sheet_title = sheet_props['title']
            sheet_id = sheet_props['sheetId']

            # Get grid properties
            grid = sheet_props.get('gridProperties', {})
            row_count = grid.get('rowCount', 0)
            col_count = grid.get('columnCount', 0)

            summary_lines.append(f"Sheet: {sheet_title}")
            summary_lines.append(f"  Rows: {row_count}, Columns: {col_count}")

            # Get first row (headers)
            try:
                result = service.spreadsheets().values().get(
                    spreadsheetId=spreadsheet_id,
                    range=f"{sheet_title}!1:1"
                ).execute()

                headers = result.get('values', [[]])[0]
                if headers:
                    headers_str = ', '.join([str(h) for h in headers[:10]])
                    summary_lines.append(f"  Headers: {headers_str}")

            except:
                pass  # Skip if can't read headers

            summary_lines.append("")

        return '\n'.join(summary_lines)

    except HttpError as e:
        return f"Sheets API error: {e.reason if hasattr(e, 'reason') else str(e)}"
    except Exception as e:
        return f"Failed to get summary: {str(e)}"


# Export all function tools for LiveKit agent registration
SHEETS_TOOLS = [
    read_sheet,
    write_to_sheet,
    append_row,
    search_sheet,
    create_spreadsheet,
    get_sheet_summary
]


def authenticate_sheets() -> str:
    """
    Re-authenticate with Sheets scope.
    Run this if you need to add Sheets scope to existing token.

    Returns:
        Success message or error details
    """
    try:
        # Force re-authentication by deleting token
        if TOKEN_FILE.exists():
            print(f"Existing token found at {TOKEN_FILE}")
            print("Will re-authenticate to add Sheets scope...")

        # Get credentials (will trigger OAuth flow)
        sheets_service._service = None
        service = sheets_service.get_service()

        # Test the connection
        result = service.spreadsheets().create(
            body={'properties': {'title': 'Test Sheet (Delete Me)'}},
            fields='spreadsheetId'
        ).execute()

        test_id = result.get('spreadsheetId')

        # Delete test sheet
        service.spreadsheets().batchUpdate(
            spreadsheetId=test_id,
            body={'requests': [{'deleteSheet': {'sheetId': 0}}]}
        ).execute()

        return (
            f"[OK] Sheets API authentication successful!\n"
            f"Token saved to {TOKEN_FILE}\n"
            f"Includes both Gmail and Sheets access."
        )

    except Exception as e:
        return f"Authentication failed: {str(e)}"


if __name__ == "__main__":
    # Manual authentication test
    print("Testing Google Sheets API connection...")
    print(authenticate_sheets())

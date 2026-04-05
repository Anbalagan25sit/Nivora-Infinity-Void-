"""
Notion Tool for Nivora Voice Agent
===================================
Provides Notion integration via Notion API for knowledge management.
All functions are registered as LiveKit function tools for voice commands.

Voice Commands Supported:
- "Save this to Notion"
- "Search Notion for my project notes"
- "Create a Notion page about X"
- "Add task to my Notion database"
- "Read my Notion page about Y"

Setup:
1. Create Notion integration at https://www.notion.so/my-integrations
2. Copy integration token to .env as NOTION_API_KEY
3. Share pages/databases with your integration
4. Optionally set NOTION_DEFAULT_DATABASE_ID for quick task adding
"""

import os
import re
from datetime import datetime
from typing import Optional, Dict, List, Any
from pathlib import Path

from notion_client import Client
from notion_client.errors import APIResponseError

# Try to import LiveKit function_tool - gracefully handle if not installed
try:
    from livekit.agents.llm import function_tool
    LIVEKIT_AVAILABLE = True
except ImportError:
    LIVEKIT_AVAILABLE = False
    # Dummy decorator for testing without LiveKit
    def function_tool(func):
        return func

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Notion API configuration
NOTION_API_KEY = os.getenv("NOTION_API_KEY")
NOTION_DEFAULT_DATABASE_ID = os.getenv("NOTION_DEFAULT_DATABASE_ID")
NOTION_NOTES_PAGE_ID = os.getenv("NOTION_NOTES_PAGE_ID")  # For agent output storage


class NotionService:
    """Notion API service wrapper."""

    def __init__(self):
        if not NOTION_API_KEY:
            raise ValueError(
                "NOTION_API_KEY not found in environment variables. "
                "Add it to .env file: NOTION_API_KEY=secret_xxxxx"
            )
        self.client = Client(auth=NOTION_API_KEY)
        self._nivora_notes_page_id = NOTION_NOTES_PAGE_ID

    def _extract_page_id(self, page_id_or_url: str) -> str:
        """Extract page ID from URL or return ID as-is."""
        # If it's a URL, extract the ID
        if "notion.so" in page_id_or_url or "notion.site" in page_id_or_url:
            # Extract 32-char hex ID from URL
            match = re.search(r'([a-f0-9]{32})', page_id_or_url.replace('-', ''))
            if match:
                page_id = match.group(1)
                # Format with hyphens: 8-4-4-4-12
                return f"{page_id[:8]}-{page_id[8:12]}-{page_id[12:16]}-{page_id[16:20]}-{page_id[20:]}"

        # Remove hyphens and reformat
        clean_id = page_id_or_url.replace('-', '')
        if len(clean_id) == 32:
            return f"{clean_id[:8]}-{clean_id[8:12]}-{clean_id[12:16]}-{clean_id[16:20]}-{clean_id[20:]}"

        return page_id_or_url

    def _blocks_to_text(self, blocks: List[Dict]) -> str:
        """Convert Notion blocks to readable text."""
        text_parts = []

        for block in blocks:
            block_type = block.get('type')

            if block_type == 'paragraph':
                text = self._extract_rich_text(block['paragraph'].get('rich_text', []))
                if text:
                    text_parts.append(text)

            elif block_type == 'heading_1':
                text = self._extract_rich_text(block['heading_1'].get('rich_text', []))
                if text:
                    text_parts.append(f"\n# {text}\n")

            elif block_type == 'heading_2':
                text = self._extract_rich_text(block['heading_2'].get('rich_text', []))
                if text:
                    text_parts.append(f"\n## {text}\n")

            elif block_type == 'heading_3':
                text = self._extract_rich_text(block['heading_3'].get('rich_text', []))
                if text:
                    text_parts.append(f"\n### {text}\n")

            elif block_type == 'bulleted_list_item':
                text = self._extract_rich_text(block['bulleted_list_item'].get('rich_text', []))
                if text:
                    text_parts.append(f"• {text}")

            elif block_type == 'numbered_list_item':
                text = self._extract_rich_text(block['numbered_list_item'].get('rich_text', []))
                if text:
                    text_parts.append(f"1. {text}")

            elif block_type == 'to_do':
                text = self._extract_rich_text(block['to_do'].get('rich_text', []))
                checked = block['to_do'].get('checked', False)
                checkbox = "[x]" if checked else "[ ]"
                if text:
                    text_parts.append(f"{checkbox} {text}")

            elif block_type == 'code':
                text = self._extract_rich_text(block['code'].get('rich_text', []))
                language = block['code'].get('language', 'plain text')
                if text:
                    text_parts.append(f"\n```{language}\n{text}\n```\n")

            elif block_type == 'quote':
                text = self._extract_rich_text(block['quote'].get('rich_text', []))
                if text:
                    text_parts.append(f"> {text}")

            elif block_type == 'divider':
                text_parts.append("\n---\n")

        return "\n".join(text_parts)

    def _extract_rich_text(self, rich_text_array: List[Dict]) -> str:
        """Extract plain text from Notion rich text array."""
        return "".join([rt.get('plain_text', '') for rt in rich_text_array])

    def _get_page_title(self, page: Dict) -> str:
        """Extract title from page properties."""
        properties = page.get('properties', {})

        # Try common title property names
        for key in ['Title', 'title', 'Name', 'name']:
            if key in properties:
                prop = properties[key]
                if prop['type'] == 'title':
                    return self._extract_rich_text(prop['title'])

        # Fallback: use first title property found
        for prop_name, prop in properties.items():
            if prop.get('type') == 'title':
                return self._extract_rich_text(prop['title'])

        return "Untitled"

    def _markdown_to_blocks(self, content: str) -> List[Dict]:
        """Convert markdown-like content to Notion blocks."""
        blocks = []
        lines = content.split('\n')

        for line in lines:
            line = line.strip()

            if not line:
                continue

            # Heading 1
            if line.startswith('# '):
                blocks.append({
                    "object": "block",
                    "type": "heading_1",
                    "heading_1": {
                        "rich_text": [{"type": "text", "text": {"content": line[2:]}}]
                    }
                })

            # Heading 2
            elif line.startswith('## '):
                blocks.append({
                    "object": "block",
                    "type": "heading_2",
                    "heading_2": {
                        "rich_text": [{"type": "text", "text": {"content": line[3:]}}]
                    }
                })

            # Heading 3
            elif line.startswith('### '):
                blocks.append({
                    "object": "block",
                    "type": "heading_3",
                    "heading_3": {
                        "rich_text": [{"type": "text", "text": {"content": line[4:]}}]
                    }
                })

            # Bullet list
            elif line.startswith('- ') or line.startswith('• '):
                blocks.append({
                    "object": "block",
                    "type": "bulleted_list_item",
                    "bulleted_list_item": {
                        "rich_text": [{"type": "text", "text": {"content": line[2:]}}]
                    }
                })

            # Numbered list
            elif re.match(r'^\d+\. ', line):
                content = re.sub(r'^\d+\. ', '', line)
                blocks.append({
                    "object": "block",
                    "type": "numbered_list_item",
                    "numbered_list_item": {
                        "rich_text": [{"type": "text", "text": {"content": content}}]
                    }
                })

            # To-do
            elif line.startswith('[ ] ') or line.startswith('[x] '):
                checked = line.startswith('[x]')
                content = line[4:]
                blocks.append({
                    "object": "block",
                    "type": "to_do",
                    "to_do": {
                        "rich_text": [{"type": "text", "text": {"content": content}}],
                        "checked": checked
                    }
                })

            # Divider
            elif line == '---':
                blocks.append({
                    "object": "block",
                    "type": "divider",
                    "divider": {}
                })

            # Regular paragraph
            else:
                blocks.append({
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [{"type": "text", "text": {"content": line}}]
                    }
                })

        return blocks


# Singleton service instance
notion_service = NotionService()


@function_tool()
def create_notion_page(
    title: str,
    content: str,
    parent_page_id: Optional[str] = None
) -> str:
    """
    Create a new Notion page with markdown content.

    Args:
        title: Page title
        content: Page content (supports markdown: # headers, - bullets, etc.)
        parent_page_id: Parent page ID or URL (optional, creates in workspace root if not provided)

    Returns:
        Success message with page URL

    Voice command examples:
        "Create a Notion page about project ideas"
        "Make a new Notion page called Meeting Notes"
    """
    try:
        # Prepare page properties
        properties = {
            "title": [
                {
                    "type": "text",
                    "text": {"content": title}
                }
            ]
        }

        # Convert content to blocks
        blocks = notion_service._markdown_to_blocks(content)

        # Prepare parent
        parent = {}
        if parent_page_id:
            parent_id = notion_service._extract_page_id(parent_page_id)
            parent = {"type": "page_id", "page_id": parent_id}
        else:
            # Create in workspace (requires workspace parent or will fail)
            # Notion requires a parent, so we'll try to use the integration's workspace
            parent = {"type": "workspace", "workspace": True}

        # Create page
        try:
            response = notion_service.client.pages.create(
                parent=parent,
                properties={"title": {"title": [{"text": {"content": title}}]}},
                children=blocks
            )
        except APIResponseError as e:
            if "workspace" in str(e):
                # If workspace parent fails, we need a page ID
                return (
                    f"Failed to create page. Please provide a parent_page_id. "
                    f"Share a Notion page with your integration and use its ID."
                )
            raise

        page_url = response['url']
        return f"Page '{title}' created successfully! URL: {page_url}"

    except APIResponseError as e:
        return f"Notion API error: {e.message if hasattr(e, 'message') else str(e)}"
    except Exception as e:
        return f"Failed to create page: {str(e)}"


@function_tool()
def search_notion(query: str) -> str:
    """
    Search all Notion pages and databases.

    Args:
        query: Search query text

    Returns:
        Formatted list of matching pages with titles and URLs

    Voice command examples:
        "Search Notion for my project notes"
        "Find my meeting notes in Notion"
        "Search Notion for todo list"
    """
    try:
        response = notion_service.client.search(
            query=query,
            filter={"property": "object", "value": "page"}
        )

        results = response.get('results', [])

        if not results:
            return f"No pages found for query: '{query}'"

        formatted_results = [f"Search results for '{query}':\n"]

        for i, page in enumerate(results[:10], 1):  # Limit to 10 results
            title = notion_service._get_page_title(page)
            url = page['url']

            # Get page type
            parent = page.get('parent', {})
            parent_type = parent.get('type', 'page')

            formatted_results.append(f"{i}. {title}")
            formatted_results.append(f"   URL: {url}")
            formatted_results.append(f"   Type: {parent_type}")

        return "\n".join(formatted_results)

    except APIResponseError as e:
        return f"Notion API error: {e.message if hasattr(e, 'message') else str(e)}"
    except Exception as e:
        return f"Search failed: {str(e)}"


@function_tool()
def read_notion_page(page_id_or_url: str) -> str:
    """
    Read full content of a Notion page.

    Args:
        page_id_or_url: Notion page ID or full URL

    Returns:
        Formatted page content with title and text

    Voice command examples:
        "Read my Notion page about project plan"
        "What's in my Notion meeting notes?"
    """
    try:
        page_id = notion_service._extract_page_id(page_id_or_url)

        # Get page metadata
        page = notion_service.client.pages.retrieve(page_id=page_id)
        title = notion_service._get_page_title(page)

        # Get page content (blocks)
        blocks_response = notion_service.client.blocks.children.list(block_id=page_id)
        blocks = blocks_response.get('results', [])

        # Convert blocks to text
        content = notion_service._blocks_to_text(blocks)

        if not content:
            content = "(Page is empty)"

        return f"Page: {title}\n\n{content}"

    except APIResponseError as e:
        return f"Notion API error: {e.message if hasattr(e, 'message') else str(e)}"
    except Exception as e:
        return f"Failed to read page: {str(e)}"


@function_tool()
def add_to_notion_database(
    database_id: str,
    properties: Dict[str, Any]
) -> str:
    """
    Add a new row/entry to a Notion database.

    Args:
        database_id: Database ID or URL
        properties: Dictionary of properties to set
                   Format: {"Property Name": value}
                   Supported values:
                   - str for text/title/select
                   - int/float for number
                   - bool for checkbox
                   - "YYYY-MM-DD" for date

    Returns:
        Success message with entry URL

    Voice command examples:
        "Add task 'Finish report' to my Notion database"
        "Add a new project entry to Notion"

    Example properties:
        {"Name": "Task title", "Status": "In Progress", "Priority": "High"}
    """
    try:
        database_id = notion_service._extract_page_id(database_id)

        # Get database schema to understand property types
        database = notion_service.client.databases.retrieve(database_id=database_id)
        db_properties = database.get('properties', {})

        # Convert simple dict to Notion property format
        notion_properties = {}

        for prop_name, value in properties.items():
            if prop_name not in db_properties:
                continue

            prop_type = db_properties[prop_name]['type']

            if prop_type == 'title':
                notion_properties[prop_name] = {
                    "title": [{"text": {"content": str(value)}}]
                }
            elif prop_type == 'rich_text':
                notion_properties[prop_name] = {
                    "rich_text": [{"text": {"content": str(value)}}]
                }
            elif prop_type == 'number':
                notion_properties[prop_name] = {
                    "number": float(value) if value else None
                }
            elif prop_type == 'select':
                notion_properties[prop_name] = {
                    "select": {"name": str(value)}
                }
            elif prop_type == 'checkbox':
                notion_properties[prop_name] = {
                    "checkbox": bool(value)
                }
            elif prop_type == 'date':
                notion_properties[prop_name] = {
                    "date": {"start": str(value)}
                }

        # Create database entry
        response = notion_service.client.pages.create(
            parent={"database_id": database_id},
            properties=notion_properties
        )

        page_url = response['url']
        return f"Entry added to database successfully! URL: {page_url}"

    except APIResponseError as e:
        return f"Notion API error: {e.message if hasattr(e, 'message') else str(e)}"
    except Exception as e:
        return f"Failed to add to database: {str(e)}"


@function_tool()
def update_notion_page(
    page_id: str,
    content: str
) -> str:
    """
    Append new content to an existing Notion page.

    Args:
        page_id: Page ID or URL to update
        content: New content to append (supports markdown)

    Returns:
        Success message

    Voice command examples:
        "Add this to my Notion journal"
        "Update my Notion notes with this info"
    """
    try:
        page_id = notion_service._extract_page_id(page_id)

        # Convert content to blocks
        blocks = notion_service._markdown_to_blocks(content)

        # Append blocks to page
        notion_service.client.blocks.children.append(
            block_id=page_id,
            children=blocks
        )

        # Get page info for confirmation
        page = notion_service.client.pages.retrieve(page_id=page_id)
        title = notion_service._get_page_title(page)

        return f"Content added to page '{title}' successfully!"

    except APIResponseError as e:
        return f"Notion API error: {e.message if hasattr(e, 'message') else str(e)}"
    except Exception as e:
        return f"Failed to update page: {str(e)}"


@function_tool()
def save_agent_output(
    title: str,
    content: str
) -> str:
    """
    Save any Nivora output to a dedicated "Nivora Notes" page.
    Auto-creates the page if it doesn't exist.
    Adds timestamp automatically.

    Args:
        title: Title/heading for this entry
        content: Content to save

    Returns:
        Success message

    Voice command examples:
        "Save this to Notion"
        "Remember this in Notion"
        "Log this to my Nivora notes"
    """
    try:
        # Try to get or create Nivora Notes page
        if not notion_service._nivora_notes_page_id:
            # Search for existing "Nivora Notes" page
            search_result = notion_service.client.search(
                query="Nivora Notes",
                filter={"property": "object", "value": "page"}
            )

            results = search_result.get('results', [])
            for page in results:
                page_title = notion_service._get_page_title(page)
                if page_title == "Nivora Notes":
                    notion_service._nivora_notes_page_id = page['id']
                    break

            # If still not found, we need to create it
            if not notion_service._nivora_notes_page_id:
                return (
                    "Nivora Notes page not found. Please:\n"
                    "1. Create a page called 'Nivora Notes' in Notion\n"
                    "2. Share it with your integration\n"
                    "3. Add the page ID to .env as NOTION_NOTES_PAGE_ID"
                )

        # Create entry with timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        entry_content = f"## {title}\n*{timestamp}*\n\n{content}\n\n---"

        # Append to Nivora Notes page
        blocks = notion_service._markdown_to_blocks(entry_content)

        notion_service.client.blocks.children.append(
            block_id=notion_service._nivora_notes_page_id,
            children=blocks
        )

        return f"Saved '{title}' to Nivora Notes at {timestamp}"

    except APIResponseError as e:
        return f"Notion API error: {e.message if hasattr(e, 'message') else str(e)}"
    except Exception as e:
        return f"Failed to save output: {str(e)}"


# Export all function tools for LiveKit agent registration
NOTION_TOOLS = [
    create_notion_page,
    search_notion,
    read_notion_page,
    add_to_notion_database,
    update_notion_page,
    save_agent_output
]


if __name__ == "__main__":
    # Test authentication
    print("Testing Notion API connection...")
    try:
        if not NOTION_API_KEY:
            print("[X] NOTION_API_KEY not found in .env")
        else:
            # Test search to verify connection
            result = notion_service.client.search(query="", page_size=1)
            print(f"[OK] Connected to Notion API successfully!")
            print(f"     Integration has access to {len(result.get('results', []))} pages/databases")
    except Exception as e:
        print(f"[X] Connection failed: {e}")

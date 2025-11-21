"""
Create Page tool for Notion MCP server.

Creates a new empty page in a Notion workspace under a specified parent.
"""
from typing import Dict, Any, Optional
from .client import NotionAPIClient
import logging

logger = logging.getLogger(__name__)


async def create_page(
    parent_id: str,
    title: str,
    cover: Optional[str] = None,
    icon: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Create a new empty page in Notion under a specified parent page or database.

    Prerequisites:
    - Parent page/database must exist and be accessible in your workspace
    - Use search or list actions first to obtain valid parent IDs
    - Root-level pages cannot be created - must specify a parent

    Args:
        parent_id: UUID of the parent page or database
                   Format: 8-4-4-4-12 hex characters
                   Example: "59833787-2cf9-4fdf-8782-e53db20768a5"
        title: Title of the new page
               Example: "My new report" or "Project Plan Q3"
        cover: Optional URL of cover image (must be publicly accessible)
               Example: "https://www.example.com/images/cover.png"
        icon: Optional emoji to use as page icon (single emoji character)
              Example: "📄" or "🤔"

    Returns:
        Page object from Notion API containing id, properties, and metadata

    Example:
        page = await create_page(
            parent_id="59833787-2cf9-4fdf-8782-e53db20768a5",
            title="Project Plan Q3",
            icon="📋"
        )
    """
    try:
        client = NotionAPIClient()

        # Build request body in Notion API format
        page_data = {
            "parent": {"page_id": parent_id},
            "properties": {
                "title": {
                    "title": [{"text": {"content": title}}]
                }
            }
        }

        # Add optional cover (convert string URL to Notion format)
        if cover:
            page_data["cover"] = {
                "type": "external",
                "external": {"url": cover}
            }

        # Add optional icon (convert emoji string to Notion format)
        if icon:
            page_data["icon"] = {
                "type": "emoji",
                "emoji": icon
            }

        response = await client.post("/pages", page_data)
        return response

    except Exception as e:
        logger.error(f"Failed to create page: {e}")
        return {
            "error": f"Failed to create page: {str(e)}"
        }

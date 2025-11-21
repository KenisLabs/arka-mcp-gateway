"""
Update Page tool for Notion MCP server.

Updates page properties, icon, cover, or archive status.
"""
from typing import Dict, Any, Optional
from .client import NotionAPIClient
import logging

logger = logging.getLogger(__name__)


async def update_page(
    page_id: str,
    properties: Optional[Dict[str, Any]] = None,
    icon: Optional[Dict[str, Any]] = None,
    cover: Optional[Dict[str, Any]] = None,
    archived: Optional[bool] = None,
) -> Dict[str, Any]:
    """
    Update a Notion page's properties, icon, cover, or archive status.

    At least one update parameter must be provided.

    Common errors:
    - "Invalid property identifier": Property name doesn't exist - use exact names
    - Must provide at least one field to update

    Args:
        page_id: UUID of the page to update
                 Example: "59833787-2cf9-4fdf-8782-e53db20768a5"
        properties: Optional dict of properties to update
                    Must match exact property names from the page
                    Example: {"Status": {"select": {"name": "In Progress"}}}
        icon: Optional icon object in Notion API format
              Example: {"type": "emoji", "emoji": "📄"}
        cover: Optional cover object in Notion API format
               Example: {"type": "external", "external": {"url": "https://..."}}
        archived: Optional archive status (True to archive, False to unarchive)

    Returns:
        Updated page object from Notion API

    Example:
        page = await update_page(
            page_id="59833787-2cf9-4fdf-8782-e53db20768a5",
            properties={
                "Status": {"select": {"name": "Done"}}
            },
            icon={"type": "emoji", "emoji": "✅"}
        )
    """
    try:
        client = NotionAPIClient()

        # Build update data
        page_data = {}

        if properties is not None:
            page_data["properties"] = properties
        if icon is not None:
            page_data["icon"] = icon
        if cover is not None:
            page_data["cover"] = cover
        if archived is not None:
            page_data["archived"] = archived

        # Validate that at least one field is provided
        if not page_data:
            return {
                "error": "At least one update parameter must be provided",
                "page_id": page_id
            }

        response = await client.patch(f"/pages/{page_id}", page_data)
        return response

    except Exception as e:
        logger.error(f"Failed to update page {page_id}: {e}")
        return {
            "error": f"Failed to update page: {str(e)}",
            "page_id": page_id
        }

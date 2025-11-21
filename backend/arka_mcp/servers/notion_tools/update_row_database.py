"""
Update Row Database tool for Notion MCP server.

Updates property values of an existing database row (page).
"""
from typing import Dict, Any, Optional
from .client import NotionAPIClient
import logging

logger = logging.getLogger(__name__)


async def update_row_database(
    page_id: str,
    properties: Optional[Dict[str, Any]] = None,
    icon: Optional[Dict[str, Any]] = None,
    cover: Optional[Dict[str, Any]] = None,
    archived: Optional[bool] = None,
) -> Dict[str, Any]:
    """
    Update property values of an existing database row (page).

    Modifies properties of a database entry. Can also update icon, cover, or
    archive status. Only specified properties are updated; others remain unchanged.

    Args:
        page_id: UUID of the database row (page) to update
                 Example: "59833787-2cf9-4fdf-8782-e53db20768a5"
        properties: Optional property values to update in Notion API format
                    Example: {
                        "Status": {"select": {"name": "Done"}},
                        "Priority": {"select": {"name": "Low"}}
                    }
        icon: Optional icon to set
              Example: {"type": "emoji", "emoji": "✅"}
        cover: Optional cover image to set
               Example: {"type": "external", "external": {"url": "https://..."}}
        archived: Optional archive status (True to archive, False to restore)

    Returns:
        Updated database page object

    Example:
        # Update status
        row = await update_row_database(
            page_id="59833787-2cf9-4fdf-8782-e53db20768a5",
            properties={
                "Status": {"select": {"name": "Done"}}
            }
        )

        # Update multiple properties
        row = await update_row_database(
            page_id="59833787-2cf9-4fdf-8782-e53db20768a5",
            properties={
                "Status": {"select": {"name": "In Review"}},
                "Priority": {"select": {"name": "High"}},
                "Due Date": {"date": {"start": "2024-12-31"}},
                "Progress": {"number": 75}
            }
        )

        # Update with icon and archive
        row = await update_row_database(
            page_id="59833787-2cf9-4fdf-8782-e53db20768a5",
            properties={
                "Status": {"select": {"name": "Completed"}}
            },
            icon={"type": "emoji", "emoji": "✅"},
            archived=False
        )
    """
    try:
        client = NotionAPIClient()

        # Build update data
        update_data = {}

        if properties is not None:
            update_data["properties"] = properties

        if icon is not None:
            update_data["icon"] = icon

        if cover is not None:
            update_data["cover"] = cover

        if archived is not None:
            update_data["archived"] = archived

        # Validate that at least one field is provided
        if not update_data:
            return {
                "error": "At least one update parameter must be provided",
                "page_id": page_id
            }

        # Update the database row
        response = await client.patch(f"/pages/{page_id}", update_data)

        return response

    except Exception as e:
        logger.error(f"Failed to update row {page_id}: {e}")
        return {
            "error": f"Failed to update row: {str(e)}",
            "page_id": page_id
        }

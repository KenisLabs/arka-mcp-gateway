"""
Insert Row Database tool for Notion MCP server.

Inserts a new row (page) into a database with property values.
"""
from typing import Dict, Any, Optional
from .client import NotionAPIClient
import logging

logger = logging.getLogger(__name__)


async def insert_row_database(
    database_id: str,
    properties: Dict[str, Any],
    icon: Optional[Dict[str, Any]] = None,
    cover: Optional[Dict[str, Any]] = None,
    children: Optional[list] = None,
) -> Dict[str, Any]:
    """
    Insert a new row (page) into a Notion database.

    Creates a new database entry with specified property values. Properties must
    match the database schema and use Notion's property value format.

    Args:
        database_id: UUID of the database
                     Example: "668d797c-76fa-4934-9b05-ad288df2d136"
        properties: Property values in Notion API format
                    Must match database property names and types
                    Example: {
                        "Name": {"title": [{"text": {"content": "Task 1"}}]},
                        "Status": {"select": {"name": "In Progress"}}
                    }
        icon: Optional icon for the row
              Example: {"type": "emoji", "emoji": "📝"}
        cover: Optional cover image for the row
               Example: {"type": "external", "external": {"url": "https://..."}}
        children: Optional content blocks to add to the page
                  Example: [{"object": "block", "type": "paragraph", ...}]

    Returns:
        Created database page object

    Example:
        # Insert a simple row
        row = await insert_row_database(
            database_id="668d797c-76fa-4934-9b05-ad288df2d136",
            properties={
                "Name": {
                    "title": [{"text": {"content": "New Task"}}]
                },
                "Status": {
                    "select": {"name": "Not Started"}
                }
            }
        )

        # Insert row with multiple properties
        row = await insert_row_database(
            database_id="668d797c-76fa-4934-9b05-ad288df2d136",
            properties={
                "Name": {"title": [{"text": {"content": "Project Alpha"}}]},
                "Status": {"select": {"name": "In Progress"}},
                "Priority": {"select": {"name": "High"}},
                "Due Date": {"date": {"start": "2024-12-31"}},
                "Assignee": {"people": [{"id": "user-uuid"}]}
            },
            icon={"type": "emoji", "emoji": "🚀"}
        )

        # Insert row with content
        row = await insert_row_database(
            database_id="668d797c-76fa-4934-9b05-ad288df2d136",
            properties={
                "Name": {"title": [{"text": {"content": "Meeting Notes"}}]}
            },
            children=[
                {
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [{"text": {"content": "Discussion points..."}}]
                    }
                }
            ]
        )
    """
    try:
        client = NotionAPIClient()

        # Build page data
        page_data = {
            "parent": {"database_id": database_id},
            "properties": properties
        }

        if icon:
            page_data["icon"] = icon

        if cover:
            page_data["cover"] = cover

        if children:
            page_data["children"] = children

        # Create the database row (page)
        response = await client.post("/pages", page_data)

        return response

    except Exception as e:
        logger.error(f"Failed to insert row into database {database_id}: {e}")
        return {
            "error": f"Failed to insert row: {str(e)}",
            "database_id": database_id
        }

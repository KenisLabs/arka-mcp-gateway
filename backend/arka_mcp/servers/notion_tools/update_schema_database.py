"""
Update Schema Database tool for Notion MCP server.

Updates database schema by adding, updating, or removing properties.
"""
from typing import Dict, Any, Optional
from .client import NotionAPIClient
import logging

logger = logging.getLogger(__name__)


async def update_schema_database(
    database_id: str,
    properties: Optional[Dict[str, Any]] = None,
    title: Optional[str] = None,
    description: Optional[str] = None,
    icon: Optional[Dict[str, Any]] = None,
    cover: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Update database schema by modifying properties, title, description, or appearance.

    Can add new properties, update existing ones, or remove properties. Properties
    use Notion's property schema format. To remove a property, set its value to null.

    Args:
        database_id: UUID of the database to update
                     Example: "668d797c-76fa-4934-9b05-ad288df2d136"
        properties: Optional property schema updates
                    To add: Include new property with type config
                    To update: Include existing property with new config
                    To remove: Set property to null
                    Example: {
                        "New Property": {"select": {"options": [{"name": "Option 1"}]}},
                        "Old Property": None
                    }
        title: Optional new title for the database
               Example: "Updated Project Tracker"
        description: Optional new description
                     Example: "Track all active projects"
        icon: Optional new icon
              Example: {"type": "emoji", "emoji": "📊"}
        cover: Optional new cover image
               Example: {"type": "external", "external": {"url": "https://..."}}

    Returns:
        Updated database object with new schema

    Example:
        # Add a new property
        db = await update_schema_database(
            database_id="668d797c-76fa-4934-9b05-ad288df2d136",
            properties={
                "Priority": {
                    "select": {
                        "options": [
                            {"name": "High", "color": "red"},
                            {"name": "Medium", "color": "yellow"},
                            {"name": "Low", "color": "green"}
                        ]
                    }
                }
            }
        )

        # Update database title and description
        db = await update_schema_database(
            database_id="668d797c-76fa-4934-9b05-ad288df2d136",
            title="Q4 Project Tracker",
            description="Track all Q4 2024 projects and their status"
        )

        # Remove a property
        db = await update_schema_database(
            database_id="668d797c-76fa-4934-9b05-ad288df2d136",
            properties={
                "Deprecated Field": None
            }
        )

        # Add multiple properties
        db = await update_schema_database(
            database_id="668d797c-76fa-4934-9b05-ad288df2d136",
            properties={
                "Due Date": {"date": {}},
                "Owner": {"people": {}},
                "Tags": {
                    "multi_select": {
                        "options": [
                            {"name": "Backend", "color": "blue"},
                            {"name": "Frontend", "color": "green"}
                        ]
                    }
                }
            }
        )
    """
    try:
        client = NotionAPIClient()

        # Build update data
        update_data = {}

        if properties is not None:
            update_data["properties"] = properties

        if title is not None:
            update_data["title"] = [{"text": {"content": title}}]

        if description is not None:
            update_data["description"] = [{"text": {"content": description}}]

        if icon is not None:
            update_data["icon"] = icon

        if cover is not None:
            update_data["cover"] = cover

        # Validate that at least one field is provided
        if not update_data:
            return {
                "error": "At least one update parameter must be provided",
                "database_id": database_id
            }

        # Update the database schema
        response = await client.patch(f"/databases/{database_id}", update_data)

        return response

    except Exception as e:
        logger.error(f"Failed to update database schema {database_id}: {e}")
        return {
            "error": f"Failed to update database schema: {str(e)}",
            "database_id": database_id
        }

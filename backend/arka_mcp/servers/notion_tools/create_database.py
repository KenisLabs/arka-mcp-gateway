"""
Create Database tool for Notion MCP server.

Creates a new database in Notion under a parent page or workspace.
"""
from typing import Dict, Any, Optional, List
from .client import NotionAPIClient
import logging

logger = logging.getLogger(__name__)


async def create_database(
    parent: Dict[str, Any],
    title: List[Dict[str, Any]],
    properties: Dict[str, Any],
    icon: Optional[Dict[str, Any]] = None,
    cover: Optional[Dict[str, Any]] = None,
    description: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    """
    Create a new database in Notion as a subpage under a parent page or workspace.

    This function creates a new database with an initial data source, title,
    and property schema. The parent must be either a Notion page (`page_id`)
    or the workspace. If the parent page does not exist or the integration
    lacks access, the API will return an error.

    Args:
        parent: Parent location (page_id or workspace)
        title: Database title as rich text array
        properties: Property schema for database
        icon: Optional icon for database
        cover: Optional cover image
        description: Optional description as rich text array

    Returns:
        Created database object

    Key points:
    - `parent`: Specifies where the database is created. Must include the type
      (`page_id` or `workspace`) and appropriate identifier.
    - `title`: The display title of the new database.
    - `properties`: Defines the initial schema of the database's data source,
      including property types such as `title`, `number`, `select`, `multi_select`,
      `relation`, `rollup`, etc. Some property types like `status` are currently
      not supported at creation.
    - Optional `icon` and `cover` can customize the database appearance.
    - Optional `description` allows adding rich-text metadata for the database.
    - Integration must have insert content capability; otherwise, a 403 error is returned.
    - The created database includes its first table view and initial data source.

    Example:
        database = await create_database(
            parent={"page_id": "abc-123"},
            title=[{"text": {"content": "My Database"}}],
            properties={
                "Name": {"title": {}},
                "Status": {"select": {}}
            }
        )
    """
    try:
        client = NotionAPIClient()

        # Build request body
        database_data = {
            "parent": parent,
            "title": title,
            "properties": properties
        }

        if icon:
            database_data["icon"] = icon
        if cover:
            database_data["cover"] = cover
        if description:
            database_data["description"] = description

        response = await client.post("/databases", database_data)
        return response

    except Exception as e:
        logger.error(f"Failed to create database: {e}")
        return {
            "error": f"Failed to create database: {str(e)}"
        }

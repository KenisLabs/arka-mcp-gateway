"""
Create Database tool for Notion MCP server.

Creates a new database in Notion under a parent page with a defined properties schema.
"""
from typing import Dict, Any, Optional, List
from .client import NotionAPIClient
import logging

logger = logging.getLogger(__name__)


async def create_database(
    parent_id: str,
    title: str,
    properties: List[Dict[str, Any]],
    icon: Optional[Dict[str, Any]] = None,
    cover: Optional[Dict[str, Any]] = None,
    description: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Create a new database in Notion as a subpage under a specified parent page.

    Accepts simplified parameters and converts them to the Notion API format internally.

    Prerequisites:
    - The parent page must be shared with your integration
    - Parent ID must be a valid UUID format (with or without hyphens)
    - If conflict errors (409) occur, retry the request

    Args:
        parent_id: UUID of the parent page
                   Example: "a1b2c3d4-e5f6-7890-1234-567890abcdef"
        title: Database title as plain text
               Example: "Project Roadmap"
        properties: Array of property definitions, each with 'name' and 'type' keys
                   Example: [{"name": "Task", "type": "title"}, {"name": "Status", "type": "select"}]
        icon: Optional icon object in Notion API format
        cover: Optional cover object in Notion API format
        description: Optional description as plain text

    Returns:
        Database object from Notion API containing id, properties, and metadata

    Example:
        database = await create_database(
            parent_id="a1b2c3d4-e5f6-7890-1234-567890abcdef",
            title="Project Roadmap",
            properties=[
                {"name": "Feature", "type": "title"},
                {"name": "Status", "type": "select"},
                {"name": "Assignee", "type": "people"}
            ]
        )
    """
    try:
        client = NotionAPIClient()

        # Build properties dict from array
        properties_dict = {}
        for prop in properties:
            name = prop.get('name')
            prop_type = prop.get('type')
            if name and prop_type:
                # Configure property based on type
                config = {}
                if prop_type == 'relation' and 'database_id' in prop:
                    config = {"database_id": prop['database_id']}
                elif prop_type == 'rollup':
                    config = {
                        "relation_property": prop.get('relation_property', ''),
                        "rollup_property": prop.get('rollup_property', ''),
                        "function": prop.get('function', 'count')
                    }
                elif prop_type == 'formula' and 'expression' in prop:
                    config = {"expression": prop['expression']}

                properties_dict[name] = {prop_type: config}

        # Build request body in Notion API format
        database_data = {
            "parent": {"page_id": parent_id},
            "title": [{"text": {"content": title}}],
            "properties": properties_dict
        }

        if icon:
            database_data["icon"] = icon
        if cover:
            database_data["cover"] = cover
        if description:
            database_data["description"] = [{"text": {"content": description}}]

        response = await client.post("/databases", database_data)
        return response

    except Exception as e:
        logger.error(f"Failed to create database: {e}")
        return {
            "error": f"Failed to create database: {str(e)}"
        }

"""
Fetch Database tool for Notion MCP server.

Retrieves database metadata and properties schema.
"""
from typing import Dict, Any
from .client import NotionAPIClient
import logging

logger = logging.getLogger(__name__)


async def fetch_database(
    database_id: str,
) -> Dict[str, Any]:
    """
    Retrieve database metadata and properties schema.

    Returns complete database object including title, description, properties schema,
    and configuration. Use this to understand database structure before querying or
    inserting rows.

    Args:
        database_id: UUID of the database
                     Example: "668d797c-76fa-4934-9b05-ad288df2d136"

    Returns:
        Database object with metadata and properties schema

    Example:
        # Get database metadata
        db = await fetch_database(
            database_id="668d797c-76fa-4934-9b05-ad288df2d136"
        )

        # Access properties schema
        properties = db.get("properties", {})
        for name, config in properties.items():
            print(f"Property: {name}, Type: {config['type']}")
    """
    try:
        client = NotionAPIClient()

        # Fetch database metadata
        response = await client.get(f"/databases/{database_id}")

        return response

    except Exception as e:
        logger.error(f"Failed to fetch database {database_id}: {e}")
        return {
            "error": f"Failed to fetch database: {str(e)}",
            "database_id": database_id
        }

"""
Retrieve Database Property tool for Notion MCP server.

Retrieves a specific property from a database's schema.
"""
from typing import Dict, Any
from .client import NotionAPIClient
import logging

logger = logging.getLogger(__name__)


async def retrieve_database_property(
    database_id: str,
    property_id: str,
) -> Dict[str, Any]:
    """
    Retrieve a specific property from a database's schema.

    Returns detailed information about a single database property including its
    type, configuration, and options. Useful for understanding property structure
    before inserting or updating rows.

    Args:
        database_id: UUID of the database
                     Example: "668d797c-76fa-4934-9b05-ad288df2d136"
        property_id: ID of the property to retrieve
                     Can be property name or encoded ID
                     Example: "Status" or "%3E%5DtK"

    Returns:
        Property schema object with type and configuration

    Example:
        # Retrieve a select property
        prop = await retrieve_database_property(
            database_id="668d797c-76fa-4934-9b05-ad288df2d136",
            property_id="Status"
        )

        # Access property configuration
        prop_type = prop.get("type")  # e.g., "select"
        if prop_type == "select":
            options = prop.get("select", {}).get("options", [])
            for option in options:
                print(f"Option: {option['name']}, Color: {option['color']}")

        # Retrieve a relation property
        prop = await retrieve_database_property(
            database_id="668d797c-76fa-4934-9b05-ad288df2d136",
            property_id="Related Tasks"
        )

        # Check relation config
        if prop.get("type") == "relation":
            related_db = prop.get("relation", {}).get("database_id")
    """
    try:
        client = NotionAPIClient()

        # Retrieve the property
        endpoint = f"/databases/{database_id}/properties/{property_id}"
        response = await client.get(endpoint)

        return response

    except Exception as e:
        logger.error(f"Failed to retrieve property {property_id} from database {database_id}: {e}")
        return {
            "error": f"Failed to retrieve database property: {str(e)}",
            "database_id": database_id,
            "property_id": property_id
        }

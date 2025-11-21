"""
Fetch Row tool for Notion MCP server.

Retrieves a specific database row (page) with all property values.
"""
from typing import Dict, Any
from .client import NotionAPIClient
import logging

logger = logging.getLogger(__name__)


async def fetch_row(
    page_id: str,
) -> Dict[str, Any]:
    """
    Retrieve a specific database row (page) with all property values.

    Returns the complete page object including all properties in their full format.
    Use this to get detailed information about a specific database entry.

    Args:
        page_id: UUID of the database row (page)
                 Example: "59833787-2cf9-4fdf-8782-e53db20768a5"

    Returns:
        Page object with all properties and metadata

    Example:
        # Fetch a database row
        row = await fetch_row(
            page_id="59833787-2cf9-4fdf-8782-e53db20768a5"
        )

        # Access property values
        properties = row.get("properties", {})

        # Extract title property
        title_prop = properties.get("Name", {}).get("title", [])
        if title_prop:
            title = title_prop[0].get("text", {}).get("content", "")

        # Extract select property
        status = properties.get("Status", {}).get("select", {}).get("name", "")

        # Extract date property
        due_date = properties.get("Due Date", {}).get("date", {}).get("start", "")
    """
    try:
        client = NotionAPIClient()

        # Fetch the page (database row)
        response = await client.get(f"/pages/{page_id}")

        return response

    except Exception as e:
        logger.error(f"Failed to fetch row {page_id}: {e}")
        return {
            "error": f"Failed to fetch row: {str(e)}",
            "page_id": page_id
        }

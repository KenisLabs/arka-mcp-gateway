"""
Get Page Property tool for Notion MCP server.

Retrieves a specific property from a Notion page with pagination support.
"""
from typing import Dict, Any, Optional
from .client import NotionAPIClient
import logging

logger = logging.getLogger(__name__)


async def get_page_property(
    page_id: str,
    property_id: str,
    page_size: Optional[int] = None,
    start_cursor: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Get a specific property from a Notion page.

    Handles pagination for properties that return multiple items (like relations or rollups).
    Use this when you need detailed property data or need to paginate through property values.

    Args:
        page_id: UUID of the page
                 Example: "59833787-2cf9-4fdf-8782-e53db20768a5"
        property_id: ID of the property to retrieve
                     Can be found in the page's properties object
                     Example: "title" or "%3E%5DtK"
        page_size: Optional number of items to return per page
                   Used for properties with multiple values
                   Example: 25
        start_cursor: Optional cursor for pagination
                      Use next_cursor from previous response
                      Example: "a1b2c3d4"

    Returns:
        Property value object with potential pagination

    Example:
        # Get a simple property
        prop = await get_page_property(
            page_id="59833787-2cf9-4fdf-8782-e53db20768a5",
            property_id="title"
        )

        # Get paginated property
        prop = await get_page_property(
            page_id="59833787-2cf9-4fdf-8782-e53db20768a5",
            property_id="%3E%5DtK",
            page_size=25,
            start_cursor="cursor_from_previous_response"
        )
    """
    try:
        client = NotionAPIClient()

        # Build query params
        params = {}
        if page_size:
            params["page_size"] = page_size
        if start_cursor:
            params["start_cursor"] = start_cursor

        # Get property value
        endpoint = f"/pages/{page_id}/properties/{property_id}"
        response = await client.get(endpoint, params if params else None)

        return response

    except Exception as e:
        logger.error(f"Failed to get property {property_id} from page {page_id}: {e}")
        return {
            "error": f"Failed to get page property: {str(e)}",
            "page_id": page_id,
            "property_id": property_id
        }

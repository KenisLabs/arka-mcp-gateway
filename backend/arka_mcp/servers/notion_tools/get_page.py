"""
Get Page tool for Notion MCP server.

Retrieves a Notion page by ID, including properties and content.
"""
from typing import Dict, Any, Optional, List
from .client import NotionAPIClient
import logging

logger = logging.getLogger(__name__)


async def get_page(
    page_id: str,
    filter_properties: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Retrieve a page from Notion.

    Args:
        page_id: Notion page ID (with or without hyphens)
        filter_properties: Optional list of property names to include

    Returns:
        Page object with properties and metadata

    Example:
        page = await get_page("abc-123")
        page = await get_page("abc123", ["Name", "Status"])
    """
    try:
        client = NotionAPIClient()

        # Build endpoint with query params
        endpoint = f"/pages/{page_id}"
        params = {}
        if filter_properties:
            params["filter_properties"] = ",".join(filter_properties)

        response = await client.get(endpoint, params if params else None)
        return response

    except Exception as e:
        logger.error(f"Failed to get page {page_id}: {e}")
        return {
            "error": f"Failed to retrieve page: {str(e)}",
            "page_id": page_id
        }

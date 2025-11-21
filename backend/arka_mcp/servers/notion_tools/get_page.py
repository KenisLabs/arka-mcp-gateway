"""
Get Page tool for Notion MCP server.

Retrieves metadata for a Notion page using its UUID.
"""
from typing import Dict, Any
from .client import NotionAPIClient
import logging

logger = logging.getLogger(__name__)


async def get_page(page_id: str) -> Dict[str, Any]:
    """
    Retrieve metadata for a Notion page.

    Fetches metadata for a Notion page using its UUID. Returns page properties,
    parent info, timestamps, and other metadata but not child content.

    Prerequisites:
    1) Page must be shared with your integration
    2) Use valid page_id from API responses (not URLs)

    For child blocks, use fetch_block_contents instead.
    Common 404 errors mean the page isn't accessible to your integration.

    Args:
        page_id: The unique UUID identifier for the Notion page to be retrieved.
                 Must be a valid 32-character UUID (with or without hyphens).

    Returns:
        Page object with metadata, properties, and timestamps

    Example:
        page = await get_page("c02fc1d3-db8b-45c5-a222-27595b15aea7")
    """
    try:
        client = NotionAPIClient()

        # Use pages endpoint to retrieve page metadata
        endpoint = f"/pages/{page_id}"
        response = await client.get(endpoint)
        return response

    except Exception as e:
        logger.error(f"Failed to get page {page_id}: {e}")
        return {
            "error": f"Failed to retrieve page: {str(e)}",
            "page_id": page_id
        }

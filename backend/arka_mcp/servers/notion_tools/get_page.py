"""
Fetch Block Metadata tool for Notion MCP server.

Fetches metadata for a Notion block (including pages, which are special blocks)
using its UUID. Returns block type, properties, and basic info but not child content.
"""
from typing import Dict, Any
from .client import NotionAPIClient
import logging

logger = logging.getLogger(__name__)


async def get_page(block_id: str) -> Dict[str, Any]:
    """
    Retrieve metadata for a Notion block.

    Fetches metadata for a Notion block (including pages, which are special blocks)
    using its UUID. Returns block type, properties, and basic info but not child content.

    Prerequisites:
    1) Block/page must be shared with your integration
    2) Use valid block_id from API responses (not URLs)

    For child blocks, use fetch_block_contents instead.
    Common 404 errors mean the block isn't accessible to your integration.

    Args:
        block_id: The unique UUID identifier for the Notion block to be retrieved.
                  Must be a valid 32-character UUID (with or without hyphens).
                  Pages in Notion are also blocks, so page IDs work here too.

    Returns:
        Block object with metadata, type, and properties

    Example:
        block = await get_page("c02fc1d3-db8b-45c5-a222-27595b15aea7")
    """
    try:
        client = NotionAPIClient()

        # Use blocks endpoint as per Notion API spec
        endpoint = f"/blocks/{block_id}"
        response = await client.get(endpoint)
        return response

    except Exception as e:
        logger.error(f"Failed to get block {block_id}: {e}")
        return {
            "error": f"Failed to retrieve block: {str(e)}",
            "block_id": block_id
        }

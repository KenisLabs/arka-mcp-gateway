"""
Fetch Block Contents tool for Notion MCP server.

Retrieves child blocks of a parent block or page with pagination support.
"""
from typing import Dict, Any, Optional
from .client import NotionAPIClient
import logging

logger = logging.getLogger(__name__)


async def fetch_block_contents(
    block_id: str,
    page_size: Optional[int] = None,
    start_cursor: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Retrieve child blocks of a parent block or page.

    Returns a paginated list of child blocks. Use this to read page content or
    nested block structures. For getting all blocks recursively, use
    fetch_all_block_contents instead.

    Args:
        block_id: UUID of the parent block or page
                  Example: "59833787-2cf9-4fdf-8782-e53db20768a5"
        page_size: Optional number of blocks to return per page (max 100)
                   Example: 50
        start_cursor: Optional cursor for pagination
                      Use next_cursor from previous response
                      Example: "7c6b1c95-de50-45ca-94e6-af1d9fd295ab"

    Returns:
        Paginated list of child blocks with has_more and next_cursor

    Example:
        # Get first page of blocks
        result = await fetch_block_contents(
            block_id="59833787-2cf9-4fdf-8782-e53db20768a5"
        )

        # Get next page using cursor
        result = await fetch_block_contents(
            block_id="59833787-2cf9-4fdf-8782-e53db20768a5",
            start_cursor=result["next_cursor"]
        )

        # Get specific page size
        result = await fetch_block_contents(
            block_id="59833787-2cf9-4fdf-8782-e53db20768a5",
            page_size=25
        )
    """
    try:
        client = NotionAPIClient()

        # Build query params
        params = {}
        if page_size:
            params["page_size"] = min(page_size, 100)  # Notion max is 100
        if start_cursor:
            params["start_cursor"] = start_cursor

        # Fetch child blocks
        endpoint = f"/blocks/{block_id}/children"
        response = await client.get(endpoint, params if params else None)

        return response

    except Exception as e:
        logger.error(f"Failed to fetch block contents for {block_id}: {e}")
        return {
            "error": f"Failed to fetch block contents: {str(e)}",
            "block_id": block_id
        }

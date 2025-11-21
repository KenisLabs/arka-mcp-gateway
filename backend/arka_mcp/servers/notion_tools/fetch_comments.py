"""
Fetch Comments tool for Notion MCP server.

Retrieves comments from a page or block with pagination.
"""
from typing import Dict, Any, Optional
from .client import NotionAPIClient
import logging

logger = logging.getLogger(__name__)


async def fetch_comments(
    block_id: str,
    page_size: Optional[int] = None,
    start_cursor: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Retrieve comments from a Notion page or block.

    Returns paginated list of comments. Comments are ordered by creation time.
    Use this to read discussions on a page.

    Args:
        block_id: UUID of the page or block to fetch comments from
                  Example: "59833787-2cf9-4fdf-8782-e53db20768a5"
        page_size: Optional number of comments to return per page (max 100)
                   Example: 50
        start_cursor: Optional cursor for pagination
                      Use next_cursor from previous response
                      Example: "7c6b1c95-de50-45ca-94e6-af1d9fd295ab"

    Returns:
        Paginated list of comments with has_more and next_cursor

    Example:
        # Get all comments from a page
        comments = await fetch_comments(
            block_id="59833787-2cf9-4fdf-8782-e53db20768a5"
        )

        # Access comment data
        for comment in comments.get("results", []):
            text = comment.get("rich_text", [])
            if text:
                content = text[0].get("text", {}).get("content", "")
                created_by = comment.get("created_by", {}).get("id", "")
                created_time = comment.get("created_time", "")

        # Get next page of comments
        comments = await fetch_comments(
            block_id="59833787-2cf9-4fdf-8782-e53db20768a5",
            start_cursor=comments["next_cursor"]
        )

        # Get specific page size
        comments = await fetch_comments(
            block_id="59833787-2cf9-4fdf-8782-e53db20768a5",
            page_size=25
        )
    """
    try:
        client = NotionAPIClient()

        # Build query params
        params = {
            "block_id": block_id
        }

        if page_size:
            params["page_size"] = min(page_size, 100)  # Notion max is 100

        if start_cursor:
            params["start_cursor"] = start_cursor

        # Fetch comments
        response = await client.get("/comments", params)

        return response

    except Exception as e:
        logger.error(f"Failed to fetch comments for block {block_id}: {e}")
        return {
            "error": f"Failed to fetch comments: {str(e)}",
            "block_id": block_id
        }

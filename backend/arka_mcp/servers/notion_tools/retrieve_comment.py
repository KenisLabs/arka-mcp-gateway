"""
Retrieve Comment tool for Notion MCP server.

Retrieves a specific comment by its ID.
"""
from typing import Dict, Any
from .client import NotionAPIClient
import logging

logger = logging.getLogger(__name__)


async def retrieve_comment(
    comment_id: str,
) -> Dict[str, Any]:
    """
    Retrieve a specific comment by its ID.

    Returns complete comment object including rich text content, author, timestamps,
    and discussion thread information.

    Args:
        comment_id: UUID of the comment to retrieve
                    Example: "9c3c2a5e-f5d4-4d3d-9e5f-8c8e3d5c7d5e"

    Returns:
        Comment object with content and metadata

    Example:
        # Retrieve a specific comment
        comment = await retrieve_comment(
            comment_id="9c3c2a5e-f5d4-4d3d-9e5f-8c8e3d5c7d5e"
        )

        # Access comment properties
        rich_text = comment.get("rich_text", [])
        if rich_text:
            content = rich_text[0].get("text", {}).get("content", "")

        # Get author information
        created_by = comment.get("created_by", {})
        author_id = created_by.get("id", "")

        # Get timestamps
        created_time = comment.get("created_time", "")
        last_edited_time = comment.get("last_edited_time", "")

        # Get discussion thread ID
        discussion_id = comment.get("discussion_id", "")
    """
    try:
        client = NotionAPIClient()

        # Retrieve the comment
        response = await client.get(f"/comments/{comment_id}")

        return response

    except Exception as e:
        logger.error(f"Failed to retrieve comment {comment_id}: {e}")
        return {
            "error": f"Failed to retrieve comment: {str(e)}",
            "comment_id": comment_id
        }

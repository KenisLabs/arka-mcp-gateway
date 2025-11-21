"""
Create Comment tool for Notion MCP server.

Adds a comment to a page or discussion.
"""
from typing import Dict, Any, Optional
from .client import NotionAPIClient
import logging

logger = logging.getLogger(__name__)


async def create_comment(
    page_id: str,
    rich_text: list,
    discussion_id: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Add a comment to a Notion page or discussion thread.

    Creates a new comment on a page. If discussion_id is provided, adds the comment
    to that specific discussion thread; otherwise creates a new top-level comment.

    Args:
        page_id: UUID of the page to comment on
                 Example: "59833787-2cf9-4fdf-8782-e53db20768a5"
        rich_text: Rich text content for the comment
                   Example: [{"text": {"content": "This is a comment"}}]
        discussion_id: Optional UUID of discussion thread to reply to
                       Example: "9c3c2a5e-f5d4-4d3d-9e5f-8c8e3d5c7d5e"

    Returns:
        Created comment object

    Example:
        # Create a new comment
        comment = await create_comment(
            page_id="59833787-2cf9-4fdf-8782-e53db20768a5",
            rich_text=[
                {"text": {"content": "Great work on this page!"}}
            ]
        )

        # Reply to existing discussion
        comment = await create_comment(
            page_id="59833787-2cf9-4fdf-8782-e53db20768a5",
            rich_text=[
                {"text": {"content": "I agree with this point."}}
            ],
            discussion_id="9c3c2a5e-f5d4-4d3d-9e5f-8c8e3d5c7d5e"
        )

        # Create comment with formatted text
        comment = await create_comment(
            page_id="59833787-2cf9-4fdf-8782-e53db20768a5",
            rich_text=[
                {
                    "text": {
                        "content": "Important note",
                        "link": None
                    },
                    "annotations": {
                        "bold": True,
                        "color": "red"
                    }
                }
            ]
        )
    """
    try:
        client = NotionAPIClient()

        # Build comment data
        comment_data = {
            "parent": {"page_id": page_id},
            "rich_text": rich_text
        }

        if discussion_id:
            comment_data["discussion_id"] = discussion_id

        # Create the comment
        response = await client.post("/comments", comment_data)

        return response

    except Exception as e:
        logger.error(f"Failed to create comment on page {page_id}: {e}")
        return {
            "error": f"Failed to create comment: {str(e)}",
            "page_id": page_id
        }

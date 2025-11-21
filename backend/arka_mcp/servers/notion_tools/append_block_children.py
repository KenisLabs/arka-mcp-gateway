"""
Append Block Children tool for Notion MCP server.

Appends child content blocks to a parent block or page.
"""
from typing import Dict, Any, List, Optional
from .client import NotionAPIClient
import logging

logger = logging.getLogger(__name__)


async def append_block_children(
    block_id: str,
    children: List[Dict[str, Any]],
    after: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Append content blocks to a parent block or page.

    Use this to add new content to existing pages or nested blocks. Each block has
    a 2000 character limit. Supports all Notion block types (paragraph, heading,
    lists, etc).

    Args:
        block_id: UUID of the parent block or page
                  Example: "59833787-2cf9-4fdf-8782-e53db20768a5"
        children: List of block objects to append
                  Each block must include 'type' and type-specific properties
                  Example: [{"type": "paragraph", "paragraph": {"rich_text": [{"text": {"content": "Hello"}}]}}]
        after: Optional block_id to insert after (for positioning)
               Example: "b55c9c91-384d-452b-81db-d1ef79372b75"

    Returns:
        Response with appended blocks and parent info

    Example:
        # Add a paragraph block
        result = await append_block_children(
            block_id="59833787-2cf9-4fdf-8782-e53db20768a5",
            children=[{
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [{"text": {"content": "New paragraph"}}]
                }
            }]
        )

        # Add multiple blocks
        result = await append_block_children(
            block_id="59833787-2cf9-4fdf-8782-e53db20768a5",
            children=[
                {
                    "type": "heading_2",
                    "heading_2": {
                        "rich_text": [{"text": {"content": "Section Title"}}]
                    }
                },
                {
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [{"text": {"content": "Section content"}}]
                    }
                }
            ]
        )
    """
    try:
        client = NotionAPIClient()

        # Build request body
        request_body = {"children": children}

        if after:
            request_body["after"] = after

        # Append blocks
        endpoint = f"/blocks/{block_id}/children"
        response = await client.patch(endpoint, request_body)

        return response

    except Exception as e:
        logger.error(f"Failed to append blocks to {block_id}: {e}")
        return {
            "error": f"Failed to append blocks: {str(e)}",
            "block_id": block_id
        }

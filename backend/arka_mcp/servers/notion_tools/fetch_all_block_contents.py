"""
Fetch All Block Contents tool for Notion MCP server.

Recursively retrieves all child blocks of a parent block or page.
"""
from typing import Dict, Any, List, Optional
from .client import NotionAPIClient
import logging

logger = logging.getLogger(__name__)


async def fetch_all_block_contents(
    block_id: str,
    recursive: Optional[bool] = True,
) -> Dict[str, Any]:
    """
    Retrieve all child blocks of a parent block or page, handling pagination automatically.

    Fetches all blocks by following pagination cursors. Optionally fetches nested blocks
    recursively. Use this when you need complete page content without manual pagination.

    Args:
        block_id: UUID of the parent block or page
                  Example: "59833787-2cf9-4fdf-8782-e53db20768a5"
        recursive: If True, recursively fetches nested blocks (default: True)
                   If False, only fetches direct children
                   Example: False

    Returns:
        All blocks with total count and nested structure

    Example:
        # Get all blocks from a page
        result = await fetch_all_block_contents(
            block_id="59833787-2cf9-4fdf-8782-e53db20768a5"
        )

        # Get only direct children (no nesting)
        result = await fetch_all_block_contents(
            block_id="59833787-2cf9-4fdf-8782-e53db20768a5",
            recursive=False
        )
    """
    try:
        client = NotionAPIClient()

        async def fetch_blocks_recursive(parent_id: str) -> List[Dict[str, Any]]:
            """Helper function to recursively fetch blocks."""
            all_blocks = []
            start_cursor = None
            has_more = True

            # Fetch all blocks at this level with pagination
            while has_more:
                params = {}
                if start_cursor:
                    params["start_cursor"] = start_cursor

                endpoint = f"/blocks/{parent_id}/children"
                response = await client.get(endpoint, params if params else None)

                blocks = response.get("results", [])
                all_blocks.extend(blocks)

                has_more = response.get("has_more", False)
                start_cursor = response.get("next_cursor")

            # Recursively fetch nested blocks if enabled
            if recursive:
                for block in all_blocks:
                    if block.get("has_children", False):
                        try:
                            nested_blocks = await fetch_blocks_recursive(block["id"])
                            block["children"] = nested_blocks
                        except Exception as nested_error:
                            logger.warning(f"Failed to fetch nested blocks for {block['id']}: {nested_error}")
                            block["children"] = []

            return all_blocks

        # Fetch all blocks
        blocks = await fetch_blocks_recursive(block_id)

        return {
            "block_id": block_id,
            "total_blocks": len(blocks),
            "recursive": recursive,
            "blocks": blocks
        }

    except Exception as e:
        logger.error(f"Failed to fetch all block contents for {block_id}: {e}")
        return {
            "error": f"Failed to fetch all block contents: {str(e)}",
            "block_id": block_id
        }

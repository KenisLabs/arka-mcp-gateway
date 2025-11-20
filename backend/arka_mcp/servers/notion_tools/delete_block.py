"""
Delete Block tool for Notion MCP server.

Archives (soft deletes) a Notion block.
"""
from typing import Dict, Any
from .client import NotionAPIClient
import logging

logger = logging.getLogger(__name__)


async def delete_block(
    block_id: str,
) -> Dict[str, Any]:
    """
    Archive (soft delete) a Notion block.

    Moves the block to trash. The block can be restored from the Notion UI.
    This operation cannot be undone programmatically. Deleting a parent block
    also archives all its children.

    Note: Notion uses "archive" rather than "delete". Blocks are moved to trash,
    not permanently deleted.

    Args:
        block_id: UUID of the block to archive
                  Example: "59833787-2cf9-4fdf-8782-e53db20768a5"

    Returns:
        Updated block object with archived status

    Example:
        # Archive a block
        result = await delete_block(
            block_id="59833787-2cf9-4fdf-8782-e53db20768a5"
        )
    """
    try:
        client = NotionAPIClient()

        # Archive the block (Notion uses DELETE method)
        response = await client.delete(f"/blocks/{block_id}")

        return response

    except Exception as e:
        logger.error(f"Failed to delete block {block_id}: {e}")
        return {
            "error": f"Failed to delete block: {str(e)}",
            "block_id": block_id
        }

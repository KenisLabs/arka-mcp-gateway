"""
Update Block tool for Notion MCP server.

Updates the content of an existing Notion block.
"""
from typing import Dict, Any, Optional
from .client import NotionAPIClient
import logging

logger = logging.getLogger(__name__)


async def update_block(
    block_id: str,
    content: Optional[str] = None,
    block_data: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Update the content of an existing Notion block.

    Can update block content using either a simple string (for text-based blocks) or
    a full block object (for complex updates). The block type cannot be changed.

    Args:
        block_id: UUID of the block to update
                  Example: "59833787-2cf9-4fdf-8782-e53db20768a5"
        content: Optional simple text content to update
                 Automatically converts to rich_text format
                 Example: "Updated paragraph text"
        block_data: Optional full block object for complex updates
                    Must include block type and properties
                    Example: {"paragraph": {"rich_text": [{"text": {"content": "New text"}}]}}

    Returns:
        Updated block object from Notion API

    Example:
        # Simple text update
        result = await update_block(
            block_id="59833787-2cf9-4fdf-8782-e53db20768a5",
            content="Updated paragraph content"
        )

        # Complex block update
        result = await update_block(
            block_id="59833787-2cf9-4fdf-8782-e53db20768a5",
            block_data={
                "paragraph": {
                    "rich_text": [
                        {"text": {"content": "Bold text", "link": None}},
                        {"text": {"content": " normal text"}}
                    ]
                }
            }
        )
    """
    try:
        client = NotionAPIClient()

        # Validate that at least one update field is provided
        if content is None and block_data is None:
            return {
                "error": "Either 'content' or 'block_data' must be provided",
                "block_id": block_id
            }

        # Build update data
        update_data = {}

        if block_data:
            # Use provided block data directly
            update_data = block_data
        elif content:
            # Get current block to determine type
            block_response = await client.get(f"/blocks/{block_id}")
            block_type = block_response.get("type")

            if not block_type:
                return {
                    "error": "Could not determine block type",
                    "block_id": block_id
                }

            # Build simple text update for the block type
            # Common text-based block types
            text_block_types = [
                "paragraph", "heading_1", "heading_2", "heading_3",
                "bulleted_list_item", "numbered_list_item",
                "toggle", "quote", "callout"
            ]

            if block_type in text_block_types:
                update_data[block_type] = {
                    "rich_text": [{"text": {"content": content}}]
                }
            else:
                return {
                    "error": f"Block type '{block_type}' does not support simple text updates. Use block_data instead.",
                    "block_id": block_id,
                    "block_type": block_type
                }

        # Update the block
        response = await client.patch(f"/blocks/{block_id}", update_data)
        return response

    except Exception as e:
        logger.error(f"Failed to update block {block_id}: {e}")
        return {
            "error": f"Failed to update block: {str(e)}",
            "block_id": block_id
        }

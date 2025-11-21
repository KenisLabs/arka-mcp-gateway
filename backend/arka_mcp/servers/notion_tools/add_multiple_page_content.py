"""
Add Multiple Page Content tool for Notion MCP server.

Bulk-adds multiple content blocks to a page with automatic batching.
"""
from typing import Dict, Any, List
from .client import NotionAPIClient
import logging

logger = logging.getLogger(__name__)


async def add_multiple_page_content(
    page_id: str,
    contents: List[str],
    content_type: str = "paragraph",
) -> Dict[str, Any]:
    """
    Bulk-add multiple content blocks to a Notion page.

    Automatically handles Notion's limits (100 blocks per request, 2000 chars per block).
    Creates multiple requests if needed. Use this for adding large amounts of content
    efficiently.

    Args:
        page_id: UUID of the page to add content to
                 Example: "59833787-2cf9-4fdf-8782-e53db20768a5"
        contents: List of text strings to add as separate blocks
                  Each string becomes one block
                  Example: ["First paragraph", "Second paragraph", "Third paragraph"]
        content_type: Type of blocks to create (default: "paragraph")
                      Options: "paragraph", "heading_1", "heading_2", "heading_3",
                               "bulleted_list_item", "numbered_list_item"
                      Example: "bulleted_list_item"

    Returns:
        Summary of blocks added and any errors

    Example:
        # Add multiple paragraphs
        result = await add_multiple_page_content(
            page_id="59833787-2cf9-4fdf-8782-e53db20768a5",
            contents=[
                "First paragraph of content",
                "Second paragraph of content",
                "Third paragraph of content"
            ]
        )

        # Add bullet points
        result = await add_multiple_page_content(
            page_id="59833787-2cf9-4fdf-8782-e53db20768a5",
            contents=[
                "First bullet point",
                "Second bullet point",
                "Third bullet point"
            ],
            content_type="bulleted_list_item"
        )
    """
    try:
        client = NotionAPIClient()

        # Truncate content that exceeds 2000 chars
        truncated_contents = []
        for content in contents:
            if len(content) > 2000:
                logger.warning(f"Content exceeds 2000 chars, truncating: {content[:50]}...")
                truncated_contents.append(content[:2000])
            else:
                truncated_contents.append(content)

        # Build block objects from content strings
        blocks = []
        for content in truncated_contents:
            block = {
                "type": content_type,
                content_type: {
                    "rich_text": [{"text": {"content": content}}]
                }
            }
            blocks.append(block)

        # Notion API limit: 100 blocks per request
        batch_size = 100
        results = []
        errors = []

        for i in range(0, len(blocks), batch_size):
            batch = blocks[i:i + batch_size]

            try:
                endpoint = f"/blocks/{page_id}/children"
                response = await client.patch(endpoint, {"children": batch})
                results.append({
                    "batch": i // batch_size + 1,
                    "blocks_added": len(batch),
                    "success": True
                })
            except Exception as batch_error:
                logger.error(f"Failed to add batch {i // batch_size + 1}: {batch_error}")
                errors.append({
                    "batch": i // batch_size + 1,
                    "error": str(batch_error)
                })

        return {
            "page_id": page_id,
            "total_blocks": len(blocks),
            "total_batches": len(results) + len(errors),
            "successful_batches": len(results),
            "failed_batches": len(errors),
            "results": results,
            "errors": errors if errors else None
        }

    except Exception as e:
        logger.error(f"Failed to add multiple content to page {page_id}: {e}")
        return {
            "error": f"Failed to add multiple content: {str(e)}",
            "page_id": page_id
        }

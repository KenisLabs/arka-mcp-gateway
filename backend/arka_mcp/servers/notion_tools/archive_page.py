"""
Archive Page tool for Notion MCP server.

Archives (moves to trash) or unarchives (restores) a Notion page.
"""
from typing import Dict, Any, Optional
from .client import NotionAPIClient
import logging

logger = logging.getLogger(__name__)


async def archive_page(
    page_id: str,
    archive: Optional[bool] = True,
) -> Dict[str, Any]:
    """
    Archive (move to trash) or unarchive (restore) a Notion page.

    Args:
        page_id: UUID of the page to archive/unarchive
                 Example: "59833787-2cf9-4fdf-8782-e53db20768a5"
        archive: True to archive (move to trash), False to unarchive (restore)
                 Default: True

    Returns:
        Updated page object from Notion API

    Example:
        # Archive a page
        page = await archive_page(
            page_id="59833787-2cf9-4fdf-8782-e53db20768a5",
            archive=True
        )

        # Restore a page from trash
        page = await archive_page(
            page_id="59833787-2cf9-4fdf-8782-e53db20768a5",
            archive=False
        )
    """
    try:
        client = NotionAPIClient()

        # Update page with archived status
        page_data = {
            "archived": archive
        }

        response = await client.patch(f"/pages/{page_id}", page_data)
        return response

    except Exception as e:
        logger.error(f"Failed to {'archive' if archive else 'unarchive'} page {page_id}: {e}")
        return {
            "error": f"Failed to {'archive' if archive else 'unarchive'} page: {str(e)}",
            "page_id": page_id
        }

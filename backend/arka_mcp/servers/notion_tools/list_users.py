"""
List Users tool for Notion MCP server.

Retrieves a paginated list of all users in the workspace.
"""
from typing import Dict, Optional, Any
from .client import NotionAPIClient
import logging

logger = logging.getLogger(__name__)


async def list_users(
    start_cursor: Optional[str] = None,
    page_size: Optional[int] = None
) -> Dict[str, Any]:
    """
    Retrieve a paginated list of all users in the workspace accessible to the integration.

    This function calls the Notion API endpoint to list users in the workspace, optionally
    starting from a provided cursor and limiting the number of results per page. Guests are
    excluded from the results. Requires the integration to have user-information capabilities.

    Args:
        start_cursor: Pagination cursor from previous response
        page_size: Number of results per page (max 100)

    Returns:
        Paginated list of users with has_more and next_cursor

    Example:
        users = await list_users(page_size=10)
        for user in users['results']:
            print(f"User: {user['name']}")
    """
    try:
        client = NotionAPIClient()

        # Build query params
        params = {}
        if start_cursor:
            params["start_cursor"] = start_cursor
        if page_size:
            params["page_size"] = page_size

        response = await client.get("/users", params if params else None)
        return response

    except Exception as e:
        logger.error(f"Failed to list users: {e}")
        return {
            "error": f"Failed to list users: {str(e)}"
        }

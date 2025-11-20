"""
Get User tool for Notion MCP server.

Retrieves information about a specific user in the workspace.
"""
from typing import Dict, Any
from .client import NotionAPIClient
import logging

logger = logging.getLogger(__name__)


async def get_user(user_id: str) -> Dict[str, Any]:
    """
    Retrieve information about a specific user in the workspace.

    This function calls the Notion API endpoint for a given user ID to look up that
    user's profile data. The user may be a person or a bot. The level of detail
    returned depends on the integration's permissions.

    Args:
        user_id: Notion user ID

    Returns:
        User object with profile information

    Example:
        user = await get_user("abc-123")
        print(f"Name: {user.get('name')}")
    """
    try:
        client = NotionAPIClient()
        response = await client.get(f"/users/{user_id}")
        return response

    except Exception as e:
        logger.error(f"Failed to get user {user_id}: {e}")
        return {
            "error": f"Failed to retrieve user: {str(e)}",
            "user_id": user_id
        }

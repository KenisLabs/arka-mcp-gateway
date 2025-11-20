"""
Get Me tool for Notion MCP server.

Retrieves the bot user associated with the current Notion API token.
"""
from typing import Dict, Any
from .client import NotionAPIClient
import logging

logger = logging.getLogger(__name__)


async def get_me() -> Dict[str, Any]:
    """
    Retrieve the bot user associated with the current Notion API token.

    This calls the Notion `/users/me` endpoint to identify which bot user the
    integration is operating as. The bot user includes an `owner` field that
    indicates the Notion workspace member who authorized this integration.

    Returns:
        Bot user object with owner information

    Example:
        me = await get_me()
        print(f"Bot ID: {me['id']}, Owner: {me['owner']}")
    """
    try:
        client = NotionAPIClient()
        response = await client.get("/users/me")
        return response

    except Exception as e:
        logger.error(f"Failed to get bot user info: {e}")
        return {
            "error": f"Failed to retrieve bot user: {str(e)}"
        }

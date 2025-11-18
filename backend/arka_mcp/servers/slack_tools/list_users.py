"""
Slack List Users Tool.

Lists all users in a Slack workspace using users.list.

Slack API Reference:
https://api.slack.com/methods/users.list
"""
from typing import Dict, Any, Optional
from .client import SlackAPIClient


async def list_users(
    cursor: Optional[str] = None,
    include_locale: Optional[bool] = False,
    limit: Optional[int] = 100,
    team_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    List all users in the Slack workspace.

    Args:
        cursor: Pagination cursor for next page
        include_locale: Include user locale information (default: False)
        limit: Maximum number of users to return (1-1000, default: 100)
        team_id: Filter by team ID (for Enterprise Grid)

    Returns:
        Dict containing:
        - ok: Success status
        - members: List of user objects with id, name, real_name, profile, etc.
        - response_metadata: Pagination metadata with next_cursor
        - cache_ts: Timestamp of user list cache

    Raises:
        ValueError: If Slack API returns an error

    Example:
        result = await list_users(limit=50)
        # Returns: {
        #   "ok": True,
        #   "members": [
        #     {
        #       "id": "U1234567890",
        #       "name": "john.doe",
        #       "real_name": "John Doe",
        #       "profile": {
        #         "email": "john@example.com",
        #         "display_name": "John",
        #         "image_72": "https://...",
        #         ...
        #       },
        #       "is_admin": False,
        #       "is_bot": False,
        #       ...
        #     },
        #     ...
        #   ],
        #   "response_metadata": {"next_cursor": "dGVhbTpDMDYxRkE1UEI="}
        # }

    Notes:
        - Requires users:read scope
        - Includes bots and deactivated users
        - Use is_bot and deleted fields to filter
        - Use cursor for pagination to get all users
        - Profile includes email (requires users:read.email scope)
    """
    client = SlackAPIClient()

    # Build request parameters
    params: Dict[str, Any] = {
        "limit": min(limit, 1000) if limit else 100  # Cap at API maximum
    }

    if cursor:
        params["cursor"] = cursor
    if include_locale:
        params["include_locale"] = include_locale
    if team_id:
        params["team_id"] = team_id

    # Use GET method for users.list
    return await client.get_method("users.list", params)

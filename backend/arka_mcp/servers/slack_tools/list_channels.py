"""
Slack List Channels Tool.

Lists all channels in a Slack workspace using conversations.list.

Slack API Reference:
https://api.slack.com/methods/conversations.list
"""
from typing import Dict, Any, Optional, List
from .client import SlackAPIClient


async def list_channels(
    exclude_archived: Optional[bool] = True,
    types: Optional[str] = "public_channel,private_channel",
    limit: Optional[int] = 100,
    cursor: Optional[str] = None,
    team_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    List all channels in the Slack workspace.

    Args:
        exclude_archived: Exclude archived channels (default: True)
        types: Comma-separated list of conversation types to include:
               - public_channel: Public channels
               - private_channel: Private channels
               - mpim: Multi-party direct messages
               - im: Direct messages
               Default: "public_channel,private_channel"
        limit: Maximum number of channels to return (1-1000, default: 100)
        cursor: Pagination cursor for next page
        team_id: Filter by team ID (for Enterprise Grid)

    Returns:
        Dict containing:
        - ok: Success status
        - channels: List of channel objects with id, name, is_channel, etc.
        - response_metadata: Pagination metadata with next_cursor

    Raises:
        ValueError: If Slack API returns an error

    Example:
        result = await list_channels(
            exclude_archived=True,
            types="public_channel",
            limit=50
        )
        # Returns: {
        #   "ok": True,
        #   "channels": [
        #     {"id": "C1234567890", "name": "general", "is_channel": True, ...},
        #     {"id": "C0987654321", "name": "random", "is_channel": True, ...}
        #   ],
        #   "response_metadata": {"next_cursor": "dGVhbTpDMDYxRkE1UEI="}
        # }

    Notes:
        - Requires channels:read scope for public channels
        - Requires groups:read scope for private channels
        - Use cursor for pagination to get all channels
        - is_archived field indicates if channel is archived
    """
    client = SlackAPIClient()

    # Build request parameters
    params: Dict[str, Any] = {
        "exclude_archived": exclude_archived,
        "types": types,
        "limit": min(limit, 1000) if limit else 100  # Cap at API maximum
    }

    if cursor:
        params["cursor"] = cursor
    if team_id:
        params["team_id"] = team_id

    # Use GET method for conversations.list
    return await client.get_method("conversations.list", params)

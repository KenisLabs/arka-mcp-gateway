"""
Slack List Scheduled Messages Tool.

Lists all scheduled messages using chat.scheduledMessages.list.

Slack API Reference:
https://api.slack.com/methods/chat.scheduledMessages.list
"""
from typing import Dict, Any, Optional
from .client import SlackAPIClient


async def list_scheduled_messages(
    channel: Optional[str] = None,
    cursor: Optional[str] = None,
    latest: Optional[int] = None,
    limit: Optional[int] = 100,
    oldest: Optional[int] = None,
    team_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    List all scheduled messages for the authenticated user.

    Args:
        channel: Filter by channel ID (e.g., "C1234567890")
        cursor: Pagination cursor
        latest: End of time range (Unix timestamp)
        limit: Max number of messages to return (default: 100, max: 1000)
        oldest: Start of time range (Unix timestamp)
        team_id: Team ID for Enterprise Grid

    Returns:
        Dict containing:
        - ok: Success status
        - scheduled_messages: Array of scheduled message objects
        - response_metadata: Pagination metadata with next_cursor

    Raises:
        ValueError: If Slack API returns an error

    Example:
        # List all scheduled messages
        result = await list_scheduled_messages()

        # List for specific channel
        result = await list_scheduled_messages(channel="C1234567890")

        # List with pagination
        result = await list_scheduled_messages(limit=50)
        if result.get("response_metadata", {}).get("next_cursor"):
            next_page = await list_scheduled_messages(
                cursor=result["response_metadata"]["next_cursor"]
            )

    Notes:
        - Requires chat:write scope or channels:read + groups:read + im:read + mpim:read
        - Only returns scheduled messages created by the authenticated user
        - Results ordered by post_at timestamp
        - Supports cursor-based pagination
    """
    client = SlackAPIClient()

    params: Dict[str, Any] = {
        "limit": min(limit, 1000) if limit else 100
    }

    if channel:
        params["channel"] = channel
    if cursor:
        params["cursor"] = cursor
    if latest:
        params["latest"] = latest
    if oldest:
        params["oldest"] = oldest
    if team_id:
        params["team_id"] = team_id

    return await client.get("chat.scheduledMessages.list", params)

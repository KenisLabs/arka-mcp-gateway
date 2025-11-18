"""
Slack Delete Scheduled Message Tool.

Deletes a scheduled message using chat.deleteScheduledMessage.

Slack API Reference:
https://api.slack.com/methods/chat.deleteScheduledMessage
"""
from typing import Dict, Any, Optional
from .client import SlackAPIClient


async def delete_scheduled_message(
    channel: str,
    scheduled_message_id: str,
    as_user: Optional[bool] = False
) -> Dict[str, Any]:
    """
    Delete a scheduled message before it's sent.

    Args:
        channel: Channel ID where message is scheduled (e.g., "C1234567890")
        scheduled_message_id: Scheduled message ID (e.g., "Q1234567890")
        as_user: Delete as authed user (default: False)

    Returns:
        Dict containing:
        - ok: Success status

    Raises:
        ValueError: If Slack API returns an error

    Example:
        # Delete scheduled message
        result = await delete_scheduled_message(
            channel="C1234567890",
            scheduled_message_id="Q1234567890"
        )
        # Returns: {"ok": True}

    Notes:
        - Requires chat:write scope
        - Can only delete your own scheduled messages
        - Returns error "invalid_scheduled_message_id" if not found
        - Returns error "channel_not_found" if channel doesn't exist
        - Once message is posted, it can't be deleted with this method
    """
    client = SlackAPIClient()

    params: Dict[str, Any] = {
        "channel": channel,
        "scheduled_message_id": scheduled_message_id
    }

    if as_user:
        params["as_user"] = as_user

    return await client.post("chat.deleteScheduledMessage", params)

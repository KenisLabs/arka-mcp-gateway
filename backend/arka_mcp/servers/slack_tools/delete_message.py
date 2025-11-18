"""
Slack Delete Message Tool.

Deletes a Slack message using chat.delete.

Slack API Reference:
https://api.slack.com/methods/chat.delete
"""
from typing import Dict, Any
from .client import SlackAPIClient


async def delete_message(
    channel: str,
    ts: str,
    as_user: bool = False
) -> Dict[str, Any]:
    """
    Delete a Slack message.

    Args:
        channel: Channel ID containing the message (e.g., C1234567890)
        ts: Timestamp of the message to delete (e.g., "1234567890.123456")
        as_user: Delete as the authed user (bot apps should use False)

    Returns:
        Dict containing:
        - ok: Success status (True if message deleted successfully)
        - channel: Channel ID
        - ts: Timestamp of deleted message

    Raises:
        ValueError: If Slack API returns an error

    Example:
        # Delete a message
        result = await delete_message(
            channel="C1234567890",
            ts="1234567890.123456"
        )
        # Returns: {
        #   "ok": True,
        #   "channel": "C1234567890",
        #   "ts": "1234567890.123456"
        # }

        # Delete thread parent (also deletes all replies)
        result = await delete_message(
            channel="C1234567890",
            ts="1234567890.000000"
        )

        # Delete specific thread reply
        result = await delete_message(
            channel="C1234567890",
            ts="1234567890.123456"
        )

        # Delete as authenticated user
        result = await delete_message(
            channel="C1234567890",
            ts="1234567890.123456",
            as_user=True
        )

    Notes:
        - Requires chat:write scope
        - Can only delete messages sent by the authenticated bot/user
        - Cannot delete messages older than 5 years
        - Deleting a thread parent deletes all replies
        - Deleted messages cannot be recovered
        - Returns error "message_not_found" if ts doesn't exist
        - Returns error "cant_delete_message" if not message author
        - Returns error "compliance_exports_prevent_deletion" if retention policy blocks deletion
        - Returns error "channel_not_found" if channel doesn't exist
        - Returns error "is_archived" if channel is archived
        - Workspace admins can delete any message regardless of author
        - Enterprise Grid workspaces may have retention policies preventing deletion
        - as_user parameter only works for user tokens, not bot tokens
        - No visual "deleted" indicator is shown (message simply disappears)
        - Consider using update_message to show "Message deleted by user" instead for audit trail
    """
    client = SlackAPIClient()

    # Build request parameters
    params: Dict[str, Any] = {
        "channel": channel,
        "ts": ts
    }

    if as_user:
        params["as_user"] = as_user

    # Use POST method for chat.delete
    return await client.call_method("chat.delete", params)

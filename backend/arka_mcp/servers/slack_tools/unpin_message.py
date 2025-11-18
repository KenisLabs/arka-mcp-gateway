"""
Slack Unpin Message Tool.

Unpins a message from a Slack channel using pins.remove.

Slack API Reference:
https://api.slack.com/methods/pins.remove
"""
from typing import Dict, Any
from .client import SlackAPIClient


async def unpin_message(
    channel: str,
    timestamp: str
) -> Dict[str, Any]:
    """
    Unpin a message from a Slack channel.

    Args:
        channel: Channel ID where the message is located (e.g., C1234567890)
        timestamp: Timestamp of the message to unpin (e.g., "1234567890.123456")

    Returns:
        Dict containing:
        - ok: Success status (True if message unpinned successfully)

    Raises:
        ValueError: If Slack API returns an error

    Example:
        # Unpin an outdated message
        result = await unpin_message(
            channel="C1234567890",
            timestamp="1234567890.123456"
        )
        # Returns: {"ok": True}

        # Unpin old announcement
        result = await unpin_message(
            channel="C9876543210",
            timestamp="1609459200.000000"
        )

        # Unpin completed meeting notes
        result = await unpin_message(
            channel="C5555555555",
            timestamp="1234567890.111111"
        )

    Notes:
        - Requires pins:write scope
        - Bot must be a member of the channel
        - Returns error "no_pin" if message is not currently pinned
        - Returns error "message_not_found" if timestamp doesn't exist
        - Returns error "channel_not_found" if channel doesn't exist
        - Returns error "not_in_channel" if bot is not in channel
        - Returns error "is_archived" if channel is archived
        - Returns error "permission_denied" if lacking permissions
        - All channel members receive notification when message is unpinned
        - Unpinning removes message from channel details sidebar
        - Original message remains in channel history
        - Use pins.list to see currently pinned messages before unpinning
        - Workspace admins can unpin messages in any channel
        - Private channel operations only visible to channel members
        - Can unpin regular messages, thread parents, or files
        - Unpinning does not delete the message
    """
    client = SlackAPIClient()

    # Build request parameters
    params: Dict[str, Any] = {
        "channel": channel,
        "timestamp": timestamp
    }

    # Use POST method for pins.remove
    return await client.call_method("pins.remove", params)

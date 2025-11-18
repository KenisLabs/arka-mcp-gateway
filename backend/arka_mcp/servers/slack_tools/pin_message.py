"""
Slack Pin Message Tool.

Pins a message to a Slack channel using pins.add.

Slack API Reference:
https://api.slack.com/methods/pins.add
"""
from typing import Dict, Any
from .client import SlackAPIClient


async def pin_message(
    channel: str,
    timestamp: str
) -> Dict[str, Any]:
    """
    Pin a message to a Slack channel.

    Args:
        channel: Channel ID where the message is located (e.g., C1234567890)
        timestamp: Timestamp of the message to pin (e.g., "1234567890.123456")

    Returns:
        Dict containing:
        - ok: Success status (True if message pinned successfully)

    Raises:
        ValueError: If Slack API returns an error

    Example:
        # Pin an important message
        result = await pin_message(
            channel="C1234567890",
            timestamp="1234567890.123456"
        )
        # Returns: {"ok": True}

        # Pin announcement to channel
        result = await pin_message(
            channel="C9876543210",
            timestamp="1609459200.000000"
        )

        # Pin meeting notes thread
        result = await pin_message(
            channel="C5555555555",
            timestamp="1234567890.111111"
        )

    Notes:
        - Requires pins:write scope
        - Bot must be a member of the channel
        - Channels can have maximum of 100 pinned items
        - Pinned messages appear in channel details sidebar
        - Returns error "already_pinned" if message is already pinned
        - Returns error "message_not_found" if timestamp doesn't exist
        - Returns error "channel_not_found" if channel doesn't exist
        - Returns error "not_in_channel" if bot is not in channel
        - Returns error "is_archived" if channel is archived
        - Returns error "too_many_pins" if channel has 100 pins already
        - Returns error "permission_denied" if lacking permissions
        - All channel members receive notification when message is pinned
        - Pinned messages remain accessible even if original is deleted
        - Use pins.list to retrieve all pinned messages in a channel
        - Workspace admins can pin messages in any channel
        - Private channel pins are only visible to channel members
        - Can pin regular messages, thread parents, or files
    """
    client = SlackAPIClient()

    # Build request parameters
    params: Dict[str, Any] = {
        "channel": channel,
        "timestamp": timestamp
    }

    # Use POST method for pins.add
    return await client.call_method("pins.add", params)

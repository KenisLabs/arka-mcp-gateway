"""
Slack Archive Channel Tool.

Archives a Slack channel using conversations.archive.

Slack API Reference:
https://api.slack.com/methods/conversations.archive
"""
from typing import Dict, Any
from .client import SlackAPIClient


async def archive_channel(
    channel: str
) -> Dict[str, Any]:
    """
    Archive a Slack channel.

    Args:
        channel: Channel ID to archive (e.g., C1234567890)

    Returns:
        Dict containing:
        - ok: Success status (True if channel archived successfully)

    Raises:
        ValueError: If Slack API returns an error

    Example:
        # Archive a channel
        result = await archive_channel(
            channel="C1234567890"
        )
        # Returns: {"ok": True}

        # Archive project channel after completion
        result = await archive_channel(
            channel="C9876543210"
        )

    Notes:
        - Requires channels:manage scope for public channels
        - Requires groups:write scope for private channels
        - Cannot archive the #general channel
        - Cannot archive already archived channels (returns "already_archived" error)
        - Archived channels are read-only but searchable
        - Archived channels can be unarchived later
        - All members remain in archived channels
        - Returns error "channel_not_found" if channel doesn't exist
        - Returns error "not_in_channel" if bot is not in the channel
        - Returns error "is_archived" if channel is already archived
        - Returns error "cant_archive_general" if trying to archive #general
        - Archiving removes the channel from active channel lists
        - Messages in archived channels remain searchable
        - Only admins and channel creators can archive by default
    """
    client = SlackAPIClient()

    # Build request parameters
    params: Dict[str, Any] = {
        "channel": channel
    }

    # Use POST method for conversations.archive
    return await client.call_method("conversations.archive", params)

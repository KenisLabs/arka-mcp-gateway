"""
Slack Kick from Channel Tool.

Removes a user from a Slack channel using conversations.kick.

Slack API Reference:
https://api.slack.com/methods/conversations.kick
"""
from typing import Dict, Any
from .client import SlackAPIClient


async def kick_from_channel(
    channel: str,
    user: str
) -> Dict[str, Any]:
    """
    Remove a user from a Slack channel.

    Args:
        channel: Channel ID to remove user from (e.g., C1234567890)
        user: User ID to remove (e.g., U1234567890)

    Returns:
        Dict containing:
        - ok: Success status (True if user removed successfully)

    Raises:
        ValueError: If Slack API returns an error

    Example:
        # Remove user from channel
        result = await kick_from_channel(
            channel="C1234567890",
            user="U1234567890"
        )
        # Returns: {"ok": True}

        # Remove user from private channel
        result = await kick_from_channel(
            channel="G1234567890",
            user="U9876543210"
        )

        # Remove inactive user from project channel
        result = await kick_from_channel(
            channel="C5555555555",
            user="U9999999999"
        )

    Notes:
        - Requires channels:manage scope for public channels
        - Requires groups:write scope for private channels
        - Bot must be a member of the channel to remove users
        - Cannot remove users from #general channel
        - Cannot remove yourself from a channel
        - Returns error "not_in_channel" if bot is not in channel
        - Returns error "channel_not_found" if channel doesn't exist
        - Returns error "user_not_found" if user ID doesn't exist
        - Returns error "cant_kick_self" if trying to kick yourself
        - Returns error "cant_kick_from_general" if trying to kick from #general
        - Returns error "cant_kick_from_last_channel" if user's last channel
        - Returns error "user_not_in_channel" if user is not in the channel
        - Returns error "is_archived" if channel is archived
        - Removed user will no longer see channel in their sidebar
        - Removed user can be re-invited later
        - User receives notification about being removed
        - Only workspace admins and channel creators can remove users by default
        - Enterprise Grid workspaces may have additional restrictions
    """
    client = SlackAPIClient()

    # Build request parameters
    params: Dict[str, Any] = {
        "channel": channel,
        "user": user
    }

    # Use POST method for conversations.kick
    return await client.call_method("conversations.kick", params)

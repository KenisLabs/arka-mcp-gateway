"""
Slack Invite to Channel Tool.

Invites users to a Slack channel using conversations.invite.

Slack API Reference:
https://api.slack.com/methods/conversations.invite
"""
from typing import Dict, Any, List
from .client import SlackAPIClient


async def invite_to_channel(
    channel: str,
    users: List[str]
) -> Dict[str, Any]:
    """
    Invite users to a Slack channel.

    Args:
        channel: Channel ID to invite users to (e.g., C1234567890)
        users: List of user IDs to invite (e.g., ["U1234567890", "U0987654321"])

    Returns:
        Dict containing:
        - ok: Success status
        - channel: Updated channel object with new members

    Raises:
        ValueError: If Slack API returns an error

    Example:
        # Invite single user to channel
        result = await invite_to_channel(
            channel="C1234567890",
            users=["U1234567890"]
        )
        # Returns: {
        #   "ok": True,
        #   "channel": {
        #     "id": "C1234567890",
        #     "name": "project-alpha",
        #     "num_members": 5,
        #     ...
        #   }
        # }

        # Invite multiple users to channel
        result = await invite_to_channel(
            channel="C1234567890",
            users=["U1111111111", "U2222222222", "U3333333333"]
        )

        # Invite users to private channel
        result = await invite_to_channel(
            channel="G1234567890",
            users=["U9999999999"]
        )

    Notes:
        - Requires channels:manage scope for public channels
        - Requires groups:write scope for private channels
        - Bot must be a member of the channel to invite users
        - Can invite up to 1000 users per request
        - Returns error "not_in_channel" if bot is not in channel
        - Returns error "channel_not_found" if channel doesn't exist
        - Returns error "user_not_found" if user ID doesn't exist
        - Returns error "cant_invite_self" if trying to invite yourself
        - Returns error "already_in_channel" if user is already a member
        - Returns error "is_archived" if channel is archived
        - Returns error "user_is_restricted" if inviting restricted user to public channel
        - Returns error "user_is_ultra_restricted" if inviting single-channel guest incorrectly
        - Invited users receive notification about the invitation
        - For private channels, only members can invite new users
        - Enterprise Grid workspaces may have additional restrictions
    """
    client = SlackAPIClient()

    # Build request parameters
    params: Dict[str, Any] = {
        "channel": channel,
        "users": ",".join(users)  # API expects comma-separated string
    }

    # Use POST method for conversations.invite
    return await client.call_method("conversations.invite", params)

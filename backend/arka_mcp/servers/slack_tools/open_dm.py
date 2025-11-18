"""
Slack Open DM Tool.

Opens a direct message or multi-person DM using conversations.open.

Slack API Reference:
https://api.slack.com/methods/conversations.open
"""
from typing import Dict, Any, Optional
from .client import SlackAPIClient


async def open_dm(
    users: str,
    return_im: Optional[bool] = False
) -> Dict[str, Any]:
    """
    Open a direct message conversation.

    Args:
        users: User ID or comma-separated user IDs (e.g., "U1234567890" or "U111,U222,U333")
        return_im: Return the full IM channel object (default: False)

    Returns:
        Dict containing:
        - ok: Success status
        - channel: Channel object with:
          - id: DM channel ID (e.g., "D1234567890")
          - created: Creation timestamp
          - is_im: True for 1-on-1 DMs
          - is_org_shared: Whether shared across org
          - user: User ID (for 1-on-1 DMs)
          - is_user_deleted: Whether user is deleted
        - already_open: Whether the DM was already open
        - no_op: Whether this was a no-op

    Raises:
        ValueError: If Slack API returns an error

    Example:
        # Open 1-on-1 DM
        result = await open_dm(users="U1234567890")
        # Returns: {"ok": True, "channel": {"id": "D1234567890", ...}}

        # Open multi-person DM (up to 8 people)
        result = await open_dm(users="U111,U222,U333")
        # Returns: {"ok": True, "channel": {"id": "G1234567890", ...}}

        # Get full IM object
        result = await open_dm(
            users="U1234567890",
            return_im=True
        )

    Notes:
        - Requires im:write or mpim:write scope
        - For 1-on-1 DMs, provide single user ID
        - For group DMs, provide comma-separated user IDs (max 8 users)
        - If DM already exists, returns existing channel
        - Returns D* ID for 1-on-1 DMs
        - Returns G* ID for multi-person DMs
        - Use the returned channel ID to send messages
    """
    client = SlackAPIClient()

    params: Dict[str, Any] = {
        "users": users
    }

    if return_im:
        params["return_im"] = return_im

    return await client.post("conversations.open", params)

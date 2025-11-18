"""
Slack Clear Status Tool.

Clears the user's Slack status using users.profile.set.

Slack API Reference:
https://api.slack.com/methods/users.profile.set
"""
from typing import Dict, Any
from .client import SlackAPIClient


async def clear_status() -> Dict[str, Any]:
    """
    Clear the authenticated user's Slack status.

    Returns:
        Dict containing:
        - ok: Success status
        - profile: Updated user profile

    Raises:
        ValueError: If Slack API returns an error

    Example:
        # Clear status
        result = await clear_status()
        # Returns: {"ok": True, "profile": {...}}

    Notes:
        - Requires users.profile:write scope
        - Sets status_text and status_emoji to empty strings
        - Removes any status expiration
    """
    client = SlackAPIClient()

    params = {
        "profile": {
            "status_text": "",
            "status_emoji": "",
            "status_expiration": 0
        }
    }

    return await client.post("users.profile.set", params)

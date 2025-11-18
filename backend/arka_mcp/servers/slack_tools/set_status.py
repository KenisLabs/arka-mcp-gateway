"""
Slack Set Status Tool.

Sets the user's Slack status using users.profile.set.

Slack API Reference:
https://api.slack.com/methods/users.profile.set
"""
from typing import Dict, Any, Optional
from .client import SlackAPIClient


async def set_status(
    status_text: str,
    status_emoji: str,
    status_expiration: Optional[int] = None
) -> Dict[str, Any]:
    """
    Set the authenticated user's Slack status.

    Args:
        status_text: Status text to display (e.g., "In a meeting")
        status_emoji: Status emoji (e.g., ":calendar:" or "calendar")
        status_expiration: Unix timestamp when status expires (optional)

    Returns:
        Dict containing:
        - ok: Success status
        - profile: Updated user profile

    Raises:
        ValueError: If Slack API returns an error

    Example:
        # Set status
        result = await set_status(
            status_text="In a meeting",
            status_emoji=":calendar:"
        )

        # Set status with expiration (30 minutes)
        import time
        result = await set_status(
            status_text="On lunch break",
            status_emoji=":hamburger:",
            status_expiration=int(time.time()) + 1800
        )

    Notes:
        - Requires users.profile:write scope
        - Status emoji should include colons (e.g., ":rocket:")
        - If status_expiration is provided, status clears automatically
        - Maximum status_text length is 100 characters
    """
    client = SlackAPIClient()

    # Ensure emoji has colons
    if status_emoji and not status_emoji.startswith(":"):
        status_emoji = f":{status_emoji}:"
    if status_emoji and not status_emoji.endswith(":"):
        status_emoji = f"{status_emoji}:"

    profile = {
        "status_text": status_text,
        "status_emoji": status_emoji
    }

    if status_expiration:
        profile["status_expiration"] = status_expiration

    params = {"profile": profile}

    return await client.post("users.profile.set", params)

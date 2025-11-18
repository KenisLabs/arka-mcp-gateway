"""
Slack Remove Reaction Tool.

Removes an emoji reaction from a message using reactions.remove.

Slack API Reference:
https://api.slack.com/methods/reactions.remove
"""
from typing import Dict, Any
from .client import SlackAPIClient


async def remove_reaction(
    channel: str,
    timestamp: str,
    name: str
) -> Dict[str, Any]:
    """
    Remove an emoji reaction from a Slack message.

    Args:
        channel: Channel ID where the message is located (e.g., C1234567890)
        timestamp: Timestamp of the message to remove reaction from (e.g., "1234567890.123456")
        name: Emoji name without colons (e.g., "thumbsup", "heart", "fire")

    Returns:
        Dict containing:
        - ok: Success status (True if reaction removed successfully)

    Raises:
        ValueError: If Slack API returns an error

    Example:
        # Remove thumbs up reaction
        result = await remove_reaction(
            channel="C1234567890",
            timestamp="1234567890.123456",
            name="thumbsup"
        )
        # Returns: {"ok": True}

        # Remove custom emoji reaction
        result = await remove_reaction(
            channel="C1234567890",
            timestamp="1234567890.123456",
            name="party_parrot"
        )

        # Remove heart reaction
        result = await remove_reaction(
            channel="C1234567890",
            timestamp="1234567890.123456",
            name="heart"
        )

    Notes:
        - Requires reactions:write scope
        - Emoji name should not include colons (use "thumbsup" not ":thumbsup:")
        - Can only remove reactions that the authenticated user has added
        - If reaction doesn't exist, API returns error "no_reaction"
        - Use the message timestamp (ts field) from conversations.history
        - Must match the exact emoji name used when adding the reaction
        - Cannot remove reactions added by other users
    """
    client = SlackAPIClient()

    # Build request parameters
    params: Dict[str, Any] = {
        "channel": channel,
        "timestamp": timestamp,
        "name": name
    }

    # Use POST method for reactions.remove
    return await client.call_method("reactions.remove", params)

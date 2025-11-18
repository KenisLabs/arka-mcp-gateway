"""
Slack Add Reaction Tool.

Adds an emoji reaction to a message using reactions.add.

Slack API Reference:
https://api.slack.com/methods/reactions.add
"""
from typing import Dict, Any
from .client import SlackAPIClient


async def add_reaction(
    channel: str,
    timestamp: str,
    name: str
) -> Dict[str, Any]:
    """
    Add an emoji reaction to a Slack message.

    Args:
        channel: Channel ID where the message is located (e.g., C1234567890)
        timestamp: Timestamp of the message to react to (e.g., "1234567890.123456")
        name: Emoji name without colons (e.g., "thumbsup", "heart", "fire")

    Returns:
        Dict containing:
        - ok: Success status (True if reaction added successfully)

    Raises:
        ValueError: If Slack API returns an error

    Example:
        # Add thumbs up reaction
        result = await add_reaction(
            channel="C1234567890",
            timestamp="1234567890.123456",
            name="thumbsup"
        )
        # Returns: {"ok": True}

        # Add custom emoji reaction
        result = await add_reaction(
            channel="C1234567890",
            timestamp="1234567890.123456",
            name="party_parrot"
        )

        # Add heart reaction
        result = await add_reaction(
            channel="C1234567890",
            timestamp="1234567890.123456",
            name="heart"
        )

    Notes:
        - Requires reactions:write scope
        - Emoji name should not include colons (use "thumbsup" not ":thumbsup:")
        - Can use standard emoji or custom workspace emoji
        - If reaction already exists from this user, API returns error "already_reacted"
        - Use the message timestamp (ts field) from conversations.history
        - Standard emoji names: thumbsup, thumbsdown, heart, fire, eyes, tada, etc.
        - See full emoji list: https://www.webfx.com/tools/emoji-cheat-sheet/
    """
    client = SlackAPIClient()

    # Build request parameters
    params: Dict[str, Any] = {
        "channel": channel,
        "timestamp": timestamp,
        "name": name
    }

    # Use POST method for reactions.add
    return await client.call_method("reactions.add", params)

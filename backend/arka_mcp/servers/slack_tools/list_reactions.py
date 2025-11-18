"""
Slack List Reactions Tool.

Gets all reactions on a specific message using reactions.get.

Slack API Reference:
https://api.slack.com/methods/reactions.get
"""
from typing import Dict, Any, Optional
from .client import SlackAPIClient


async def list_reactions(
    channel: str,
    timestamp: str,
    full: Optional[bool] = False
) -> Dict[str, Any]:
    """
    Get all reactions on a Slack message.

    Args:
        channel: Channel ID where the message is located (e.g., C1234567890)
        timestamp: Timestamp of the message (e.g., "1234567890.123456")
        full: Return full user objects instead of just IDs (default: False)

    Returns:
        Dict containing:
        - ok: Success status
        - type: "message"
        - channel: Channel ID
        - message: Message object with:
          - type: "message"
          - user: User ID who posted
          - text: Message text
          - ts: Message timestamp
          - reactions: Array of reaction objects, each with:
            - name: Emoji name (e.g., "thumbsup", "heart", "fire")
            - count: Number of users who reacted with this emoji
            - users: Array of user IDs who reacted (or user objects if full=True)

    Raises:
        ValueError: If Slack API returns an error

    Example:
        # Get reactions for a message
        result = await list_reactions(
            channel="C1234567890",
            timestamp="1234567890.123456"
        )
        # Returns: {
        #   "ok": True,
        #   "type": "message",
        #   "channel": "C1234567890",
        #   "message": {
        #     "type": "message",
        #     "user": "U1234567890",
        #     "text": "Great job team! :rocket:",
        #     "ts": "1234567890.123456",
        #     "reactions": [
        #       {
        #         "name": "thumbsup",
        #         "count": 5,
        #         "users": ["U1111111111", "U2222222222", "U3333333333", "U4444444444", "U5555555555"]
        #       },
        #       {
        #         "name": "heart",
        #         "count": 3,
        #         "users": ["U2222222222", "U6666666666", "U7777777777"]
        #       },
        #       {
        #         "name": "fire",
        #         "count": 2,
        #         "users": ["U1111111111", "U8888888888"]
        #       },
        #       {
        #         "name": "rocket",
        #         "count": 1,
        #         "users": ["U9999999999"]
        #       }
        #     ]
        #   }
        # }

        # Get reactions with full user objects
        result = await list_reactions(
            channel="C1234567890",
            timestamp="1234567890.123456",
            full=True
        )
        # Returns reactions with full user details instead of just IDs

        # Check reactions on a thread reply
        result = await list_reactions(
            channel="C1234567890",
            timestamp="1234567890.234567"
        )

        # No reactions case
        result = await list_reactions(
            channel="C1234567890",
            timestamp="1234567890.345678"
        )
        # Returns: {
        #   "ok": True,
        #   "type": "message",
        #   "channel": "C1234567890",
        #   "message": {
        #     "type": "message",
        #     "user": "U1234567890",
        #     "text": "No reactions yet",
        #     "ts": "1234567890.345678"
        #     # Note: "reactions" field is absent when no reactions
        #   }
        # }

    Notes:
        - Requires reactions:read scope
        - Bot/user must have access to the channel
        - Returns error "message_not_found" if timestamp doesn't exist
        - Returns error "channel_not_found" if channel doesn't exist
        - Returns error "not_in_channel" if bot/user not in channel
        - Reactions are ordered by when they were first added
        - Each reaction shows which users added it
        - Same user can only add each emoji once
        - Users array is in order reactions were added
        - full=True includes user profile details (name, avatar, etc.)
        - Custom workspace emoji are supported
        - Skin tone variants count as separate reactions
        - If message has no reactions, "reactions" field is absent
        - Useful for analyzing message engagement
        - Can be used to see who supports an idea/proposal
        - Works with both channel messages and thread replies
        - File comments can also have reactions (use file and file_comment params)
    """
    client = SlackAPIClient()

    # Build request parameters
    params: Dict[str, Any] = {
        "channel": channel,
        "timestamp": timestamp
    }

    if full:
        params["full"] = full

    # Use GET method for reactions.get
    return await client.get_method("reactions.get", params)

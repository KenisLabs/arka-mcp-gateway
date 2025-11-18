"""
Slack List Messages Tool.

Lists messages from a Slack channel or conversation using conversations.history.

Slack API Reference:
https://api.slack.com/methods/conversations.history
"""
from typing import Dict, Any, Optional
from .client import SlackAPIClient


async def list_messages(
    channel: str,
    cursor: Optional[str] = None,
    inclusive: Optional[bool] = False,
    latest: Optional[str] = None,
    limit: Optional[int] = 100,
    oldest: Optional[str] = None,
    include_all_metadata: Optional[bool] = False
) -> Dict[str, Any]:
    """
    List messages from a Slack channel or conversation.

    Args:
        channel: Channel ID to fetch history from (e.g., C1234567890)
        cursor: Pagination cursor for next page
        inclusive: Include messages with latest or oldest timestamp (default: False)
        latest: End of time range (Unix timestamp or message ts)
        limit: Maximum number of messages to return (1-1000, default: 100)
        oldest: Start of time range (Unix timestamp or message ts)
        include_all_metadata: Include all message metadata (default: False)

    Returns:
        Dict containing:
        - ok: Success status
        - messages: List of message objects, each containing:
          - type: Message type (usually "message")
          - user: User ID who posted the message
          - text: Message text content
          - ts: Timestamp (unique message identifier)
          - thread_ts: Parent message timestamp (if in thread)
          - reply_count: Number of replies (if thread parent)
          - reply_users_count: Number of users who replied
          - latest_reply: Timestamp of latest reply
          - reply_users: List of user IDs who replied
          - subscribed: True if user is subscribed to thread
          - last_read: Timestamp of user's last read
          - unread_count: Number of unread messages in thread
          - attachments: Legacy message attachments
          - blocks: Block Kit blocks
          - files: List of attached files
          - upload: True if file upload message
          - reactions: List of reaction objects
          - edited: Edit metadata if message was edited
          - bot_id: Bot ID if posted by bot
          - app_id: App ID if posted by app
          - metadata: Message metadata
        - has_more: True if more messages available
        - pin_count: Number of pinned messages in channel
        - channel_actions_ts: Timestamp of latest channel action
        - channel_actions_count: Number of channel actions
        - response_metadata: Pagination metadata with next_cursor

    Raises:
        ValueError: If Slack API returns an error

    Example:
        # Get latest 50 messages
        result = await list_messages(
            channel="C1234567890",
            limit=50
        )

        # Get messages in time range
        result = await list_messages(
            channel="C1234567890",
            oldest="1609459200.000000",  # Jan 1, 2021
            latest="1612137600.000000",  # Feb 1, 2021
            inclusive=True
        )

        # Paginate through messages
        result = await list_messages(
            channel="C1234567890",
            cursor="dGVhbTpDMDYxRkE1UEI="
        )

        # Returns: {
        #   "ok": True,
        #   "messages": [
        #     {
        #       "type": "message",
        #       "user": "U1234567890",
        #       "text": "Hello world!",
        #       "ts": "1234567890.123456",
        #       "reactions": [
        #         {"name": "thumbsup", "count": 3, "users": ["U111", "U222", "U333"]}
        #       ]
        #     },
        #     ...
        #   ],
        #   "has_more": True,
        #   "response_metadata": {"next_cursor": "dGVhbTpDMDYxRkE1UEI="}
        # }

    Notes:
        - Requires channels:history scope for public channels
        - Requires groups:history scope for private channels
        - Requires im:history scope for direct messages
        - Requires mpim:history scope for multi-party DMs
        - Messages are returned in reverse chronological order (newest first)
        - Use oldest/latest for time-based filtering
        - Use cursor for pagination to get all messages
        - ts (timestamp) is the unique message identifier
        - thread_ts identifies messages in a thread
    """
    client = SlackAPIClient()

    # Build request parameters
    params: Dict[str, Any] = {
        "channel": channel,
        "limit": min(limit, 1000) if limit else 100  # Cap at API maximum
    }

    if cursor:
        params["cursor"] = cursor
    if inclusive is not None:
        params["inclusive"] = inclusive
    if latest:
        params["latest"] = latest
    if oldest:
        params["oldest"] = oldest
    if include_all_metadata:
        params["include_all_metadata"] = include_all_metadata

    # Use GET method for conversations.history
    return await client.get_method("conversations.history", params)

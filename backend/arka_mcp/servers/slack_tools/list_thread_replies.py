"""
Slack List Thread Replies Tool.

Retrieves all replies in a message thread using conversations.replies.

Slack API Reference:
https://api.slack.com/methods/conversations.replies
"""
from typing import Dict, Any, Optional
from .client import SlackAPIClient


async def list_thread_replies(
    channel: str,
    ts: str,
    cursor: Optional[str] = None,
    inclusive: Optional[bool] = False,
    latest: Optional[str] = None,
    limit: Optional[int] = 100,
    oldest: Optional[str] = None
) -> Dict[str, Any]:
    """
    Retrieve all replies in a message thread.

    Args:
        channel: Channel ID containing the thread (e.g., C1234567890)
        ts: Timestamp of the parent message (thread_ts) (e.g., "1234567890.123456")
        cursor: Pagination cursor for next page
        inclusive: Include parent message with latest or oldest timestamp (default: False)
        latest: End of time range (Unix timestamp)
        limit: Maximum number of messages to return (1-1000, default: 100)
        oldest: Start of time range (Unix timestamp)

    Returns:
        Dict containing:
        - ok: Success status
        - messages: List of message objects in the thread, including:
          - Parent message (first in array)
          - All replies in chronological order
          - Each message has: type, user, text, ts, thread_ts, reply_count, etc.
        - has_more: True if more messages available
        - response_metadata: Pagination metadata with next_cursor

    Raises:
        ValueError: If Slack API returns an error

    Example:
        # Get all replies in a thread
        result = await list_thread_replies(
            channel="C1234567890",
            ts="1234567890.123456"
        )
        # Returns: {
        #   "ok": True,
        #   "messages": [
        #     {
        #       "type": "message",
        #       "user": "U1234567890",
        #       "text": "Original message (thread parent)",
        #       "ts": "1234567890.123456",
        #       "thread_ts": "1234567890.123456",
        #       "reply_count": 3,
        #       "reply_users": ["U111", "U222"],
        #       ...
        #     },
        #     {
        #       "type": "message",
        #       "user": "U2222222222",
        #       "text": "First reply",
        #       "ts": "1234567890.234567",
        #       "thread_ts": "1234567890.123456",
        #       ...
        #     },
        #     {
        #       "type": "message",
        #       "user": "U3333333333",
        #       "text": "Second reply",
        #       "ts": "1234567890.345678",
        #       "thread_ts": "1234567890.123456",
        #       ...
        #     }
        #   ],
        #   "has_more": False
        # }

        # Get thread replies with pagination
        result = await list_thread_replies(
            channel="C1234567890",
            ts="1234567890.123456",
            limit=50,
            cursor="dGVhbTpDMDYxRkE1UEI="
        )

        # Get recent replies in time range
        result = await list_thread_replies(
            channel="C1234567890",
            ts="1234567890.123456",
            oldest="1609459200.000000",  # Jan 1, 2021
            latest="1612137600.000000",  # Feb 1, 2021
            inclusive=True
        )

        # Get only 10 most recent replies
        result = await list_thread_replies(
            channel="C1234567890",
            ts="1234567890.123456",
            limit=10
        )

    Notes:
        - Requires channels:history scope for public channels
        - Requires groups:history scope for private channels
        - Requires im:history scope for direct messages
        - Requires mpim:history scope for multi-party DMs
        - First message in response is always the parent message
        - All subsequent messages are replies in chronological order
        - Use cursor for pagination to get all replies in large threads
        - ts parameter is the thread_ts (parent message timestamp)
        - Returns error "channel_not_found" if channel doesn't exist
        - Returns error "thread_not_found" if ts doesn't point to valid thread
        - Returns error "not_in_channel" if bot/user not in channel
        - Messages include full details: text, user, reactions, files, etc.
        - Threads can have unlimited replies
        - Parent message has reply_count and reply_users fields
        - Useful for getting context of a conversation
        - Can filter by time range using oldest/latest
    """
    client = SlackAPIClient()

    # Build request parameters
    params: Dict[str, Any] = {
        "channel": channel,
        "ts": ts,  # Thread parent timestamp
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

    # Use GET method for conversations.replies
    return await client.get_method("conversations.replies", params)

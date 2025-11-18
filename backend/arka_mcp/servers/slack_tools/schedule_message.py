"""
Slack Schedule Message Tool.

Schedules a message to be sent at a specific time using chat.scheduleMessage.

Slack API Reference:
https://api.slack.com/methods/chat.scheduleMessage
"""
from typing import Dict, Any, Optional, List
from .client import SlackAPIClient


async def schedule_message(
    channel: str,
    post_at: int,
    text: Optional[str] = None,
    as_user: Optional[bool] = None,
    attachments: Optional[List[Dict[str, Any]]] = None,
    blocks: Optional[List[Dict[str, Any]]] = None,
    link_names: Optional[bool] = None,
    metadata: Optional[Dict[str, Any]] = None,
    parse: Optional[str] = None,
    reply_broadcast: Optional[bool] = None,
    thread_ts: Optional[str] = None,
    unfurl_links: Optional[bool] = None,
    unfurl_media: Optional[bool] = None
) -> Dict[str, Any]:
    """
    Schedule a message to be sent at a specific time.

    Args:
        channel: Channel ID to send to (e.g., "C1234567890")
        post_at: Unix timestamp when to post (e.g., 1609459200)
        text: Plain text message content
        as_user: Post as authed user (default: False)
        attachments: Legacy message attachments
        blocks: Block Kit blocks for rich formatting
        link_names: Link channel/user names (default: False)
        metadata: Message metadata
        parse: Parse mode ("full" or "none")
        reply_broadcast: Broadcast thread reply to channel
        thread_ts: Thread timestamp to reply to
        unfurl_links: Enable link unfurling
        unfurl_media: Enable media unfurling

    Returns:
        Dict containing:
        - ok: Success status
        - channel: Channel ID
        - scheduled_message_id: ID of scheduled message
        - post_at: Unix timestamp when message will be posted
        - message: Message object with preview

    Raises:
        ValueError: If Slack API returns an error

    Example:
        # Schedule message for 1 hour from now
        import time
        result = await schedule_message(
            channel="C1234567890",
            post_at=int(time.time()) + 3600,
            text="This is a scheduled message!"
        )
        # Returns: {"ok": True, "scheduled_message_id": "Q1234567890", ...}

        # Schedule with blocks
        result = await schedule_message(
            channel="C1234567890",
            post_at=1609459200,
            blocks=[
                {
                    "type": "section",
                    "text": {"type": "mrkdwn", "text": "*Reminder*: Meeting at 3 PM"}
                }
            ]
        )

        # Schedule thread reply
        result = await schedule_message(
            channel="C1234567890",
            post_at=1609459200,
            text="Follow-up message",
            thread_ts="1234567890.123456"
        )

    Notes:
        - Requires chat:write scope
        - post_at must be between 60 seconds and 120 days in the future
        - Scheduled messages can be cancelled using chat.deleteScheduledMessage
        - List scheduled messages with chat.scheduledMessages.list
        - If post_at is in the past, returns error "time_in_past"
        - Maximum 2500 scheduled messages per channel
        - Scheduled messages respect channel posting permissions
        - Either text or blocks must be provided
    """
    client = SlackAPIClient()

    params: Dict[str, Any] = {
        "channel": channel,
        "post_at": post_at
    }

    if text:
        params["text"] = text
    if as_user is not None:
        params["as_user"] = as_user
    if attachments:
        params["attachments"] = attachments
    if blocks:
        params["blocks"] = blocks
    if link_names is not None:
        params["link_names"] = link_names
    if metadata:
        params["metadata"] = metadata
    if parse:
        params["parse"] = parse
    if reply_broadcast is not None:
        params["reply_broadcast"] = reply_broadcast
    if thread_ts:
        params["thread_ts"] = thread_ts
    if unfurl_links is not None:
        params["unfurl_links"] = unfurl_links
    if unfurl_media is not None:
        params["unfurl_media"] = unfurl_media

    return await client.post("chat.scheduleMessage", params)

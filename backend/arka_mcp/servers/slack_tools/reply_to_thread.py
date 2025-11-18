"""
Slack Reply to Thread Tool.

Sends a reply to a message thread using chat.postMessage with thread_ts.

Slack API Reference:
https://api.slack.com/methods/chat.postMessage
https://api.slack.com/messaging/managing-threads
"""
from typing import Dict, Any, Optional, List
from .client import SlackAPIClient


async def reply_to_thread(
    channel: str,
    thread_ts: str,
    text: Optional[str] = None,
    blocks: Optional[List[Dict[str, Any]]] = None,
    attachments: Optional[List[Dict[str, Any]]] = None,
    reply_broadcast: Optional[bool] = False,
    unfurl_links: Optional[bool] = None,
    unfurl_media: Optional[bool] = None,
    link_names: Optional[bool] = None,
    mrkdwn: Optional[bool] = True,
    metadata: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Reply to a message thread in Slack.

    Args:
        channel: Channel ID where the thread is located (e.g., C1234567890)
        thread_ts: Timestamp of the parent message (creates thread reply) (e.g., "1234567890.123456")
        text: Plain text message content (required if blocks not provided)
        blocks: Structured Block Kit blocks (alternative to text)
        attachments: Legacy message attachments
        reply_broadcast: Also post reply to channel (not just in thread, default: False)
        unfurl_links: Enable unfurling of text-based content
        unfurl_media: Enable unfurling of media content
        link_names: Find and link channel names and usernames
        mrkdwn: Enable Slack markdown formatting (default: True)
        metadata: Message metadata object

    Returns:
        Dict containing:
        - ok: Success status
        - channel: Channel ID
        - ts: Timestamp of the reply message
        - message: Full message object with thread details

    Raises:
        ValueError: If Slack API returns an error

    Example:
        # Simple text reply to thread
        result = await reply_to_thread(
            channel="C1234567890",
            thread_ts="1234567890.123456",
            text="Thanks for the update!"
        )
        # Returns: {
        #   "ok": True,
        #   "channel": "C1234567890",
        #   "ts": "1234567890.789012",
        #   "message": {
        #     "text": "Thanks for the update!",
        #     "thread_ts": "1234567890.123456",
        #     ...
        #   }
        # }

        # Reply with formatting
        result = await reply_to_thread(
            channel="C1234567890",
            thread_ts="1234567890.123456",
            text="*Important:* This is a critical update! :warning:",
            mrkdwn=True
        )

        # Reply with Block Kit
        result = await reply_to_thread(
            channel="C1234567890",
            thread_ts="1234567890.123456",
            blocks=[
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "*Status Update:* Task completed successfully :white_check_mark:"
                    }
                }
            ]
        )

        # Reply and broadcast to channel (makes reply visible outside thread)
        result = await reply_to_thread(
            channel="C1234567890",
            thread_ts="1234567890.123456",
            text="IMPORTANT: Everyone should see this update",
            reply_broadcast=True
        )

        # Reply with user mentions
        result = await reply_to_thread(
            channel="C1234567890",
            thread_ts="1234567890.123456",
            text="Hey @john, can you take a look at this?",
            link_names=True
        )

    Notes:
        - Requires chat:write scope
        - thread_ts must be the timestamp of the parent message (first message in thread)
        - To reply to a reply, still use the parent's thread_ts, not the reply's ts
        - reply_broadcast makes the reply visible in main channel (not just thread)
        - If thread doesn't exist, creates new thread with this as first reply
        - Thread replies show "X replies" indicator on parent message
        - Users subscribed to thread get notified of new replies
        - Must provide either text or blocks (or both)
        - Block Kit is recommended over attachments for rich formatting
        - Max text length: 40,000 characters
        - Max 50 blocks per message
        - Threads can have unlimited replies
        - Returns error "channel_not_found" if channel doesn't exist
        - Returns error "thread_not_found" if thread_ts doesn't exist
        - Returns error "msg_too_long" if text exceeds limit
        - Link names converts @username and #channel to mentions
        - Markdown formatting: *bold*, _italic_, ~strike~, `code`, ```preformatted```
        - User is automatically subscribed to threads they reply to
    """
    client = SlackAPIClient()

    # Build request parameters
    params: Dict[str, Any] = {
        "channel": channel,
        "thread_ts": thread_ts  # This makes it a thread reply
    }

    # Either text or blocks must be provided
    if text is not None:
        params["text"] = text
    if blocks is not None:
        params["blocks"] = blocks
    if attachments is not None:
        params["attachments"] = attachments
    if reply_broadcast is not None:
        params["reply_broadcast"] = reply_broadcast
    if unfurl_links is not None:
        params["unfurl_links"] = unfurl_links
    if unfurl_media is not None:
        params["unfurl_media"] = unfurl_media
    if link_names is not None:
        params["link_names"] = link_names
    if mrkdwn is not None:
        params["mrkdwn"] = mrkdwn
    if metadata is not None:
        params["metadata"] = metadata

    # Use POST method for chat.postMessage
    return await client.call_method("chat.postMessage", params)

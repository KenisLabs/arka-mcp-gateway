"""
Slack Update Message Tool.

Updates/edits a Slack message using chat.update.

Slack API Reference:
https://api.slack.com/methods/chat.update
"""
from typing import Dict, Any, Optional, List
from .client import SlackAPIClient


async def update_message(
    channel: str,
    ts: str,
    text: Optional[str] = None,
    blocks: Optional[List[Dict[str, Any]]] = None,
    attachments: Optional[List[Dict[str, Any]]] = None,
    as_user: Optional[bool] = None,
    link_names: Optional[bool] = None,
    parse: Optional[str] = None,
    reply_broadcast: Optional[bool] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Update/edit a Slack message.

    Args:
        channel: Channel ID containing the message (e.g., C1234567890)
        ts: Timestamp of the message to update (e.g., "1234567890.123456")
        text: New plain text message content (required if blocks not provided)
        blocks: Structured Block Kit blocks (alternative to text)
        attachments: Legacy message attachments
        as_user: Update as the authed user (bot apps should use False)
        link_names: Find and link channel names and usernames (default: True)
        parse: Change parsing mode ("full", "none", default: "full")
        reply_broadcast: Broadcast to channel if updating thread reply
        metadata: Message metadata object

    Returns:
        Dict containing:
        - ok: Success status
        - channel: Channel ID
        - ts: Timestamp of updated message
        - text: Updated message text
        - message: Updated message object with full details

    Raises:
        ValueError: If Slack API returns an error

    Example:
        # Update message text
        result = await update_message(
            channel="C1234567890",
            ts="1234567890.123456",
            text="Updated message content"
        )
        # Returns: {
        #   "ok": True,
        #   "channel": "C1234567890",
        #   "ts": "1234567890.123456",
        #   "text": "Updated message content",
        #   "message": {...}
        # }

        # Update with Block Kit
        result = await update_message(
            channel="C1234567890",
            ts="1234567890.123456",
            blocks=[
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "*Updated* message with formatting"
                    }
                }
            ]
        )

        # Update thread reply and broadcast to channel
        result = await update_message(
            channel="C1234567890",
            ts="1234567890.123456",
            text="Important update!",
            reply_broadcast=True
        )

        # Update with link detection
        result = await update_message(
            channel="C1234567890",
            ts="1234567890.123456",
            text="Hey @john check #general channel",
            link_names=True
        )

    Notes:
        - Requires chat:write scope
        - Can only update messages sent by the authenticated bot/user
        - Must provide either text or blocks (or both)
        - Message shows "(edited)" indicator after update
        - Cannot update messages older than 5 years
        - Returns error "message_not_found" if ts doesn't exist
        - Returns error "cant_update_message" if not message author
        - Returns error "edit_window_closed" if message too old
        - Returns error "is_archived" if channel is archived
        - Returns error "msg_too_long" if text exceeds 40,000 characters
        - Blocks are recommended over attachments for new messages
        - Link names converts @username to user mentions automatically
        - Parse mode affects how text is interpreted (markdown, etc.)
        - reply_broadcast allows editing thread replies to show in main channel
        - Metadata can be used for app-specific data attached to message
    """
    client = SlackAPIClient()

    # Build request parameters
    params: Dict[str, Any] = {
        "channel": channel,
        "ts": ts
    }

    # Either text or blocks must be provided
    if text is not None:
        params["text"] = text
    if blocks is not None:
        params["blocks"] = blocks
    if attachments is not None:
        params["attachments"] = attachments
    if as_user is not None:
        params["as_user"] = as_user
    if link_names is not None:
        params["link_names"] = link_names
    if parse is not None:
        params["parse"] = parse
    if reply_broadcast is not None:
        params["reply_broadcast"] = reply_broadcast
    if metadata is not None:
        params["metadata"] = metadata

    # Use POST method for chat.update
    return await client.call_method("chat.update", params)

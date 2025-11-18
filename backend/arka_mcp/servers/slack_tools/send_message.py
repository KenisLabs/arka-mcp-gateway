"""
Slack Send Message Tool.

Sends a message to a Slack channel, group, or DM using chat.postMessage.

Slack API Reference:
https://api.slack.com/methods/chat.postMessage
"""
from typing import Dict, Any, Optional, List
from .client import SlackAPIClient


async def send_message(
    channel: str,
    text: Optional[str] = None,
    markdown_text: Optional[str] = None,
    thread_ts: Optional[str] = None,
    reply_broadcast: Optional[bool] = None,
    username: Optional[str] = None,
    icon_emoji: Optional[str] = None,
    icon_url: Optional[str] = None,
    link_names: Optional[bool] = None,
    unfurl_links: Optional[bool] = None,
    unfurl_media: Optional[bool] = None,
    parse: Optional[str] = None,
    attachments: Optional[List[Dict[str, Any]]] = None,
    blocks: Optional[List[Dict[str, Any]]] = None,
    metadata: Optional[Dict[str, Any]] = None,
    as_user: Optional[bool] = None
) -> Dict[str, Any]:
    """
    Send a message to a Slack channel.

    Args:
        channel: Channel, private group, or DM channel ID (e.g., C1234567890, D1234567890)
        text: Plain text message (required unless blocks or attachments provided)
        markdown_text: Markdown formatted message (alternative to text)
        thread_ts: Timestamp of parent message to reply in thread
        reply_broadcast: Broadcast thread reply to channel (default: false)
        username: Bot username override (requires chat:write.customize scope)
        icon_emoji: Bot icon emoji override (e.g., :chart_with_upwards_trend:)
        icon_url: Bot icon URL override
        link_names: Find and link @mentions and #channels
        unfurl_links: Enable link unfurling (default: true)
        unfurl_media: Enable media unfurling (default: true)
        parse: How to parse text (none, full)
        attachments: Legacy message attachments (secondary content blocks)
        blocks: Block Kit blocks (rich message formatting)
        metadata: Message metadata (invisible to users)
        as_user: Post as authenticated user (legacy, deprecated)

    Returns:
        Dict containing:
        - ok: Success status
        - channel: Channel ID where message was posted
        - ts: Timestamp of the message
        - message: Complete message object

    Raises:
        ValueError: If Slack API returns an error

    Example:
        result = await send_message(
            channel="C1234567890",
            text="Hello from MCP Gateway!",
            thread_ts="1234567890.123456"
        )
        # Returns: {"ok": True, "channel": "C1234567890", "ts": "1234567890.654321", ...}

    Notes:
        - Either text, markdown_text, blocks, or attachments must be provided
        - markdown_text uses Slack's mrkdwn format (similar to Markdown)
        - Use blocks for rich interactive messages (buttons, images, etc.)
        - thread_ts must be a valid message timestamp from the channel
    """
    client = SlackAPIClient()

    # Build request parameters
    params: Dict[str, Any] = {
        "channel": channel,
    }

    # Handle text content (prioritize markdown_text over text)
    if markdown_text:
        params["text"] = markdown_text
        params["mrkdwn"] = True
    elif text:
        params["text"] = text

    # Optional parameters
    if thread_ts is not None:
        params["thread_ts"] = thread_ts
    if reply_broadcast is not None:
        params["reply_broadcast"] = reply_broadcast
    if username is not None:
        params["username"] = username
    if icon_emoji is not None:
        params["icon_emoji"] = icon_emoji
    if icon_url is not None:
        params["icon_url"] = icon_url
    if link_names is not None:
        params["link_names"] = link_names
    if unfurl_links is not None:
        params["unfurl_links"] = unfurl_links
    if unfurl_media is not None:
        params["unfurl_media"] = unfurl_media
    if parse is not None:
        params["parse"] = parse
    if attachments is not None:
        params["attachments"] = attachments
    if blocks is not None:
        params["blocks"] = blocks
    if metadata is not None:
        params["metadata"] = metadata
    if as_user is not None:
        params["as_user"] = as_user

    # Make API call
    return await client.call_method("chat.postMessage", params)

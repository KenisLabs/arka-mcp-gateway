"""
Slack List Pins Tool.

Lists all pinned items in a channel using pins.list.

Slack API Reference:
https://api.slack.com/methods/pins.list
"""
from typing import Dict, Any
from .client import SlackAPIClient


async def list_pins(
    channel: str
) -> Dict[str, Any]:
    """
    List all pinned items in a Slack channel.

    Args:
        channel: Channel ID to list pins from (e.g., C1234567890)

    Returns:
        Dict containing:
        - ok: Success status
        - items: Array of pinned items, each containing:
          - type: Type of pinned item ("message", "file", "file_comment")
          - channel: Channel ID
          - created: Unix timestamp when pinned
          - created_by: User ID who pinned the item
          - message: Message object (if type is "message") with:
            - type: "message"
            - user: User ID who posted
            - text: Message text
            - ts: Message timestamp
            - thread_ts: Thread timestamp (if in thread)
            - reactions: Array of reactions
            - files: Array of attached files
            - permalink: Permanent link to message
          - file: File object (if type is "file") with:
            - id: File ID
            - name: Filename
            - title: File title
            - mimetype: MIME type
            - filetype: File type
            - url_private: Private download URL
            - permalink: Permanent link to file
          - comment: Comment object (if type is "file_comment")

    Raises:
        ValueError: If Slack API returns an error

    Example:
        # List all pins in a channel
        result = await list_pins(
            channel="C1234567890"
        )
        # Returns: {
        #   "ok": True,
        #   "items": [
        #     {
        #       "type": "message",
        #       "channel": "C1234567890",
        #       "created": 1234567890,
        #       "created_by": "U1234567890",
        #       "message": {
        #         "type": "message",
        #         "user": "U2222222222",
        #         "text": "Important announcement: New feature released!",
        #         "ts": "1234567890.123456",
        #         "permalink": "https://workspace.slack.com/archives/C1234/p1234567890123456",
        #         "reactions": [
        #           {"name": "tada", "count": 5}
        #         ]
        #       }
        #     },
        #     {
        #       "type": "file",
        #       "channel": "C1234567890",
        #       "created": 1234567800,
        #       "created_by": "U3333333333",
        #       "file": {
        #         "id": "F1234567890",
        #         "name": "project_timeline.pdf",
        #         "title": "Q1 Project Timeline",
        #         "mimetype": "application/pdf",
        #         "filetype": "pdf",
        #         "url_private": "https://files.slack.com/files-pri/...",
        #         "permalink": "https://workspace.slack.com/files/..."
        #       }
        #     },
        #     {
        #       "type": "message",
        #       "channel": "C1234567890",
        #       "created": 1234567700,
        #       "created_by": "U4444444444",
        #       "message": {
        #         "type": "message",
        #         "user": "U5555555555",
        #         "text": "Meeting notes from today's standup",
        #         "ts": "1234567700.123456",
        #         "thread_ts": "1234567700.123456",
        #         "reply_count": 8,
        #         "permalink": "https://workspace.slack.com/archives/C1234/p1234567700123456"
        #       }
        #     }
        #   ]
        # }

        # List pins in private channel
        result = await list_pins(
            channel="G1234567890"
        )

        # List pins in DM
        result = await list_pins(
            channel="D1234567890"
        )

    Notes:
        - Requires pins:read scope
        - Bot/user must be a member of the channel
        - Returns all pinned items in chronological order (newest first)
        - Maximum 100 pinned items per channel
        - Returns error "channel_not_found" if channel doesn't exist
        - Returns error "not_in_channel" if bot/user not in channel
        - Returns error "is_archived" if channel is archived
        - Pinned items include messages, files, and file comments
        - Each item shows who pinned it and when
        - Messages include full content and metadata
        - Files include download URLs and details
        - Permalink provides direct link to original item
        - Pins persist even if original message/file is deleted
        - Useful for finding important channel information
        - Can be used to create channel documentation overview
        - Thread parent messages can be pinned
        - Thread replies can also be pinned separately
        - Reactions on pinned messages are included
    """
    client = SlackAPIClient()

    # Build request parameters
    params: Dict[str, Any] = {
        "channel": channel
    }

    # Use GET method for pins.list
    return await client.get_method("pins.list", params)

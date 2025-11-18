"""
Move a Gmail message to trash.

Implements the GMAIL_MOVE_TO_TRASH tool specification from gmail.md.

Security features:
- Input validation with Pydantic
- Authenticated via worker_context OAuth tokens
- Validates message_id format
"""
from typing import Dict, Any
from arka_mcp.servers.gmail_tools.client import GmailAPIClient
from arka_mcp.servers.gmail_tools.models import MoveToTrashRequest


async def move_to_trash(message_id: str, user_id: str = "me") -> Dict[str, Any]:
    """
    Move an existing email message to trash.

    Messages in trash are automatically deleted after 30 days.

    Args:
        message_id: ID of the message to trash (required)
        user_id: User's email address or 'me' (default: 'me')

    Returns:
        Dict containing the updated message with TRASH label

    Example:
        result = await move_to_trash(message_id="1875f42779f726f2")

    Gmail API Reference:
        https://developers.google.com/gmail/api/reference/rest/v1/users.messages/trash
    """
    # Validate input
    request = MoveToTrashRequest(message_id=message_id, user_id=user_id)

    # Make API request
    client = GmailAPIClient()
    return await client.post(
        f"/users/{request.user_id}/messages/{request.message_id}/trash",
        {}
    )

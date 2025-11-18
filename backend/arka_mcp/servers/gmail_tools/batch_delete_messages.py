"""
Permanently delete multiple Gmail messages in bulk.

Implements the GMAIL_BATCH_DELETE_MESSAGES tool specification from gmail.md.

Security features:
- Input validation with Pydantic
- Authenticated via worker_context OAuth tokens
- Validates all message IDs
"""
from typing import Dict, Any, List
from arka_mcp.servers.gmail_tools.client import GmailAPIClient
from arka_mcp.servers.gmail_tools.models import BatchDeleteMessagesRequest


async def batch_delete_messages(
    ids: List[str],
    userId: str = "me"
) -> Dict[str, Any]:
    """
    Permanently delete multiple Gmail messages in bulk.

    WARNING: This operation cannot be undone. Deleted messages are permanently removed.

    Args:
        ids: List of message IDs to delete (required)
        userId: User's email address or 'me' (default: 'me')

    Returns:
        Empty dict on success

    Example:
        await batch_delete_messages(
            ids=["18c5f5d1a2b3c4d5", "18c5f5d1a2b3c4d6"]
        )

    Gmail API Reference:
        https://developers.google.com/gmail/api/reference/rest/v1/users.messages/batchDelete
    """
    # Validate input
    request = BatchDeleteMessagesRequest(ids=ids, userId=userId)

    # Build request body
    body = {"ids": request.ids}

    # Make API request
    client = GmailAPIClient()
    return await client.post(f"/users/{request.userId}/messages/batchDelete", body)

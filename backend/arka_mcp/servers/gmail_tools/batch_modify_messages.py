"""
Batch modify labels on multiple Gmail messages.

Implements the GMAIL_BATCH_MODIFY_MESSAGES tool specification from gmail.md.

Security features:
- Input validation with Pydantic
- Authenticated via worker_context OAuth tokens
- Validates up to 1000 message IDs
"""
from typing import Dict, Any, List, Optional
from arka_mcp.servers.gmail_tools.client import GmailAPIClient
from arka_mcp.servers.gmail_tools.models import BatchModifyMessagesRequest


async def batch_modify_messages(
    messageIds: List[str],
    addLabelIds: Optional[List[str]] = None,
    removeLabelIds: Optional[List[str]] = None,
    userId: str = "me"
) -> Dict[str, Any]:
    """
    Modify labels on multiple Gmail messages in one efficient API call.

    Supports up to 1,000 messages per request for bulk operations like
    archiving, marking as read/unread, or applying custom labels.

    Args:
        messageIds: List of message IDs to modify (1-1000 messages)
        addLabelIds: Label IDs to add (e.g., ['INBOX', 'STARRED'])
        removeLabelIds: Label IDs to remove (e.g., ['UNREAD'])
        userId: User's email address or 'me' (default: 'me')

    Returns:
        Empty dict on success

    Example:
        # Mark multiple messages as read
        await batch_modify_messages(
            messageIds=["msg1", "msg2", "msg3"],
            removeLabelIds=["UNREAD"]
        )

        # Archive and star messages
        await batch_modify_messages(
            messageIds=["msg1", "msg2"],
            addLabelIds=["STARRED"],
            removeLabelIds=["INBOX"]
        )

    Gmail API Reference:
        https://developers.google.com/gmail/api/reference/rest/v1/users.messages/batchModify
    """
    # Validate input
    request = BatchModifyMessagesRequest(
        messageIds=messageIds,
        addLabelIds=addLabelIds,
        removeLabelIds=removeLabelIds,
        userId=userId
    )

    # Build request body
    body = {"ids": request.messageIds}

    if request.addLabelIds:
        body["addLabelIds"] = request.addLabelIds

    if request.removeLabelIds:
        body["removeLabelIds"] = request.removeLabelIds

    # Make API request
    client = GmailAPIClient()
    return await client.post(f"/users/{request.userId}/messages/batchModify", body)

"""
Add and/or remove Gmail labels from an email message.

Implements the GMAIL_ADD_LABEL_TO_EMAIL tool specification from gmail.md.

Security features:
- Input validation with Pydantic (message_id, label_ids)
- Authenticated via worker_context OAuth tokens
- Audit logging
- Error sanitization
"""
from typing import Dict, Any, List, Optional
from arka_mcp.servers.gmail_tools.client import GmailAPIClient
from arka_mcp.servers.gmail_tools.models import AddLabelToEmailRequest


async def add_label_to_email(
    message_id: str,
    add_label_ids: Optional[List[str]] = None,
    remove_label_ids: Optional[List[str]] = None,
    user_id: str = "me"
) -> Dict[str, Any]:
    """
    Add and/or remove specified Gmail labels for a message.

    Modifies the labels on a specific email message. Can add new labels,
    remove existing labels, or both in a single operation.

    Args:
        message_id: Immutable ID of the message to modify (required)
        add_label_ids: Label IDs to add (default: [])
            - For system labels: "INBOX", "STARRED", "IMPORTANT", etc.
            - For custom labels: Use label ID from list_labels (e.g., "Label_123")
            - Cannot add immutable labels like "DRAFT" or "SENT"
        remove_label_ids: Label IDs to remove (default: [])
            - For system labels: "UNREAD", "SPAM", etc.
            - For custom labels: Use label ID from list_labels
            - Cannot remove immutable labels like "DRAFT" or "SENT"
        user_id: User's email address or 'me' for authenticated user (default: 'me')

    Returns:
        Dict containing updated message with modified labelIds

    Example usage:
        # Mark message as starred and important
        await add_label_to_email(
            message_id="17f1b2b9c1b2a3d4",
            add_label_ids=["STARRED", "IMPORTANT"]
        )

        # Mark as read (remove UNREAD label)
        await add_label_to_email(
            message_id="17f1b2b9c1b2a3d4",
            remove_label_ids=["UNREAD"]
        )

        # Move from inbox to archive (remove INBOX)
        await add_label_to_email(
            message_id="17f1b2b9c1b2a3d4",
            remove_label_ids=["INBOX"]
        )

    Gmail API Reference:
        https://developers.google.com/gmail/api/reference/rest/v1/users.messages/modify

    Notes:
        - Ensure message_id is valid (obtain from fetch_emails or other tools)
        - Use list_labels to get custom label IDs
        - System labels have specific names: INBOX, SPAM, TRASH, UNREAD, STARRED, IMPORTANT
        - Some system labels are immutable (DRAFT, SENT) and cannot be modified via messages.modify
    """
    # Validate inputs
    request = AddLabelToEmailRequest(
        message_id=message_id,
        add_label_ids=add_label_ids or [],
        remove_label_ids=remove_label_ids or [],
        user_id=user_id
    )

    # Build request body
    modify_request = {}
    if request.add_label_ids:
        modify_request["addLabelIds"] = request.add_label_ids
    if request.remove_label_ids:
        modify_request["removeLabelIds"] = request.remove_label_ids

    # Make API request
    client = GmailAPIClient()
    return await client.post(
        f"/users/{request.user_id}/messages/{request.message_id}/modify",
        modify_request
    )

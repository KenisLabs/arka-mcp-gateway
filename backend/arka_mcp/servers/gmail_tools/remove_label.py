"""
Permanently delete a Gmail label.

Implements the GMAIL_REMOVE_LABEL tool specification from gmail.md.

Security features:
- Input validation with Pydantic
- Authenticated via worker_context OAuth tokens
- Validates label_id format
"""
from typing import Dict, Any
from arka_mcp.servers.gmail_tools.client import GmailAPIClient
from arka_mcp.servers.gmail_tools.models import RemoveLabelRequest


async def remove_label(label_id: str, user_id: str = "me") -> Dict[str, Any]:
    """
    Permanently delete a specific user-created Gmail label.

    Cannot delete system labels (INBOX, SENT, DRAFT, etc.).

    Args:
        label_id: ID of the label to delete (required)
            - Must be a user-created label ID (e.g., "Label_123")
            - Cannot be a system label
        user_id: User's email address or 'me' (default: 'me')

    Returns:
        Empty dict on successful deletion

    Example:
        await remove_label(label_id="Label_123")

    Gmail API Reference:
        https://developers.google.com/gmail/api/reference/rest/v1/users.labels/delete
    """
    # Validate input
    request = RemoveLabelRequest(label_id=label_id, user_id=user_id)

    # Make API request
    client = GmailAPIClient()
    return await client.delete(f"/users/{request.user_id}/labels/{request.label_id}")

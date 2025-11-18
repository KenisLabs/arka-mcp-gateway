"""
List all Gmail labels for the authenticated user.

Security features:
- Input validation with Pydantic
- Authenticated via worker_context OAuth tokens
- Audit logging
- Error sanitization
"""
from typing import Dict, Any
from arka_mcp.servers.gmail_tools.client import GmailAPIClient
from arka_mcp.servers.gmail_tools.models import ListLabelsRequest


async def list_labels(user_id: str = "me") -> Dict[str, Any]:
    """
    List all Gmail labels for the authenticated user.

    Returns labels including both system labels (INBOX, STARRED, etc.)
    and user-created custom labels.

    Args:
        user_id: User's email address or 'me' for authenticated user (default: 'me')

    Returns:
        Dict containing:
        - labels: List of label objects with id, name, type, etc.

    Example response:
        {
            "labels": [
                {
                    "id": "INBOX",
                    "name": "INBOX",
                    "type": "system"
                },
                {
                    "id": "Label_123",
                    "name": "Important",
                    "type": "user"
                }
            ]
        }

    Gmail API Reference:
        https://developers.google.com/gmail/api/reference/rest/v1/users.labels/list
    """
    # Validate input
    request = ListLabelsRequest(user_id=user_id)

    # Make API request
    client = GmailAPIClient()
    return await client.get(f"/users/{request.user_id}/labels")

"""
Permanently delete a specific Gmail draft.

Implements the GMAIL_DELETE_DRAFT tool specification from gmail.md.

Security features:
- Input validation with Pydantic
- Authenticated via worker_context OAuth tokens
- Validates draft_id format
"""
from typing import Dict, Any
from arka_mcp.servers.gmail_tools.client import GmailAPIClient
from arka_mcp.servers.gmail_tools.models import DeleteDraftRequest


async def delete_draft(draft_id: str, user_id: str = "me") -> Dict[str, Any]:
    """
    Permanently delete a specific Gmail draft using its ID.

    Ensure the draft exists and the user has necessary permissions.

    Args:
        draft_id: Immutable ID of the draft to delete (required)
        user_id: User's email address or 'me' (default: 'me')

    Returns:
        Empty dict on successful deletion

    Example:
        await delete_draft(draft_id="r-8388446164079304564")

    Gmail API Reference:
        https://developers.google.com/gmail/api/reference/rest/v1/users.drafts/delete
    """
    # Validate input
    request = DeleteDraftRequest(draft_id=draft_id, user_id=user_id)

    # Make API request
    client = GmailAPIClient()
    return await client.delete(f"/users/{request.user_id}/drafts/{request.draft_id}")

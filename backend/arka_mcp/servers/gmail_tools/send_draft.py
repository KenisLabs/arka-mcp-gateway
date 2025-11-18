"""
Send an existing Gmail draft.

Implements the GMAIL_SEND_DRAFT tool specification from gmail.md.

Security features:
- Input validation with Pydantic
- Authenticated via worker_context OAuth tokens
- Validates draft_id format
"""
from typing import Dict, Any
from arka_mcp.servers.gmail_tools.client import GmailAPIClient
from arka_mcp.servers.gmail_tools.models import SendDraftRequest


async def send_draft(draft_id: str, user_id: str = "me") -> Dict[str, Any]:
    """
    Send the specified, existing draft to the recipients in the To, Cc, and Bcc headers.

    Args:
        draft_id: The ID of the draft to send (required)
            - Make sure the draft ID is valid and not a placeholder
            - Use list_drafts to get the draft ID if you don't have it
        user_id: User's email address or 'me' (default: 'me')

    Returns:
        Dict containing the sent message details

    Example:
        result = await send_draft(draft_id="r-xxxxxxxxxxxxxxxxx")

    Gmail API Reference:
        https://developers.google.com/gmail/api/reference/rest/v1/users.drafts/send
    """
    # Validate input
    request = SendDraftRequest(draft_id=draft_id, user_id=user_id)

    # Build request body
    body = {"id": request.draft_id}

    # Make API request
    client = GmailAPIClient()
    return await client.post(f"/users/{request.user_id}/drafts/send", body)

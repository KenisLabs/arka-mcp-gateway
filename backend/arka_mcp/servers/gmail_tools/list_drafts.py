"""
Retrieve a paginated list of email drafts from Gmail.

Implements the GMAIL_LIST_DRAFTS tool specification from gmail.md.

Security features:
- Input validation with Pydantic
- Authenticated via worker_context OAuth tokens
- Support for pagination
"""
from typing import Dict, Any
from arka_mcp.servers.gmail_tools.client import GmailAPIClient
from arka_mcp.servers.gmail_tools.models import ListDraftsRequest


async def list_drafts(
    user_id: str = "me",
    max_results: int = 1,
    page_token: str = "",
    verbose: bool = False
) -> Dict[str, Any]:
    """
    Retrieve a paginated list of email drafts from a user's Gmail account.

    Use verbose=true to get full draft details including subject, body, sender, and timestamp.

    Args:
        user_id: User's mailbox ID or 'me' (default: 'me')
        max_results: Maximum number of drafts to return per page (1-500, default: 1)
        page_token: Token from previous response to retrieve specific page
        verbose: If true, fetches full draft details; if false, returns only draft IDs (default: false)

    Returns:
        Dict containing drafts and pagination info

    Example:
        # List all drafts with full details
        drafts = await list_drafts(
            max_results=100,
            verbose=True
        )

    Gmail API Reference:
        https://developers.google.com/gmail/api/reference/rest/v1/users.drafts/list
    """
    # Validate input
    request = ListDraftsRequest(
        user_id=user_id,
        max_results=max_results,
        page_token=page_token,
        verbose=verbose
    )

    # Build query parameters
    params = {"maxResults": request.max_results}

    if request.page_token:
        params["pageToken"] = request.page_token

    # Make API request
    client = GmailAPIClient()
    return await client.get(f"/users/{request.user_id}/drafts", params)

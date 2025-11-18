"""
Fetch emails from Gmail with filtering and pagination support.

Implements the GMAIL_FETCH_EMAILS tool specification from gmail.md.

Security features:
- Input validation with Pydantic
- Authenticated via worker_context OAuth tokens
- Support for pagination and filtering
"""
from typing import Dict, Any, Optional, List
from arka_mcp.servers.gmail_tools.client import GmailAPIClient
from arka_mcp.servers.gmail_tools.models import FetchEmailsRequest


async def fetch_emails(
    user_id: str = "me",
    max_results: int = 1,
    label_ids: Optional[List[str]] = None,
    query: Optional[str] = None,
    page_token: Optional[str] = None,
    include_spam_trash: bool = False,
    include_payload: bool = True,
    ids_only: bool = False,
    verbose: bool = True
) -> Dict[str, Any]:
    """
    Fetch a list of email messages from Gmail account.

    Supports filtering by labels, search queries, and pagination.

    Args:
        user_id: User's email address or 'me' (default: 'me')
        max_results: Maximum number of messages to return (1-500, default: 1)
        label_ids: Filter by label IDs (e.g., ['INBOX', 'UNREAD'])
        query: Gmail search query (e.g., 'from:user@example.com is:unread')
        page_token: Token for retrieving next page of results
        include_spam_trash: Include messages from SPAM and TRASH
        include_payload: Include full message payload
        ids_only: Return only message IDs (fastest)
        verbose: Return detailed message information

    Returns:
        Dict containing messages and pagination info

    Example:
        # Fetch unread emails from inbox
        emails = await fetch_emails(
            query="is:unread",
            label_ids=["INBOX"],
            max_results=10
        )

    Gmail API Reference:
        https://developers.google.com/gmail/api/reference/rest/v1/users.messages/list
    """
    # Validate input
    request = FetchEmailsRequest(
        user_id=user_id,
        max_results=max_results,
        label_ids=label_ids,
        query=query,
        page_token=page_token,
        include_spam_trash=include_spam_trash,
        include_payload=include_payload,
        ids_only=ids_only,
        verbose=verbose
    )

    # Build query parameters
    params = {
        "maxResults": request.max_results,
        "includeSpamTrash": request.include_spam_trash
    }

    if request.label_ids:
        params["labelIds"] = request.label_ids

    if request.query:
        params["q"] = request.query

    if request.page_token:
        params["pageToken"] = request.page_token

    # Make API request
    client = GmailAPIClient()
    return await client.get(f"/users/{request.user_id}/messages", params)

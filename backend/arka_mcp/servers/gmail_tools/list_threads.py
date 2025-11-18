"""
List email threads from a Gmail account with filtering and pagination.

Implements the GMAIL_LIST_THREADS tool specification from gmail.md.

Security features:
- Input validation with Pydantic
- Authenticated via worker_context OAuth tokens
- Support for search queries and pagination
"""
from typing import Dict, Any
from arka_mcp.servers.gmail_tools.client import GmailAPIClient
from arka_mcp.servers.gmail_tools.models import ListThreadsRequest


async def list_threads(
    user_id: str = "me",
    max_results: int = 10,
    query: str = "",
    page_token: str = "",
    verbose: bool = False
) -> Dict[str, Any]:
    """
    Retrieve a list of email threads from a Gmail account.

    Supports filtering and pagination.

    Args:
        user_id: User's email address or 'me' (default: 'me')
        max_results: Maximum number of threads to return (1-500, default: 10)
        query: Filter using Gmail search query syntax (e.g., 'from:user@example.com is:unread')
        page_token: Token from previous response to retrieve specific page
        verbose: If true, returns threads with complete message details (default: false)

    Returns:
        Dict containing threads and pagination info

    Example:
        # List unread threads
        threads = await list_threads(
            query="is:unread",
            max_results=50
        )

    Gmail API Reference:
        https://developers.google.com/gmail/api/reference/rest/v1/users.threads/list
    """
    # Validate input
    request = ListThreadsRequest(
        user_id=user_id,
        max_results=max_results,
        query=query,
        page_token=page_token,
        verbose=verbose
    )

    # Build query parameters
    params = {"maxResults": request.max_results}

    if request.query:
        params["q"] = request.query

    if request.page_token:
        params["pageToken"] = request.page_token

    # Make API request
    client = GmailAPIClient()
    return await client.get(f"/users/{request.user_id}/threads", params)

"""
List Gmail mailbox change history since a known startHistoryId.

Implements the GMAIL_LIST_HISTORY tool specification from gmail.md.
(Note: This appears to be a duplicate of history_list in the spec)

Security features:
- Input validation with Pydantic
- Authenticated via worker_context OAuth tokens
"""
from typing import Dict, Any, Optional, List
from arka_mcp.servers.gmail_tools.client import GmailAPIClient
from arka_mcp.servers.gmail_tools.models import HistoryListRequest


async def list_history(
    start_history_id: str,
    user_id: str = "me",
    max_results: int = 100,
    page_token: Optional[str] = None,
    label_id: Optional[str] = None,
    history_types: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    List Gmail mailbox change history since a known startHistoryId.

    Use when performing incremental mailbox syncs to fetch only new changes.

    Args:
        start_history_id: Returns history records after this ID (required)
            - If the ID is invalid or too old, the API returns 404
            - Perform a full sync in that case
        user_id: User's email address or 'me' (default: 'me')
        max_results: Maximum number of history records to return (default: 100, max: 500)
        page_token: Token to retrieve a specific page of results
        label_id: Only return history records involving messages with this label ID
        history_types: Filter by specific history types
            - Allowed values: messageAdded, messageDeleted, labelAdded, labelRemoved

    Returns:
        Dict containing history records and pagination info

    Example:
        history = await list_history(
            start_history_id="1234567890",
            history_types=["messageAdded", "labelRemoved"]
        )

    Gmail API Reference:
        https://developers.google.com/gmail/api/reference/rest/v1/users.history/list
    """
    # Validate input
    request = HistoryListRequest(
        startHistoryId=start_history_id,
        user_id=user_id,
        maxResults=max_results,
        pageToken=page_token,
        labelId=label_id,
        historyTypes=history_types
    )

    # Build query parameters
    params = {
        "startHistoryId": request.startHistoryId,
        "maxResults": request.maxResults
    }

    if request.pageToken:
        params["pageToken"] = request.pageToken

    if request.labelId:
        params["labelId"] = request.labelId

    if request.historyTypes:
        params["historyTypes"] = request.historyTypes

    # Make API request
    client = GmailAPIClient()
    return await client.get(f"/users/{request.user_id}/history", params)

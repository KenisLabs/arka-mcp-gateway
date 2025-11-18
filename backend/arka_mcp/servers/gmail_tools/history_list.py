"""
List Gmail mailbox history changes since a startHistoryId.

Implements the GMAIL_HISTORY_LIST tool specification from gmail.md.

Security features:
- Input validation with Pydantic
- Authenticated via worker_context OAuth tokens
"""
from typing import Dict, Any, Optional, List
from arka_mcp.servers.gmail_tools.client import GmailAPIClient
from arka_mcp.servers.gmail_tools.models import HistoryListRequest


async def history_list(
    startHistoryId: str,
    user_id: str = "me",
    maxResults: Optional[int] = None,
    pageToken: Optional[str] = None,
    labelId: Optional[str] = None,
    historyTypes: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Fetch Gmail mailbox history changes since a startHistoryId.

    Use when performing reliable incremental syncs by supplying the last seen historyId.

    Args:
        startHistoryId: Return history records after this ID (required)
            - If invalid or too old, the API returns 404 and a full sync is needed
        user_id: User's email address or 'me' (default: 'me')
        maxResults: Maximum number of history records to return (default: 100 if unspecified)
        pageToken: Token to retrieve a specific page of results
        labelId: Only return messages with the specified label ID
        historyTypes: Filter by history record types
            - Allowed values: messageAdded, messageDeleted, labelAdded, labelRemoved

    Returns:
        Dict containing history records and pagination info

    Example:
        history = await history_list(
            startHistoryId="1234567890",
            historyTypes=["messageAdded", "labelRemoved"]
        )

    Gmail API Reference:
        https://developers.google.com/gmail/api/reference/rest/v1/users.history/list
    """
    # Validate input
    request = HistoryListRequest(
        startHistoryId=startHistoryId,
        user_id=user_id,
        maxResults=maxResults,
        pageToken=pageToken,
        labelId=labelId,
        historyTypes=historyTypes
    )

    # Build query parameters
    params = {"startHistoryId": request.startHistoryId}

    if request.maxResults:
        params["maxResults"] = request.maxResults

    if request.pageToken:
        params["pageToken"] = request.pageToken

    if request.labelId:
        params["labelId"] = request.labelId

    if request.historyTypes:
        params["historyTypes"] = request.historyTypes

    # Make API request
    client = GmailAPIClient()
    return await client.get(f"/users/{request.user_id}/history", params)

"""
Retrieve messages from a Gmail thread using its thread ID.

Implements the GMAIL_FETCH_MESSAGE_BY_THREAD_ID tool specification from gmail.md.

Security features:
- Input validation with Pydantic
- Authenticated via worker_context OAuth tokens
- Validates thread_id format
"""
from typing import Dict, Any
from arka_mcp.servers.gmail_tools.client import GmailAPIClient
from arka_mcp.servers.gmail_tools.models import FetchMessagesByThreadIdRequest


async def fetch_messages_by_thread_id(
    thread_id: str,
    user_id: str = "me",
    page_token: str = ""
) -> Dict[str, Any]:
    """
    Retrieve messages from a Gmail thread using its thread ID.

    Args:
        thread_id: Unique ID of the thread (required)
        user_id: User's email address or 'me' (default: 'me')
        page_token: Token for retrieving a specific page of messages

    Returns:
        Dict containing the thread with all its messages

    Example:
        thread = await fetch_messages_by_thread_id(
            thread_id="xsdfe3264vrfw"
        )

    Gmail API Reference:
        https://developers.google.com/gmail/api/reference/rest/v1/users.threads/get
    """
    # Validate input
    request = FetchMessagesByThreadIdRequest(
        thread_id=thread_id,
        user_id=user_id,
        page_token=page_token
    )

    # Build query parameters
    params = {}
    if request.page_token:
        params["pageToken"] = request.page_token

    # Make API request
    client = GmailAPIClient()
    return await client.get(
        f"/users/{request.user_id}/threads/{request.thread_id}",
        params if params else None
    )

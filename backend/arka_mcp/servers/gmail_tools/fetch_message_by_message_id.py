"""
Fetch a specific Gmail message by its ID.

Implements the GMAIL_FETCH_MESSAGE_BY_MESSAGE_ID tool specification from gmail.md.

Security features:
- Input validation with Pydantic
- Authenticated via worker_context OAuth tokens
- Validates message_id format
"""
from typing import Dict, Any
from arka_mcp.servers.gmail_tools.client import GmailAPIClient
from arka_mcp.servers.gmail_tools.models import FetchMessageByIdRequest


async def fetch_message_by_message_id(
    message_id: str,
    user_id: str = "me",
    format: str = "full"
) -> Dict[str, Any]:
    """
    Fetch a specific email message by its ID.

    Args:
        message_id: Unique ID of the message (required)
        user_id: User's email address or 'me' (default: 'me')
        format: Message format (minimal/full/raw/metadata, default: 'full')
            - minimal: ID and labels only
            - full: Complete message data
            - raw: Base64url encoded raw message
            - metadata: ID, labels, and headers

    Returns:
        Dict containing the full message details

    Example:
        message = await fetch_message_by_message_id(
            message_id="xsdfe3264vrfw",
            format="full"
        )

    Gmail API Reference:
        https://developers.google.com/gmail/api/reference/rest/v1/users.messages/get
    """
    # Validate input
    request = FetchMessageByIdRequest(
        message_id=message_id,
        user_id=user_id,
        format=format
    )

    # Build query parameters
    params = {"format": request.format}

    # Make API request
    client = GmailAPIClient()
    return await client.get(
        f"/users/{request.user_id}/messages/{request.message_id}",
        params
    )

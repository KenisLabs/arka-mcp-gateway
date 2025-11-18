"""
Retrieve Gmail profile information for a user.

Implements the GMAIL_GET_PROFILE tool specification from gmail.md.

Security features:
- Input validation with Pydantic
- Authenticated via worker_context OAuth tokens
"""
from typing import Dict, Any
from arka_mcp.servers.gmail_tools.client import GmailAPIClient
from arka_mcp.servers.gmail_tools.models import GetProfileRequest


async def get_profile(user_id: str = "me") -> Dict[str, Any]:
    """
    Retrieve key Gmail profile information.

    Returns email address, message/thread totals, and history ID for a user.

    Args:
        user_id: The email address of the Gmail user or 'me' (default: 'me')

    Returns:
        Dict containing:
        - emailAddress: User's email address
        - messagesTotal: Total number of messages in mailbox
        - threadsTotal: Total number of threads in mailbox
        - historyId: Current history ID

    Example:
        profile = await get_profile()
        print(f"Email: {profile['emailAddress']}")
        print(f"Total messages: {profile['messagesTotal']}")

    Gmail API Reference:
        https://developers.google.com/gmail/api/reference/rest/v1/users/getProfile
    """
    # Validate input
    request = GetProfileRequest(user_id=user_id)

    # Make API request
    client = GmailAPIClient()
    return await client.get(f"/users/{request.user_id}/profile")

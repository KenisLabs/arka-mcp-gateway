"""
Retrieve a specific attachment from a Gmail message.

Implements the GMAIL_GET_ATTACHMENT tool specification from gmail.md.

Security features:
- Input validation with Pydantic
- Authenticated via worker_context OAuth tokens
- Validates message_id and attachment_id formats
"""
from typing import Dict, Any
from arka_mcp.servers.gmail_tools.client import GmailAPIClient
from arka_mcp.servers.gmail_tools.models import GetAttachmentRequest


async def get_attachment(
    message_id: str,
    attachment_id: str,
    file_name: str,
    user_id: str = "me"
) -> Dict[str, Any]:
    """
    Retrieve a specific attachment by ID from a message.

    Args:
        message_id: ID of the message containing the attachment (required)
        attachment_id: ID of the attachment to retrieve (required)
        file_name: Desired filename for the downloaded attachment (required)
        user_id: User's email address or 'me' (default: 'me')

    Returns:
        Dict containing attachment data in base64url encoding

    Example:
        attachment = await get_attachment(
            message_id="18exampleMessageId7f9",
            attachment_id="A_PART0.1_18exampleAttachmentId7f9",
            file_name="invoice.pdf"
        )

    Gmail API Reference:
        https://developers.google.com/gmail/api/reference/rest/v1/users.messages.attachments/get
    """
    # Validate input
    request = GetAttachmentRequest(
        message_id=message_id,
        attachment_id=attachment_id,
        file_name=file_name,
        user_id=user_id
    )

    # Make API request
    client = GmailAPIClient()
    return await client.get(
        f"/users/{request.user_id}/messages/{request.message_id}/attachments/{request.attachment_id}"
    )

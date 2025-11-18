"""
Create a new Gmail label.

Implements the GMAIL_CREATE_LABEL tool specification from gmail.md.

Security features:
- Input validation with Pydantic
- Authenticated via worker_context OAuth tokens
- Validates label name format and length
"""
from typing import Dict, Any, Optional
from arka_mcp.servers.gmail_tools.client import GmailAPIClient
from arka_mcp.servers.gmail_tools.models import CreateLabelRequest


async def create_label(
    label_name: str,
    user_id: str = "me",
    background_color: Optional[str] = None,
    text_color: Optional[str] = None,
    label_list_visibility: str = "labelShow",
    message_list_visibility: str = "show"
) -> Dict[str, Any]:
    """
    Create a new Gmail label with the specified name and properties.

    Args:
        label_name: The name for the new label (required)
            - Must be unique within the account
            - Maximum 225 characters
            - Cannot contain ',', '/', or '.'
        user_id: User's email address or 'me' (default: 'me')
        background_color: Background color (hex from Gmail palette)
        text_color: Text color (hex from Gmail palette)
        label_list_visibility: How label appears in list (labelShow/labelShowIfUnread/labelHide)
        message_list_visibility: How messages appear (show/hide)

    Returns:
        Dict containing the created label with id, name, and other properties

    Example:
        label = await create_label(
            label_name="Important Clients",
            background_color="#4a86e8",
            text_color="#ffffff"
        )

    Gmail API Reference:
        https://developers.google.com/gmail/api/reference/rest/v1/users.labels/create
    """
    # Validate input
    request = CreateLabelRequest(
        label_name=label_name,
        user_id=user_id,
        background_color=background_color,
        text_color=text_color,
        label_list_visibility=label_list_visibility,
        message_list_visibility=message_list_visibility
    )

    # Build request body
    body = {
        "name": request.label_name,
        "labelListVisibility": request.label_list_visibility,
        "messageListVisibility": request.message_list_visibility
    }

    # Add color if both background and text colors are provided
    if request.background_color and request.text_color:
        body["color"] = {
            "backgroundColor": request.background_color,
            "textColor": request.text_color
        }

    # Make API request
    client = GmailAPIClient()
    return await client.post(f"/users/{request.user_id}/labels", body)

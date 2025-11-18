"""
Update an existing Gmail label.

Implements the GMAIL_PATCH_LABEL tool specification from gmail.md.

Security features:
- Input validation with Pydantic
- Authenticated via worker_context OAuth tokens
- Partial update support (only specified fields)
"""
from typing import Dict, Any, Optional
from arka_mcp.servers.gmail_tools.client import GmailAPIClient
from arka_mcp.servers.gmail_tools.models import PatchLabelRequest


async def patch_label(
    label_id: str,
    user_id: str = "me",
    name: Optional[str] = None,
    background_color: Optional[str] = None,
    text_color: Optional[str] = None,
    label_list_visibility: Optional[str] = None,
    message_list_visibility: Optional[str] = None
) -> Dict[str, Any]:
    """
    Update properties of an existing Gmail label.

    Only the specified fields will be updated (partial update).

    Args:
        label_id: ID of the label to update (required)
        user_id: User's email address or 'me' (default: 'me')
        name: New display name for the label
        background_color: New background color (hex from Gmail palette)
        text_color: New text color (hex from Gmail palette)
        label_list_visibility: How label appears in list (labelShow/labelShowIfUnread/labelHide)
        message_list_visibility: How messages appear (show/hide)

    Returns:
        Dict containing the updated label

    Example:
        updated_label = await patch_label(
            label_id="Label_123",
            name="Very Important Clients",
            background_color="#ff0000"
        )

    Gmail API Reference:
        https://developers.google.com/gmail/api/reference/rest/v1/users.labels/patch
    """
    # Validate input
    request = PatchLabelRequest(
        id=label_id,
        userId=user_id,
        name=name,
        labelListVisibility=label_list_visibility,
        messageListVisibility=message_list_visibility
    )

    # Build patch body (only include fields that are set)
    body = {}

    if name:
        body["name"] = name

    if background_color and text_color:
        body["color"] = {
            "backgroundColor": background_color,
            "textColor": text_color
        }

    if label_list_visibility:
        body["labelListVisibility"] = label_list_visibility

    if message_list_visibility:
        body["messageListVisibility"] = message_list_visibility

    # Make API request
    client = GmailAPIClient()
    return await client.patch(f"/users/{user_id}/labels/{label_id}", body)

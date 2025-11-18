"""
Add or remove labels from a Gmail thread.

Implements the GMAIL_MODIFY_THREAD_LABELS tool specification from gmail.md.

Security features:
- Input validation with Pydantic
- Authenticated via worker_context OAuth tokens
- Validates thread_id format
"""
from typing import Dict, Any, List, Optional
from arka_mcp.servers.gmail_tools.client import GmailAPIClient
from arka_mcp.servers.gmail_tools.models import ModifyThreadLabelsRequest


async def modify_thread_labels(
    thread_id: str,
    user_id: str = "me",
    add_label_ids: Optional[List[str]] = None,
    remove_label_ids: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Add or remove labels from a Gmail thread, affecting all its messages.

    Args:
        thread_id: Immutable ID of the thread to modify (required)
        user_id: User's email address or 'me' (default: 'me')
        add_label_ids: Label IDs to add (e.g., ['STARRED', 'INBOX'])
        remove_label_ids: Label IDs to remove (e.g., ['IMPORTANT'])

    Returns:
        Dict containing the updated thread

    Example:
        # Star entire thread
        await modify_thread_labels(
            thread_id="18ea7715b619f09c",
            add_label_ids=["STARRED"]
        )

        # Archive thread
        await modify_thread_labels(
            thread_id="18ea7715b619f09c",
            remove_label_ids=["INBOX"]
        )

    Gmail API Reference:
        https://developers.google.com/gmail/api/reference/rest/v1/users.threads/modify
    """
    # Validate input
    request = ModifyThreadLabelsRequest(
        thread_id=thread_id,
        user_id=user_id,
        add_label_ids=add_label_ids,
        remove_label_ids=remove_label_ids
    )

    # Build request body
    body = {}

    if request.add_label_ids:
        body["addLabelIds"] = request.add_label_ids

    if request.remove_label_ids:
        body["removeLabelIds"] = request.remove_label_ids

    # Make API request
    client = GmailAPIClient()
    return await client.post(
        f"/users/{request.user_id}/threads/{request.thread_id}/modify",
        body
    )

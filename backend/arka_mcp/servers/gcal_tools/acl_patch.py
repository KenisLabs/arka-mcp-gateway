"""
Updates an access control rule for a calendar using patch semantics (partial update). This allows modifying specific fields without affecting other properties. Note: Each patch request consumes three quota units. For domain-type ACL rules, if PATCH fails with 500 error, this action will automatically fallback to UPDATE method.

Google Calendar API Reference:
https://developers.google.com/calendar/api/v3/reference/acl/patch
"""
from typing import Any, Dict, Optional
from .client import CalendarAPIClient


async def acl_patch(
    calendar_id: str,
    rule_id: str,
    role: Optional[str] = None,
    scope: Optional[Dict[str, Any]] = None,
    sendNotifications: Optional[bool] = None
) -> Dict[str, Any]:
    """
    Updates an access control rule for a calendar using patch semantics (partial update). This allows modifying specific fields without affecting other properties.

    Args:
        calendar_id: Calendar identifier. To retrieve calendar IDs call the calendarList.list method.
        rule_id: ACL rule identifier. This is typically in the format 'type:value', such as 'user:email@example.com'.
        role: The role assigned to the scope. Possible values are:
              - "none" - Provides no access.
              - "freeBusyReader" - Provides read access to free/busy information.
              - "reader" - Provides read access to the calendar.
              - "writer" - Provides read and write access to the calendar.
              - "owner" - Provides ownership of the calendar.
        scope: The extent to which calendar access is granted by this ACL rule. Optional for patch operations.
               Structure: {"type": "user|group|domain|default", "value": "email or domain"}
        sendNotifications: Whether to send notifications about the calendar sharing change.

    Returns:
        Dict containing the API response

    Example:
        result = await acl_patch(
            calendar_id="primary",
            rule_id="user:user@example.com",
            role="reader",
            sendNotifications=False
        )
    """
    client = CalendarAPIClient()

    endpoint = f"/calendars/{calendar_id}/acl/{rule_id}"

    # Build request body - role and scope go in the body
    request_body = {}
    if role is not None:
        request_body["role"] = role
    if scope is not None:
        request_body["scope"] = scope

    # Query parameters - sendNotifications is a query parameter
    params = {}
    if sendNotifications is not None:
        params["sendNotifications"] = sendNotifications

    return await client.patch(endpoint, json_data=request_body, params=params)

"""
Updates an access control rule for the specified calendar.

Google Calendar API Reference:
https://developers.google.com/calendar/api/v3/reference/acl/update
"""
from typing import Optional
from .client import CalendarAPIClient


async def update_acl_rule(
    calendar_id: str,
    role: str,
    rule_id: str,
    sendNotifications: Optional[bool] = True
) -> dict:
    """
    Updates an access control rule for the specified calendar.

    Args:
        calendar_id: Calendar identifier. To retrieve calendar IDs call the calendarList.list method.
        role: The role assigned to the scope. Possible values are:
              - "none" - Provides no access.
              - "freeBusyReader" - Provides read access to free/busy information.
              - "reader" - Provides read access to the calendar.
              - "writer" - Provides read and write access to the calendar.
              - "owner" - Provides ownership of the calendar.
        rule_id: ACL rule identifier.
        sendNotifications: Whether to send notifications about the calendar sharing change. Default: True.

    Returns:
        Dict containing the API response

    Example:
        result = await update_acl_rule(
            calendar_id="primary",
            rule_id="user:user@example.com",
            role="writer",
            sendNotifications=True
        )
    """
    client = CalendarAPIClient()

    endpoint = f"/calendars/{calendar_id}/acl/{rule_id}"

    # Build request body - only role goes in the body
    request_body = {}
    if role is not None:
        request_body["role"] = role

    # Query parameters - sendNotifications is a query parameter
    params = {}
    if sendNotifications is not None:
        params["sendNotifications"] = sendNotifications

    return await client.put(endpoint, json_data=request_body, params=params)

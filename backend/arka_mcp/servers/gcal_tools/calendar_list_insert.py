"""
Inserts an existing calendar into the user's calendar list.

Google Calendar API Reference:
https://developers.google.com/calendar/api/v3/reference/calendarList/insert
"""
from typing import Any, Dict, List, Optional
from .client import CalendarAPIClient


async def calendar_list_insert(
    id: str,
    backgroundColor: Optional[str] = None,
    colorId: Optional[str] = None,
    colorRgbFormat: Optional[bool] = None,
    defaultReminders: Optional[List[Dict[str, Any]]] = None,
    foregroundColor: Optional[str] = None,
    hidden: Optional[bool] = None,
    notificationSettings: Optional[Dict[str, Any]] = None,
    selected: Optional[bool] = None,
    summaryOverride: Optional[str] = None
) -> Dict[str, Any]:
    """
    Inserts an existing calendar into the user's calendar list.

    Args:
        id: The identifier of the calendar to insert.
        backgroundColor: The background color of the calendar in the Web UI. (Hexadecimal color code)
        colorId: The color of the calendar. This is an ID referring to an entry in the calendar color definitions.
        colorRgbFormat: Whether to use the foregroundColor and backgroundColor fields to write the calendar colors.
        defaultReminders: The default reminders that the authenticated user has for this calendar.
        foregroundColor: The foreground color of the calendar in the Web UI. (Hexadecimal color code)
        hidden: Whether the calendar has been hidden from the list. Default is False.
        notificationSettings: The notifications that the authenticated user is receiving for this calendar.
        selected: Whether the calendar is selected and visible in the calendar list. Default is True.
        summaryOverride: The summary that the authenticated user has set for this calendar.

    Returns:
        Dict containing the API response

    Example:
        result = await calendar_list_insert(
            id="calendar@example.com",
            selected=True,
            colorId="1"
        )
    """
    client = CalendarAPIClient()

    endpoint = "/users/me/calendarList"

    # Build request body with proper camelCase field names
    request_body = {}
    if id is not None:
        request_body["id"] = id
    if backgroundColor is not None:
        request_body["backgroundColor"] = backgroundColor
    if colorId is not None:
        request_body["colorId"] = colorId
    if foregroundColor is not None:
        request_body["foregroundColor"] = foregroundColor
    if selected is not None:
        request_body["selected"] = selected
    if hidden is not None:
        request_body["hidden"] = hidden
    if summaryOverride is not None:
        request_body["summaryOverride"] = summaryOverride
    if defaultReminders is not None:
        request_body["defaultReminders"] = defaultReminders
    if notificationSettings is not None:
        request_body["notificationSettings"] = notificationSettings

    # Query parameters
    params = {}
    if colorRgbFormat is not None:
        params["colorRgbFormat"] = colorRgbFormat

    return await client.post(endpoint, json_data=request_body, params=params)

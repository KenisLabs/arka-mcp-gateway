"""
Updates an existing entry on the user\'s calendar list.

Google Calendar API Reference:
https://developers.google.com/calendar/api/v3/reference/calendarList/update
"""
from typing import Any, Dict, List, Optional
from .client import CalendarAPIClient


async def calendar_list_update(
    calendar_id: str,
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
    Updates an existing entry on the user's calendar list.

    Args:
        calendar_id: Calendar identifier. Must be an actual calendar ID (e.g., calendar email address).
        backgroundColor: Hex color for calendar background.
        colorId: ID for calendar color from colors endpoint.
        colorRgbFormat: Whether to use RGB for foreground/background colors.
        defaultReminders: List of default reminders.
        foregroundColor: Hex color for calendar foreground.
        hidden: Whether calendar is hidden.
        notificationSettings: Notification settings for the calendar.
        selected: Whether calendar content shows in UI.
        summaryOverride: User-set summary for the calendar.

    Returns:
        Dict containing the API response

    Example:
        result = await calendar_list_update(
            calendar_id="calendar@example.com",
            selected=True,
            colorId="2"
        )
    """
    client = CalendarAPIClient()

    endpoint = f"/users/me/calendarList/{calendar_id}"

    # Build request body with proper camelCase field names
    request_body = {}
    if backgroundColor is not None:
        request_body["backgroundColor"] = backgroundColor
    if foregroundColor is not None:
        request_body["foregroundColor"] = foregroundColor
    if colorId is not None:
        request_body["colorId"] = colorId
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

    return await client.put(endpoint, json_data=request_body, params=params)

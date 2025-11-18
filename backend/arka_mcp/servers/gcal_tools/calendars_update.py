"""
Updates metadata for a calendar.

Google Calendar API Reference:
https://developers.google.com/calendar/api/v3/reference/calendars/update
"""
from typing import Optional
from .client import CalendarAPIClient


async def calendars_update(
    calendarId: str,
    summary: str,
    description: Optional[str] = None,
    location: Optional[str] = None,
    timeZone: Optional[str] = None
) -> dict:
    """
    Updates metadata for a calendar.

    Args:
        calendarId: Calendar identifier. To retrieve calendar IDs call the calendarList.list method.
        summary: Title of the calendar.
        description: Description of the calendar. Optional.
        location: Geographic location of the calendar as free-form text. Optional.
        timeZone: The time zone of the calendar. (Formatted as an IANA Time Zone Database name, e.g. "Europe/Zurich")

    Returns:
        Dict containing the API response

    Example:
        result = await calendars_update(
            calendarId="primary",
            summary="My Updated Calendar",
            description="Updated description",
            timeZone="America/New_York"
        )
    """
    client = CalendarAPIClient()

    endpoint = f"/calendars/{calendarId}"

    request_body = {}
    if summary is not None:
        request_body["summary"] = summary
    if description is not None:
        request_body["description"] = description
    if location is not None:
        request_body["location"] = location
    if timeZone is not None:
        request_body["timeZone"] = timeZone

    return await client.put(endpoint, json_data=request_body)

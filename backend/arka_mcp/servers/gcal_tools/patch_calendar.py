"""
Partially updates (PATCHes) an existing Google Calendar, modifying only the fields provided; `summary` is mandatory and cannot be an empty string, and an empty string for `description` or `location` clears them.

Google Calendar API Reference:
https://developers.google.com/calendar/api/v3/reference/calendars/patch
"""
from typing import Optional
from .client import CalendarAPIClient


async def patch_calendar(
    calendar_id: str,
    summary: str,
    description: Optional[str] = None,
    location: Optional[str] = None,
    timezone: Optional[str] = None
) -> dict:
    """
    Partially updates (PATCHes) an existing Google Calendar, modifying only the fields provided; `summary` is mandatory and cannot be an empty string.

    Args:
        calendar_id: Identifier of the Google Calendar to update; use 'primary' for the main calendar.
        summary: New title for the calendar; cannot be an empty string.
        description: New description for the calendar.
        location: New geographic location of the calendar (e.g., 'Paris, France').
        timezone: New IANA Time Zone Database name for the calendar (e.g., 'Europe/Zurich', 'America/New_York').

    Returns:
        Dict containing the API response

    Example:
        result = await patch_calendar(
            calendar_id="primary",
            summary="My Updated Calendar",
            timezone="America/New_York"
        )
    """
    client = CalendarAPIClient()

    endpoint = f"/calendars/{calendar_id}"

    request_body = {}
    if summary is not None:
        request_body["summary"] = summary
    if description is not None:
        request_body["description"] = description
    if location is not None:
        request_body["location"] = location
    if timezone is not None:
        request_body["timeZone"] = timezone

    return await client.patch(endpoint, json_data=request_body)

"""
Retrieves a specific Google Calendar, identified by `calendar_id`, to which the authenticated user has access.

Google Calendar API Reference:
https://developers.google.com/calendar/api/v3/reference/calendars/get
"""
from typing import Optional
from .client import CalendarAPIClient


async def get_calendar(
    calendar_id: str = "primary"
) -> dict:
    """
    Retrieves a specific Google Calendar, identified by `calendar_id`, to which the authenticated user h...

    Args:
        calendar_id: Identifier of the Google Calendar to retrieve. 'primary' (the default) represents the u...

    Returns:
        Dict containing the API response

    Example:
        result = await get_calendar(...)
    """
    client = CalendarAPIClient()

    endpoint = f"/calendars/{calendar_id}"

    return await client.get(endpoint)

"""
Clears a primary calendar. This operation deletes all events associated with the primary calendar of an account.

Google Calendar API Reference:
https://developers.google.com/calendar/api/v3/reference/calendars/clear
"""
from .client import CalendarAPIClient


async def clear_calendar(
    calendar_id: str
) -> dict:
    """
    Clears a primary calendar. This operation deletes all events associated with the primary calendar of...

    Args:
        calendar_id: Calendar identifier. To retrieve calendar IDs call the `calendarList.list` method. If y...

    Returns:
        Dict containing the API response

    Example:
        result = await clear_calendar(...)
    """
    client = CalendarAPIClient()

    endpoint = f"/calendars/{calendar_id}/clear"

    return await client.post(endpoint, json_data={})

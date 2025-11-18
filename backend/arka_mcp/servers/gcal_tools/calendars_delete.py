"""
Deletes a secondary calendar. Use calendars.clear for clearing all events on primary calendars.

Google Calendar API Reference:
https://developers.google.com/calendar/api/v3/reference/calendars/delete
"""
from .client import CalendarAPIClient


async def calendars_delete(
    calendar_id: str
) -> dict:
    """
    Deletes a secondary calendar. Use calendars.clear for clearing all events on primary calendars.

    Args:
        calendar_id: Calendar identifier. To retrieve calendar IDs call the calendarList.list method. If you...

    Returns:
        Dict containing the API response

    Example:
        result = await calendars_delete(...)
    """
    client = CalendarAPIClient()

    endpoint = f"/calendars/{calendar_id}"

    return await client.delete(endpoint)

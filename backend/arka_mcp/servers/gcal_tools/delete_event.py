"""
Deletes a specified event by `event_id` from a Google Calendar (`calendar_id`); this action is idempotent and raises a 404 error if the event is not found.

Google Calendar API Reference:
https://developers.google.com/calendar/api/v3/reference/events/delete
"""
from typing import Optional
from .client import CalendarAPIClient


async def delete_event(
    event_id: str,
    calendar_id: str = "primary"
) -> dict:
    """
    Deletes a specified event by `event_id` from a Google Calendar (`calendar_id`); this action is idemp...

    Args:
        calendar_id: Identifier of the Google Calendar (e.g., email address, specific ID, or 'primary' for t...
        event_id: Unique identifier of the event to delete, typically obtained upon event creation.

    Returns:
        Dict containing the API response

    Example:
        result = await delete_event(...)
    """
    client = CalendarAPIClient()

    endpoint = f"/calendars/{calendar_id}/events/{event_id}"

    return await client.delete(endpoint)

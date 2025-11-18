"""
Moves an event to another calendar, i.e., changes an event's organizer.

Google Calendar API Reference:
https://developers.google.com/calendar/api/v3/reference/events/move
"""
from typing import Optional
from .client import CalendarAPIClient


async def events_move(
    calendar_id: str,
    event_id: str,
    destination: str,
    sendUpdates: Optional[str] = None
) -> dict:
    """
    Moves an event to another calendar, i.e., changes an event's organizer.

    This is a POST request with query parameters only (no body).

    Args:
        calendar_id: Calendar identifier of the source calendar
        event_id: Event identifier
        destination: Calendar identifier of the destination calendar
        sendUpdates: Guests who should receive notifications ("all", "externalOnly", "none")

    Returns:
        Dict containing the moved event

    Example:
        result = await events_move(
            calendar_id="primary",
            event_id="event123",
            destination="other@gmail.com",
            sendUpdates="all"
        )

    API Reference:
        https://developers.google.com/calendar/api/v3/reference/events/move
    """
    client = CalendarAPIClient()

    endpoint = f"/calendars/{calendar_id}/events/{event_id}/move"

    # Build query parameters (this is a POST with query params, no body)
    params = {"destination": destination}
    if sendUpdates:
        params["sendUpdates"] = sendUpdates

    return await client.post(endpoint, json_data={}, params=params)

"""
Finds events in a specified Google Calendar using text query, time ranges (event start/end, last modification), and event types; ensure `timeMin` is not chronologically after `timeMax` if both are provided.

Google Calendar API Reference:
https://developers.google.com/calendar/api/v3/reference/events/get
"""
from typing import List, Optional
from .client import CalendarAPIClient


async def find_event(
    calendar_id: str = "primary",
    event_types: List[str] = None,
    max_results: int = 10,
    order_by: Optional[str] = None,
    page_token: Optional[str] = None,
    query: Optional[str] = None,
    show_deleted: Optional[bool] = None,
    single_events: bool = True,
    timeMax: Optional[str] = None,
    timeMin: Optional[str] = None,
    updated_min: Optional[str] = None
) -> dict:
    """
    Finds events in a specified Google Calendar using text query, time ranges (event start/end, last mod...

    Args:
        calendar_id: Identifier of the Google Calendar to query. Use 'primary' for the primary calendar of t...
        event_types: Event types to include. Supported values: 'birthday', 'default', 'focusTime', 'outOfOff...
        max_results: Maximum number of events per page (1-2500).
        order_by: Order of events: 'startTime' (ascending by start time) or 'updated' (ascending by last ...
        page_token: Token from a previous response's `nextPageToken` to fetch the subsequent page of results.
        query: Free-text search terms to find events. This query is matched against various event fiel...
        show_deleted: Include events whose status is 'cancelled'. This surfaces cancelled/deleted events, not...
        single_events: When true, recurring event series are expanded into their individual instances. When fa...
        timeMax: Upper bound (exclusive) for an event's start time to filter by. Only events starting be...
        timeMin: Lower bound (exclusive) for an event's end time to filter by. Only events ending after ...
        updated_min: Lower bound (exclusive) for an event's last modification time to filter by. Only events...

    Returns:
        Dict containing the API response

    Example:
        result = await find_event(...)
    """
    client = CalendarAPIClient()

    endpoint = f"/calendars/{calendar_id}/events/{eventId}"

    params = {}
    if timeMin is not None:
        params["timeMin"] = timeMin
    if timeMax is not None:
        params["timeMax"] = timeMax

    return await client.get(endpoint, params=params)

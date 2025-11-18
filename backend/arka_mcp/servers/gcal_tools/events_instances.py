"""
Returns instances of the specified recurring event.

Google Calendar API Reference:
https://developers.google.com/calendar/api/v3/reference/events/instances
"""
from typing import Optional
from .client import CalendarAPIClient


async def events_instances(
    calendarId: str,
    eventId: str,
    maxAttendees: Optional[int] = None,
    maxResults: Optional[int] = None,
    originalStart: Optional[str] = None,
    pageToken: Optional[str] = None,
    showDeleted: Optional[bool] = None,
    timeMax: Optional[str] = None,
    timeMin: Optional[str] = None,
    timeZone: Optional[str] = None
) -> dict:
    """
    Returns instances of the specified recurring event.

    Args:
        calendarId: Calendar identifier. To retrieve calendar IDs call the `calendarList.list` method. If y...
        eventId: Recurring event identifier.
        maxAttendees: The maximum number of attendees to include in the response. If there are more than the ...
        maxResults: Maximum number of events returned on one result page. By default the value is 250 event...
        originalStart: The original start time of the instance in the result. Optional.
        pageToken: Token specifying which result page to return. Optional.
        showDeleted: Whether to include deleted events (with status equals "cancelled") in the result. Cance...
        timeMax: Upper bound (exclusive) for an event's start time to filter by. Optional. The default i...
        timeMin: Lower bound (inclusive) for an event's end time to filter by. Optional. The default is ...
        timeZone: Time zone used in the response. Optional. The default is the time zone of the calendar.

    Returns:
        Dict containing the API response

    Example:
        result = await events_instances(...)
    """
    client = CalendarAPIClient()

    endpoint = f"/calendars/{calendarId}/events/{eventId}/instances"

    params = {}
    if maxResults is not None:
        params["maxResults"] = maxResults
    if showDeleted is not None:
        params["showDeleted"] = showDeleted
    if timeMax is not None:
        params["timeMax"] = timeMax
    if maxAttendees is not None:
        params["maxAttendees"] = maxAttendees
    if pageToken is not None:
        params["pageToken"] = pageToken
    if timeMin is not None:
        params["timeMin"] = timeMin
    if timeZone is not None:
        params["timeZone"] = timeZone

    return await client.get(endpoint, params=params)

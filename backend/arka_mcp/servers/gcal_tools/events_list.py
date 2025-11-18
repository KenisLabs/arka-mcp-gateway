"""
Returns events on the specified calendar.

Google Calendar API Reference:
https://developers.google.com/calendar/api/v3/reference/events/list
"""
from typing import Optional
from .client import CalendarAPIClient


async def events_list(
    calendarId: str,
    alwaysIncludeEmail: Optional[bool] = None,
    eventTypes: Optional[str] = None,
    iCalUID: Optional[str] = None,
    maxAttendees: Optional[int] = None,
    maxResults: Optional[int] = None,
    orderBy: Optional[str] = None,
    pageToken: Optional[str] = None,
    privateExtendedProperty: Optional[str] = None,
    q: Optional[str] = None,
    sharedExtendedProperty: Optional[str] = None,
    showDeleted: Optional[bool] = None,
    showHiddenInvitations: Optional[bool] = None,
    singleEvents: Optional[bool] = None,
    syncToken: Optional[str] = None,
    timeMax: Optional[str] = None,
    timeMin: Optional[str] = None,
    timeZone: Optional[str] = None,
    updatedMin: Optional[str] = None
) -> dict:
    """
    Returns events on the specified calendar.

    Args:
        alwaysIncludeEmail: Deprecated and ignored.
        calendarId: Calendar identifier. To retrieve calendar IDs call the calendarList.list method. If you...
        eventTypes: Event types to return. Optional. This parameter can be repeated multiple times to retur...
        iCalUID: Specifies an event ID in the iCalendar format to be provided in the response. Optional....
        maxAttendees: The maximum number of attendees to include in the response. If there are more than the ...
        maxResults: Maximum number of events returned on one result page. The number of events in the resul...
        orderBy: The order of the events returned in the result. Optional. The default is an unspecified...
        pageToken: Token specifying which result page to return. Optional.
        privateExtendedProperty: Extended properties constraint specified as propertyName=value. Matches only private pr...
        q: Free text search terms to find events that match these terms in various fields. Optional.
        sharedExtendedProperty: Extended properties constraint specified as propertyName=value. Matches only shared pro...
        showDeleted: Include cancelled events (status="cancelled"). Optional; default is false. This surface...
        showHiddenInvitations: Whether to include hidden invitations in the result. Optional. The default is False. Hi...
        singleEvents: Whether to expand recurring events into instances and only return single one-off events...
        syncToken: Token from nextSyncToken to return only entries changed since the last list. Cannot be ...
        timeMax: Upper bound (exclusive) for an event's start time to filter by. Optional. If unset, no ...
        timeMin: Lower bound (exclusive) for an event's end time to filter by. Optional. If unset, no en...
        timeZone: Time zone used in the response. Optional. Use an IANA time zone identifier (e.g., Ameri...
        updatedMin: Lower bound for an event's last modification time (RFC3339). When specified, entries de...

    Returns:
        Dict containing the API response

    Example:
        result = await events_list(...)
    """
    client = CalendarAPIClient()

    endpoint = f"/calendars/{calendarId}/events"

    params = {}
    if maxResults is not None:
        params["maxResults"] = maxResults
    if singleEvents is not None:
        params["singleEvents"] = singleEvents
    if syncToken is not None:
        params["syncToken"] = syncToken
    if timeZone is not None:
        params["timeZone"] = timeZone
    if showDeleted is not None:
        params["showDeleted"] = showDeleted
    if sharedExtendedProperty is not None:
        params["sharedExtendedProperty"] = sharedExtendedProperty
    if showHiddenInvitations is not None:
        params["showHiddenInvitations"] = showHiddenInvitations
    if updatedMin is not None:
        params["updatedMin"] = updatedMin
    if timeMax is not None:
        params["timeMax"] = timeMax
    if maxAttendees is not None:
        params["maxAttendees"] = maxAttendees
    if pageToken is not None:
        params["pageToken"] = pageToken
    if eventTypes is not None:
        params["eventTypes"] = eventTypes
    if orderBy is not None:
        params["orderBy"] = orderBy
    if timeMin is not None:
        params["timeMin"] = timeMin
    if q is not None:
        params["q"] = q
    if privateExtendedProperty is not None:
        params["privateExtendedProperty"] = privateExtendedProperty
    if alwaysIncludeEmail is not None:
        params["alwaysIncludeEmail"] = alwaysIncludeEmail
    if iCalUID is not None:
        params["iCalUID"] = iCalUID

    return await client.get(endpoint, params=params)

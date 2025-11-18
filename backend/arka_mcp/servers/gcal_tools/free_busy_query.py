"""
Returns free/busy information for a set of calendars.

Google Calendar API Reference:
https://developers.google.com/calendar/api/v3/reference/freebusy/query
"""
from typing import Any, Dict, List, Optional
from .client import CalendarAPIClient


async def free_busy_query(
    items: List[Dict[str, Any]],
    timeMax: str,
    timeMin: str,
    calendarExpansionMax: Optional[int] = None,
    groupExpansionMax: Optional[int] = None,
    timeZone: Optional[str] = None
) -> Dict[str, Any]:
    """
    Returns free/busy information for a set of calendars.

    Args:
        calendarExpansionMax: Maximal number of calendars for which FreeBusy information is to be provided. Optional....
        groupExpansionMax: Maximal number of calendar identifiers to be provided for a single group. Optional. An ...
        items: List of calendars and/or groups to query.
        timeMax: The end of the interval for the query formatted as per RFC3339.
        timeMin: The start of the interval for the query formatted as per RFC3339.
        timeZone: Time zone used in the response. Optional. The default is UTC.

    Returns:
        Dict containing the API response

    Example:
        result = await free_busy_query(...)
    """
    client = CalendarAPIClient()

    endpoint = "/freeBusy"

    request_body = {
        "items": items,
        "timeMax": timeMax,
        "timeMin": timeMin
    }
    if groupExpansionMax is not None:
        request_body["groupExpansionMax"] = groupExpansionMax
    if calendarExpansionMax is not None:
        request_body["calendarExpansionMax"] = calendarExpansionMax
    if timeZone is not None:
        request_body["timeZone"] = timeZone

    return await client.post(endpoint, json_data=request_body)

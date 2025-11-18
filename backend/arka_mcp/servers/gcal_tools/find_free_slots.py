"""
Finds both free and busy time slots in Google Calendars.

Google Calendar API Reference:
https://developers.google.com/calendar/api/v3/reference/freebusy/query
"""
from typing import List, Optional, Dict, Any
from .client import CalendarAPIClient


async def find_free_slots(
    items: List[str],
    time_min: str,
    time_max: str,
    timeZone: str = "UTC",
    calendarExpansionMax: int = 50,
    groupExpansionMax: int = 100
) -> Dict[str, Any]:
    """
    Finds both free and busy time slots in Google Calendars for specified calendars.

    Args:
        items: List of calendar identifiers to query for free/busy information
        time_min: Start datetime for the query interval (RFC3339)
        time_max: End datetime for the query interval (RFC3339)
        timeZone: IANA timezone identifier (e.g., 'America/New_York', 'UTC')
        calendarExpansionMax: Maximum calendars for FreeBusy information (max: 50)
        groupExpansionMax: Maximum calendar identifiers for a single group (max: 100)

    Returns:
        Dict containing busy time slots and calendar information

    Example:
        result = await find_free_slots(
            items=["primary", "colleague@example.com"],
            time_min="2024-01-15T09:00:00Z",
            time_max="2024-01-15T17:00:00Z",
            timeZone="America/Los_Angeles"
        )

    API Reference:
        https://developers.google.com/calendar/api/v3/reference/freebusy/query
    """
    client = CalendarAPIClient()

    endpoint = "/freeBusy"

    # Build request body with proper field names (camelCase as per API)
    request_body: Dict[str, Any] = {
        "timeMin": time_min,
        "timeMax": time_max,
        "timeZone": timeZone,
        "items": [{"id": cal_id} for cal_id in items]
    }

    if calendarExpansionMax is not None:
        request_body["calendarExpansionMax"] = calendarExpansionMax
    if groupExpansionMax is not None:
        request_body["groupExpansionMax"] = groupExpansionMax

    return await client.post(endpoint, json_data=request_body)

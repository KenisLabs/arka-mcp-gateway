"""
Watch for changes to Events resources.

Google Calendar API Reference:
https://developers.google.com/calendar/api/v3/reference/events/watch
"""
from typing import Any, Dict, Optional
from .client import CalendarAPIClient


async def events_watch(
    address: str,
    calendarId: str,
    id: str,
    params: Optional[Dict[str, Any]] = None,
    payload: Optional[bool] = None,
    token: Optional[str] = None,
    type: str = "web_hook"
) -> Dict[str, Any]:
    """
    Watch for changes to Events resources.

    Args:
        address: The address where notifications are delivered for this channel.
        calendarId: Calendar identifier. To retrieve calendar IDs call the calendarList.list method. If you...
        id: A UUID or similar unique string that identifies this channel.
        params: Additional parameters controlling delivery channel behavior. Optional.
        payload: A Boolean value to indicate whether payload is wanted. Optional.
        token: An arbitrary string delivered to the target address with each notification delivered ov...
        type: The type of delivery mechanism used for this channel.

    Returns:
        Dict containing the API response

    Example:
        result = await events_watch(...)
    """
    client = CalendarAPIClient()

    endpoint = f"/calendars/{calendarId}/events/watch"

    request_body = {}
    if type is not None:
        request_body["type"] = type
    if address is not None:
        request_body["address"] = address
    if token is not None:
        request_body["token"] = token
    if params is not None:
        request_body["params"] = params
    if id is not None:
        request_body["id"] = id
    if payload is not None:
        request_body["payload"] = payload

    return await client.post(endpoint, json_data=request_body)

"""
Watch for changes to Settings resources.

Google Calendar API Reference:
https://developers.google.com/calendar/api/v3/reference/settings/watch
"""
from typing import Any, Dict, Optional
from .client import CalendarAPIClient


async def settings_watch(
    address: str,
    id: str,
    type: str,
    params: Optional[Dict[str, Any]] = None,
    token: Optional[str] = None
) -> Dict[str, Any]:
    """
    Watch for changes to Settings resources.

    Args:
        address: The address where notifications are delivered for this channel.
        id: A UUID or similar unique string that identifies this channel.
        params: Additional parameters controlling delivery channel behavior.
        token: An arbitrary string delivered to the target address with each notification delivered ov...
        type: The type of delivery mechanism used for this channel. Valid values are "web_hook" (or "...

    Returns:
        Dict containing the API response

    Example:
        result = await settings_watch(...)
    """
    client = CalendarAPIClient()

    endpoint = "/users/me/settings/watch"

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

    return await client.post(endpoint, json_data=request_body)

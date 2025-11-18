"""
Returns all user settings for the authenticated user.

Google Calendar API Reference:
https://developers.google.com/calendar/api/v3/reference/settings/list
"""
from typing import Optional
from .client import CalendarAPIClient


async def settings_list(
    maxResults: Optional[int] = None,
    pageToken: Optional[str] = None,
    syncToken: Optional[str] = None
) -> dict:
    """
    Returns all user settings for the authenticated user.

    Args:
        maxResults: Maximum number of entries returned on one result page. By default the value is 100 entr...
        pageToken: Token specifying which result page to return.
        syncToken: Token obtained from the nextSyncToken field returned on the last page of results from t...

    Returns:
        Dict containing the API response

    Example:
        result = await settings_list(...)
    """
    client = CalendarAPIClient()

    endpoint = "/users/me/settings"

    params = {}
    if maxResults is not None:
        params["maxResults"] = maxResults
    if pageToken is not None:
        params["pageToken"] = pageToken
    if syncToken is not None:
        params["syncToken"] = syncToken

    return await client.get(endpoint, params=params)

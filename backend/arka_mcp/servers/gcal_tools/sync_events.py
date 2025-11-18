"""
Synchronizes Google Calendar events using sync tokens for incremental updates.

Google Calendar API Reference:
https://developers.google.com/calendar/api/v3/reference/events/list
"""
from typing import List, Optional, Dict, Any
from .client import CalendarAPIClient


async def sync_events(
    calendar_id: str = "primary",
    syncToken: Optional[str] = None,
    pageToken: Optional[str] = None,
    maxResults: Optional[int] = None,
    singleEvents: Optional[bool] = None,
    eventTypes: Optional[List[str]] = None,
    showDeleted: Optional[bool] = None
) -> Dict[str, Any]:
    """
    Synchronizes Google Calendar events with incremental sync support.

    Args:
        calendar_id: Google Calendar identifier ('primary' for main calendar)
        syncToken: Token for incremental sync (from previous response's nextSyncToken)
        pageToken: Token for pagination (from previous response's nextPageToken)
        maxResults: Max events per page (max 2500)
        singleEvents: If True, expands recurring events into individual instances
        eventTypes: Filter events by types (e.g., ['default', 'focusTime'])
        showDeleted: Include deleted events (useful with syncToken)

    Returns:
        Dict containing events list, nextPageToken, and nextSyncToken

    Example:
        # Initial sync
        result = await sync_events(calendar_id="primary", maxResults=100)
        sync_token = result.get("nextSyncToken")

        # Incremental sync
        result = await sync_events(calendar_id="primary", syncToken=sync_token)

    API Reference:
        https://developers.google.com/calendar/api/v3/reference/events/list
    """
    client = CalendarAPIClient()

    endpoint = f"/calendars/{calendar_id}/events"

    # Build query parameters (use camelCase as per API)
    params: Dict[str, Any] = {}

    if syncToken:
        params["syncToken"] = syncToken
    if pageToken:
        params["pageToken"] = pageToken
    if maxResults is not None:
        params["maxResults"] = maxResults
    if singleEvents is not None:
        params["singleEvents"] = singleEvents
    if showDeleted is not None:
        params["showDeleted"] = showDeleted
    if eventTypes:
        # eventTypes can be repeated or comma-separated
        params["eventTypes"] = eventTypes

    return await client.get(endpoint, params=params)

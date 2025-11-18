"""
List Google Calendar calendars.

Retrieves a paginated list of calendars from the user's calendar list,
with optional filtering and sync capabilities.

Google Calendar API Reference:
https://developers.google.com/calendar/api/v3/reference/calendarList/list
"""
from typing import Dict, Any, Optional
from .client import CalendarAPIClient
from .models import ListCalendarsRequest


async def list_calendars(
    max_results: int = 100,
    min_access_role: Optional[str] = None,
    page_token: Optional[str] = None,
    show_deleted: bool = False,
    show_hidden: bool = False,
    sync_token: Optional[str] = None
) -> Dict[str, Any]:
    """
    List calendars from the user's calendar list.

    Args:
        max_results: Maximum number of calendars to return (1-250, default 100)
        min_access_role: Filter by minimum access role (freeBusyReader, owner, reader, writer)
        page_token: Token for retrieving specific page of results
        show_deleted: Include deleted calendar list entries
        show_hidden: Include hidden calendars
        sync_token: Sync token to retrieve only changed entries

    Returns:
        Dict containing:
        - items: List of calendar resources
        - nextPageToken: Token for next page (if more results available)
        - nextSyncToken: Token for incremental sync

    Example:
        calendars = await list_calendars(max_results=50, show_hidden=True)
        for cal in calendars['items']:
            print(f"{cal['summary']}: {cal['id']}")
    """
    # Validate request parameters
    request = ListCalendarsRequest(
        max_results=max_results,
        min_access_role=min_access_role,
        page_token=page_token,
        show_deleted=show_deleted,
        show_hidden=show_hidden,
        sync_token=sync_token
    )

    # Build query parameters
    params = {
        "maxResults": request.max_results,
        "showDeleted": request.show_deleted,
        "showHidden": request.show_hidden,
    }

    # Add optional parameters
    if request.min_access_role:
        params["minAccessRole"] = request.min_access_role
    if request.page_token:
        params["pageToken"] = request.page_token
    if request.sync_token:
        params["syncToken"] = request.sync_token

    # Make API request
    client = CalendarAPIClient()
    return await client.get("/users/me/calendarList", params=params)

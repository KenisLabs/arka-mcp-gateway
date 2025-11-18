"""
Retrieves the list of access control rules (ACLs) for a specified calendar, providing the necessary 'rule_id' values required for updating specific ACL rules.

Google Calendar API Reference:
https://developers.google.com/calendar/api/v3/reference/acl/list
"""
from typing import Optional
from .client import CalendarAPIClient


async def list_acl_rules(
    calendar_id: str,
    max_results: Optional[int] = None,
    page_token: Optional[str] = None,
    show_deleted: Optional[bool] = None,
    sync_token: Optional[str] = None
) -> dict:
    """
    Retrieves the list of access control rules (ACLs) for a specified calendar, providing the necessary ...

    Args:
        calendar_id: Calendar identifier. To retrieve calendar IDs call the calendarList.list method. If you...
        max_results: Maximum number of entries returned on one result page. Optional. The default is 100.
        page_token: Token specifying which result page to return. Optional.
        show_deleted: Whether to include deleted ACLs in the result. Optional. The default is False.
        sync_token: Token obtained from the nextSyncToken field returned on the last page of a previous lis...

    Returns:
        Dict containing the API response

    Example:
        result = await list_acl_rules(...)
    """
    client = CalendarAPIClient()

    endpoint = f"/calendars/{calendar_id}/acl"

    return await client.get(endpoint)

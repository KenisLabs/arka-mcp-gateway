from typing import Any, Optional, List
from .client import JiraAPIClient

async def get_all_users(
    max_results: Optional[int] = None,
    start_at: Optional[int] = None,
) -> List[dict[str, Any]]:
    """
    Retrieves all users from the Jira instance including active, inactive, and other states.

    Args:
        max_results: Maximum number of items to return per page.
        start_at: 0-based index of the first item to return.

    Returns:
        A list of user detail dicts from the Jira API.
    """
    client = JiraAPIClient()
    # Use the Jira Cloud REST API endpoint for listing users
    endpoint = '/users/search'
    # If pagination parameters provided, fetch that page only
    if max_results is not None or start_at is not None:
        params: dict[str, Any] = {}
        if max_results is not None:
            params['maxResults'] = max_results
        if start_at is not None:
            params['startAt'] = start_at
        return await client.get(endpoint, params=params)
    # Otherwise iterate through all pages
    all_users: List[dict[str, Any]] = []
    start = 0
    per_page = 50
    while True:
        params = {'startAt': start, 'maxResults': per_page}
        page = await client.get(endpoint, params=params)
        if not page:
            break
        all_users.extend(page)
        if len(page) < per_page:
            break
        start += len(page)
    return all_users

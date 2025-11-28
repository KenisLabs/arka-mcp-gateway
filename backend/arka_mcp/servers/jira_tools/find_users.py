from typing import Any, Optional, List
from .client import JiraAPIClient

async def find_users(
    account_id: Optional[str] = None,
    query: Optional[str] = None,
    active: Optional[bool] = None,
    max_results: Optional[int] = None,
    start_at: Optional[int] = None,
) -> List[dict[str, Any]]:
    """
    Searches for Jira users by email, display name, or account ID.

    Args:
        account_id: Exact Atlassian account ID to fetch a single user.
        query: Text query to match against username or email.
        active: Filter by active status (True=active, False=inactive).
        max_results: Maximum number of items per page.
        start_at: 0-based index of the first item to return.

    Returns:
        A list of user detail dicts from the Jira API.

    Raises:
        ValueError: If neither 'account_id' nor 'query' is provided.
    """
    client = JiraAPIClient()
    # Fetch by account ID
    if account_id:
        endpoint = '/user'
        return await client.get(endpoint, params={'accountId': account_id})
    # Ensure we have a query string
    if not query:
        raise ValueError("Either 'query' or 'account_id' must be provided.")
    # Search via query
    endpoint = '/user/search'
    params: dict[str, Any] = {'query': query}
    if active is False:
        # include inactive users, then filter
        params['includeInactive'] = 'true'
    if max_results is not None:
        params['maxResults'] = max_results
    if start_at is not None:
        params['startAt'] = start_at
    users = await client.get(endpoint, params=params)
    # Filter out active/inactive if requested
    if active is False:
        users = [u for u in users if not u.get('active', True)]
    if active is True:
        users = [u for u in users if u.get('active', False)]
    return users

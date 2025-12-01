from typing import Any, Optional
from .client import JiraAPIClient

async def get_current_user(expand: Optional[str] = None) -> dict[str, Any]:
    """
    Retrieves detailed information about the currently authenticated Jira user.

    Args:
        expand: Comma-separated list of user properties to expand
            (e.g., 'groups', 'applicationRoles').

    Returns:
        A dict representing the Jira user JSON response.
    """
    client = JiraAPIClient()
    endpoint = "/myself"
    params: dict[str, Any] = {}
    if expand:
        params['expand'] = expand
    return await client.get(endpoint, params=params)

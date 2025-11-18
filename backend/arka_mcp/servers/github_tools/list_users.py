from typing import Dict, Any, Optional


async def list_users(
    start_cursor: Optional[str] = None, page_size: Optional[int] = None
) -> Dict[str, Any]:
    """
    Retrieve a paginated list of all users in the workspace accessible to the integration.

    This function calls the Notion API endpoint to list users in the workspace, optionally
    starting from a provided cursor and limiting the number of results per page. Guests are
    excluded from the results. Requires the integration to have user-information capabilities.
    """
    pass

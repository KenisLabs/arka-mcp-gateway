from typing import Dict, Optional, Any
from .base import get_notion_client, handle_notion_error, clean_notion_response


async def list_users(
    start_cursor: Optional[str] = None, page_size: Optional[int] = None
) -> Dict[str, Any]:
    """
    Retrieve a paginated list of all users in the workspace accessible to the integration.

    This function calls the Notion API endpoint to list users in the workspace, optionally
    starting from a provided cursor and limiting the number of results per page. Guests are
    excluded from the results. Requires the integration to have user-information capabilities.
    """
    try:
        notion = get_notion_client()

        params = {}
        if start_cursor:
            params["start_cursor"] = start_cursor
        if page_size:
            params["page_size"] = page_size

        response = notion.users.list(**params)
        return clean_notion_response(response)

    except Exception as e:
        return handle_notion_error(e)

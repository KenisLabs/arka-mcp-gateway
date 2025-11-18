from typing import Dict, Any, Optional
from .base import get_notion_client, handle_notion_error, clean_notion_response


async def search(
    query: Optional[str] = None,
    sort: Optional[Dict[str, Any]] = None,
    filter_conditions: Optional[Dict[str, Any]] = None,
    start_cursor: Optional[str] = None,
    page_size: Optional[int] = None,
) -> Dict[str, Any]:
    """
    Perform a search over pages and databases in the workspace that your integration has access to.

    This function maps to the Notion API “/v1/search” endpoint and allows you to:
    - Specify a free-text `query` string to match against page or database titles (and child pages) within the scope of the integration. :contentReference[oaicite:1]{index=1}
    - Apply a `filter_conditions` object to restrict results to only pages, only databases, or other object-types. :contentReference[oaicite:2]{index=2}
    - Define a `sort` object to order results by timestamp or other properties. :contentReference[oaicite:3]{index=3}
    - Use `start_cursor` for pagination to continue from a previous batch, and `page_size` to limit the number of results per request. :contentReference[oaicite:4]{index=4}
    - If no `query` is provided then it returns all accessible pages and databases shared with the integration (subject to other filter/sort parameters). :contentReference[oaicite:5]{index=5}

    Use this function when you want to discover or fetch pages/databases that your integration can access, especially for use-cases like onboarding, indexing or searching workspace content.
    """
    try:
        notion = get_notion_client()

        search_params = {}
        if query:
            search_params["query"] = query
        if sort:
            search_params["sort"] = sort
        if filter_conditions:
            search_params["filter"] = filter_conditions
        if start_cursor:
            search_params["start_cursor"] = start_cursor
        if page_size:
            search_params["page_size"] = page_size

        response = notion.search(**search_params)
        return clean_notion_response(response)

    except Exception as e:
        return handle_notion_error(e)

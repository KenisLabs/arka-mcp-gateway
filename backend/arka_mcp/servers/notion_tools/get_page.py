from typing import Dict, Any, Optional, List
from .base import get_notion_client, handle_notion_error, clean_notion_response


async def get_page(
    page_id: str, filter_properties: Optional[List[str]] = None
) -> Dict[str, Any]:
    """Retrieve a page from Notion."""
    try:
        notion = get_notion_client()

        params = {}
        if filter_properties:
            params["filter_properties"] = filter_properties

        response = notion.pages.retrieve(page_id, **params)
        return clean_notion_response(response)

    except Exception as e:
        return handle_notion_error(e)

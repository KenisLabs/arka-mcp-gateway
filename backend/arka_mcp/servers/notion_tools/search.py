"""
Search tool for Notion MCP server.

Searches across pages and databases in the workspace.
"""
from typing import Dict, Any, Optional
from .client import NotionAPIClient
import logging

logger = logging.getLogger(__name__)


async def search(
    query: Optional[str] = None,
    sort: Optional[Dict[str, Any]] = None,
    filter_conditions: Optional[Dict[str, Any]] = None,
    start_cursor: Optional[str] = None,
    page_size: Optional[int] = None,
) -> Dict[str, Any]:
    """
    Perform a search over pages and databases in the workspace.

    This function maps to the Notion API "/v1/search" endpoint and allows you to:
    - Specify a free-text `query` string to match against page or database titles
    - Apply a `filter_conditions` object to restrict results to only pages, only databases
    - Define a `sort` object to order results by timestamp or other properties
    - Use `start_cursor` for pagination to continue from a previous batch
    - Use `page_size` to limit the number of results per request
    - If no `query` is provided, returns all accessible pages and databases

    Args:
        query: Text to search for in titles and content
        sort: Sort criteria (e.g., {"direction": "ascending", "timestamp": "last_edited_time"})
        filter_conditions: Filter by object type (e.g., {"property": "object", "value": "page"})
        start_cursor: Pagination cursor from previous response
        page_size: Number of results per page (max 100)

    Returns:
        Search results with pages and databases

    Example:
        results = await search(query="Project")
        results = await search(filter_conditions={"property": "object", "value": "page"})
    """
    try:
        client = NotionAPIClient()

        # Build request body for POST /v1/search
        request_body = {}
        if query:
            request_body["query"] = query
        if sort:
            request_body["sort"] = sort
        if filter_conditions:
            request_body["filter"] = filter_conditions
        if start_cursor:
            request_body["start_cursor"] = start_cursor
        if page_size:
            request_body["page_size"] = page_size

        response = await client.post("/search", request_body)
        return response

    except Exception as e:
        logger.error(f"Failed to search Notion: {e}")
        return {
            "error": f"Failed to search: {str(e)}",
            "query": query
        }

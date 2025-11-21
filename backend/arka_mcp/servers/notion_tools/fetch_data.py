"""
Fetch Data tool for Notion MCP server.

Fetches pages and/or databases from the workspace with minimal data.
"""
from typing import Dict, Any, Optional
from .client import NotionAPIClient
import logging

logger = logging.getLogger(__name__)


async def fetch_data(
    query: Optional[str] = None,
    get_pages: Optional[bool] = True,
    get_databases: Optional[bool] = True,
    page_size: Optional[int] = None,
    get_all: Optional[bool] = False,
) -> Dict[str, Any]:
    """
    Fetch Notion items (pages and/or databases) with minimal data.

    Use this to get a quick overview of items in the workspace. For full details,
    use specific fetch methods for pages or databases.

    Args:
        query: Optional search query to filter items by title
               Example: "project" or "meeting notes"
        get_pages: Include pages in results (default: True)
        get_databases: Include databases in results (default: True)
        page_size: Number of results per page (max 100)
                   Example: 10
        get_all: If True, fetches all results by following pagination
                 If False, returns only first page (default: False)

    Returns:
        Search results with pages and/or databases

    Example:
        # Get all pages and databases
        results = await fetch_data()

        # Search for specific items
        results = await fetch_data(
            query="project",
            get_pages=True,
            get_databases=False
        )

        # Get everything with pagination
        results = await fetch_data(get_all=True)
    """
    try:
        client = NotionAPIClient()

        # Build filter based on get_pages and get_databases
        filter_obj = None
        if get_pages and not get_databases:
            filter_obj = {"property": "object", "value": "page"}
        elif get_databases and not get_pages:
            filter_obj = {"property": "object", "value": "database"}
        # If both True or both False, no filter (get everything)

        # Build initial request
        request_body = {}
        if query:
            request_body["query"] = query
        if filter_obj:
            request_body["filter"] = filter_obj
        if page_size:
            request_body["page_size"] = page_size

        # Make first request
        response = await client.post("/search", request_body)

        # If get_all is True, fetch all pages
        if get_all and response.get("has_more"):
            all_results = response.get("results", [])

            while response.get("has_more"):
                request_body["start_cursor"] = response["next_cursor"]
                response = await client.post("/search", request_body)
                all_results.extend(response.get("results", []))

            response["results"] = all_results
            response["has_more"] = False

        return response

    except Exception as e:
        logger.error(f"Failed to fetch data: {e}")
        return {
            "error": f"Failed to fetch data: {str(e)}"
        }

"""
Query Data Source tool for Notion MCP server.

Queries a Notion data source with filtering and pagination.
"""
from typing import Dict, Any, List, Optional
from .client import NotionAPIClient
import logging

logger = logging.getLogger(__name__)


async def query_data_source(
    data_source_id: str,
    filter: Optional[Dict[str, Any]] = None,
    sorts: Optional[List[Dict[str, Any]]] = None,
    page_size: Optional[int] = None,
    start_cursor: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Query a Notion data source with optional filtering, sorting, and pagination.

    Data sources are a feature in newer Notion API versions (2025-09-03+) that
    provide a unified way to query multiple types of data. This tool attempts
    to use the data source endpoint if available, falling back to database queries.

    Note: Data sources are part of Notion API v2025-09-03. This tool may not work
    with older API versions (like 2022-06-28).

    Args:
        data_source_id: UUID of the data source to query
                        Example: "668d797c-76fa-4934-9b05-ad288df2d136"
        filter: Optional filter object for queries
                Example: {"property": "Status", "select": {"equals": "Done"}}
        sorts: Optional list of sort objects
               Example: [{"property": "Name", "direction": "ascending"}]
        page_size: Optional number of results per page (max 100)
                   Example: 50
        start_cursor: Optional cursor for pagination
                      Example: "7c6b1c95-de50-45ca-94e6-af1d9fd295ab"

    Returns:
        Query results with items and pagination info

    Example:
        # Query a data source
        results = await query_data_source(
            data_source_id="668d797c-76fa-4934-9b05-ad288df2d136"
        )

        # Query with filter
        results = await query_data_source(
            data_source_id="668d797c-76fa-4934-9b05-ad288df2d136",
            filter={
                "property": "Status",
                "select": {"equals": "Active"}
            }
        )

        # Query with sorting
        results = await query_data_source(
            data_source_id="668d797c-76fa-4934-9b05-ad288df2d136",
            sorts=[{"property": "Created", "direction": "descending"}]
        )
    """
    try:
        client = NotionAPIClient()

        # Build request body
        request_body = {}

        if filter:
            request_body["filter"] = filter

        if sorts:
            request_body["sorts"] = sorts

        if page_size:
            request_body["page_size"] = min(page_size, 100)

        if start_cursor:
            request_body["start_cursor"] = start_cursor

        # Try data source endpoint (may not be available in older API versions)
        try:
            endpoint = f"/data_sources/{data_source_id}/query"
            response = await client.post(endpoint, request_body)
            return response
        except Exception as data_source_error:
            # Fall back to database query endpoint
            logger.warning(f"Data source endpoint not available, trying database endpoint: {data_source_error}")
            endpoint = f"/databases/{data_source_id}/query"
            response = await client.post(endpoint, request_body)
            return response

    except Exception as e:
        logger.error(f"Failed to query data source {data_source_id}: {e}")
        return {
            "error": f"Failed to query data source: {str(e)}",
            "data_source_id": data_source_id
        }

"""
Query Database tool for Notion MCP server.

Queries a database with optional sorting and pagination.
"""
from typing import Dict, Any, List, Optional
from .client import NotionAPIClient
import logging

logger = logging.getLogger(__name__)


async def query_database(
    database_id: str,
    sorts: Optional[List[Dict[str, Any]]] = None,
    page_size: Optional[int] = None,
    start_cursor: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Query a Notion database with optional sorting and pagination.

    Returns database rows (pages) with their properties. Use this for basic queries
    without filters. For filtered queries, use query_database_with_filter.

    Args:
        database_id: UUID of the database to query
                     Example: "668d797c-76fa-4934-9b05-ad288df2d136"
        sorts: Optional list of sort objects
               Example: [{"property": "Name", "direction": "ascending"}]
        page_size: Optional number of results per page (max 100)
                   Example: 50
        start_cursor: Optional cursor for pagination
                      Use next_cursor from previous response
                      Example: "7c6b1c95-de50-45ca-94e6-af1d9fd295ab"

    Returns:
        Query results with pages and pagination info

    Example:
        # Query all rows
        results = await query_database(
            database_id="668d797c-76fa-4934-9b05-ad288df2d136"
        )

        # Query with sorting
        results = await query_database(
            database_id="668d797c-76fa-4934-9b05-ad288df2d136",
            sorts=[
                {"property": "Name", "direction": "ascending"},
                {"property": "Created", "direction": "descending"}
            ]
        )

        # Query with pagination
        results = await query_database(
            database_id="668d797c-76fa-4934-9b05-ad288df2d136",
            page_size=25,
            start_cursor="previous_cursor_value"
        )
    """
    try:
        client = NotionAPIClient()

        # Build request body
        request_body = {}

        if sorts:
            request_body["sorts"] = sorts

        if page_size:
            request_body["page_size"] = min(page_size, 100)  # Notion max is 100

        if start_cursor:
            request_body["start_cursor"] = start_cursor

        # Query database
        endpoint = f"/databases/{database_id}/query"
        response = await client.post(endpoint, request_body)

        return response

    except Exception as e:
        logger.error(f"Failed to query database {database_id}: {e}")
        return {
            "error": f"Failed to query database: {str(e)}",
            "database_id": database_id
        }

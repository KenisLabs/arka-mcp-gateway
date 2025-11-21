"""
Query Database with Filter tool for Notion MCP server.

Queries a database with advanced filtering, sorting, and pagination.
"""
from typing import Dict, Any, List, Optional
from .client import NotionAPIClient
import logging

logger = logging.getLogger(__name__)


async def query_database_with_filter(
    database_id: str,
    filter: Optional[Dict[str, Any]] = None,
    sorts: Optional[List[Dict[str, Any]]] = None,
    page_size: Optional[int] = None,
    start_cursor: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Query a Notion database with advanced filtering capabilities.

    Supports complex filter conditions (and, or, property filters) along with
    sorting and pagination. Use this for filtered queries; for simple queries
    without filters, use query_database.

    Args:
        database_id: UUID of the database to query
                     Example: "668d797c-76fa-4934-9b05-ad288df2d136"
        filter: Optional filter object for complex queries
                Supports property filters, compound filters (and/or)
                Example: {"property": "Status", "select": {"equals": "Done"}}
        sorts: Optional list of sort objects
               Example: [{"property": "Name", "direction": "ascending"}]
        page_size: Optional number of results per page (max 100)
                   Example: 50
        start_cursor: Optional cursor for pagination
                      Use next_cursor from previous response
                      Example: "7c6b1c95-de50-45ca-94e6-af1d9fd295ab"

    Returns:
        Filtered query results with pages and pagination info

    Example:
        # Filter by status
        results = await query_database_with_filter(
            database_id="668d797c-76fa-4934-9b05-ad288df2d136",
            filter={
                "property": "Status",
                "select": {"equals": "In Progress"}
            }
        )

        # Complex filter with AND condition
        results = await query_database_with_filter(
            database_id="668d797c-76fa-4934-9b05-ad288df2d136",
            filter={
                "and": [
                    {"property": "Status", "select": {"equals": "Done"}},
                    {"property": "Priority", "select": {"equals": "High"}}
                ]
            }
        )

        # Filter with sorting
        results = await query_database_with_filter(
            database_id="668d797c-76fa-4934-9b05-ad288df2d136",
            filter={"property": "Status", "select": {"equals": "Done"}},
            sorts=[{"property": "Created", "direction": "descending"}]
        )

        # Filter by date range
        results = await query_database_with_filter(
            database_id="668d797c-76fa-4934-9b05-ad288df2d136",
            filter={
                "property": "Due Date",
                "date": {
                    "on_or_after": "2024-01-01"
                }
            }
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
            request_body["page_size"] = min(page_size, 100)  # Notion max is 100

        if start_cursor:
            request_body["start_cursor"] = start_cursor

        # Query database with filter
        endpoint = f"/databases/{database_id}/query"
        response = await client.post(endpoint, request_body)

        return response

    except Exception as e:
        logger.error(f"Failed to query database with filter {database_id}: {e}")
        return {
            "error": f"Failed to query database with filter: {str(e)}",
            "database_id": database_id
        }

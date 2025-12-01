"""
Tool to list comments of a Jira issue with pagination and optional rendered body.

Use case:
    Instead of calling `get_issue` to fetch comments, use this tool for efficient comment listings.
"""
from typing import Any, Dict, Optional
from .client import JiraAPIClient


async def list_issue_comments(
    issue_id_or_key: str,
    expand: Optional[str] = None,
    max_results: Optional[int] = 50,
    start_at: Optional[int] = 0,
    order_by: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Retrieves comments from a Jira issue.

    Args:
        issue_id_or_key: The numeric ID or key of the Jira issue.
        expand: Comma-separated entities to expand (e.g., 'renderedBody').
        max_results: Maximum comments per page.
        start_at: Pagination start index.
        order_by: Field to sort by (e.g., 'created').

    Returns:
        A dict with comments list, pagination info (maxResults, startAt, total), and success flag.
    """
    client = JiraAPIClient()
    params: Dict[str, Any] = {"startAt": start_at, "maxResults": max_results}
    if expand:
        params["expand"] = expand
    if order_by:
        params["orderBy"] = order_by
    # Fetch comments
    result = await client.get(f"/issue/{issue_id_or_key}/comment", params=params)
    # Structure response
    return {
        "data": {
            "comments": result.get("comments", []),
            "maxResults": result.get("maxResults"),
            "startAt": result.get("startAt"),
            "total": result.get("total"),
        },
        "successful": True,
    }

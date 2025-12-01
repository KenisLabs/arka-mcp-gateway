"""
Tool to retrieve all visible Jira projects with pagination and filtering.

Use case:
    Fetch a paginated list of projects matching filters instead of manual catalog APIs.
"""
from typing import Any, Dict, List, Optional
from .client import JiraAPIClient


async def get_all_projects(
    action: Optional[str] = None,
    categoryId: Optional[int] = None,
    expand: Optional[str] = None,
    maxResults: Optional[int] = None,
    name: Optional[str] = None,
    orderBy: Optional[str] = None,
    properties: Optional[List[str]] = None,
    query: Optional[str] = None,
    startAt: Optional[int] = None,
    status: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    Retrieves all visible projects using Jira's paginated project search API.

    Args:
        action: Filter by user permission (e.g., 'view', 'browse', 'create').
        categoryId: Project category ID to filter.
        expand: Comma-separated entities to expand (description, issueTypes, lead, projectKeys).
        maxResults: Maximum items per page.
        name: Deprecated; project name to search (maps to query).
        orderBy: Field to sort by, prefix with '-' for descending.
        properties: List of project property keys to include.
        query: Text to search in project name or key.
        startAt: Pagination start index.
        status: List of project status values (live, archived, deleted).

    Returns:
        A dict with raw API response under 'data' and success flag.
    """
    client = JiraAPIClient()
    params: Dict[str, Any] = {}
    if action:
        params['action'] = action
    if categoryId is not None:
        params['categoryId'] = categoryId
    if expand:
        params['expand'] = expand
    if maxResults is not None:
        params['maxResults'] = maxResults
    # Map deprecated name to query if query not provided
    if name and not query:
        params['query'] = name
    if orderBy:
        params['orderBy'] = orderBy
    if properties:
        params['properties'] = ','.join(properties)
    if query:
        params['query'] = query
    if startAt is not None:
        params['startAt'] = startAt
    if status:
        params['status'] = ','.join(status)
    result = await client.get('/project/search', params=params)
    return {'data': result, 'successful': True}

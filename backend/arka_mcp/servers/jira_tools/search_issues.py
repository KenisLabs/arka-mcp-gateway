from typing import Any, Optional, List
from .client import JiraAPIClient


async def search_issues(
    jql: str,
    max_results: int = 50,
    next_page_token: Optional[str] = None,
    expand: Optional[str] = None,
    fields: Optional[List[str]] = None,
    fields_by_keys: Optional[bool] = None,
    properties: Optional[List[str]] = None,
    reconcile_issues: Optional[List[int]] = None,
) -> dict[str, Any]:
    """
    Executes a Jira JQL search with pagination and optional expansions.

    Args:
        jql: Jira Query Language string to execute.
        max_results: Maximum issues per page.
        next_page_token: Token for pagination (startAt index as string).
        expand: Comma-separated list of entities to expand (e.g., 'changelog').
        fields: Specific issue fields to retrieve.
        fields_by_keys: Identify fields by keys instead of IDs.
        properties: List of issue property keys to include.
        reconcile_issues: List of issue IDs for read-after-write reconciliation.

    Returns:
        A dict representing the Jira search JSON response.

    Raises:
        ValueError: If 'jql' parameter is missing.
    """
    if not jql:
        raise ValueError("Parameter 'jql' is required for search_issues.")
    # Prepare base search parameters
    params: dict[str, Any] = {
        'jql': jql,
        'startAt': int(next_page_token) if next_page_token else 0,
        'maxResults': max_results,
    }
    # Always expand field names by default; append any additional expansions
    base_expand = 'names'
    if expand:
        # Avoid duplicate values
        params['expand'] = f"{base_expand},{expand}"
    else:
        params['expand'] = base_expand
    if fields:
        params['fields'] = ','.join(fields)
    if fields_by_keys is not None:
        params['fieldsByKeys'] = str(fields_by_keys).lower()
    if properties:
        params['properties'] = ','.join(properties)
    if reconcile_issues:
        params['reconcileIssues'] = ','.join(str(i) for i in reconcile_issues)
    client = JiraAPIClient()
    return await client.get('/search/jql', params=params)

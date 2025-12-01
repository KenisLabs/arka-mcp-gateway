"""
Tool to retrieve available workflow transitions for a Jira issue.

Use case:
    Fetch this instead of embedding transitions in `get_issue` when you only need workflow actions.
"""
from typing import Any, Dict, Optional
from .client import JiraAPIClient


async def get_transitions(
    issue_id_or_key: str,
    expand: Optional[str] = None,
    include_unavailable_transitions: Optional[bool] = None,
    skip_remote_only_condition: Optional[bool] = None,
    sort_by_ops_bar_and_status: Optional[bool] = None,
    transition_id: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Retrieves available workflow transitions for a Jira issue.

    Args:
        issue_id_or_key: The ID or key of the Jira issue (e.g., 'PROJ-123').
        expand: Comma-separated list to expand (e.g., 'transitions.fields').
        include_unavailable_transitions: Include transitions not currently allowed.
        skip_remote_only_condition: Skip remote-only condition checks.
        sort_by_ops_bar_and_status: Sort by UI operations bar and status.
        transition_id: Specific transition ID to retrieve (returns single transition).

    Returns:
        A dict with key 'transitions' listing transition objects and success flag.
    """
    client = JiraAPIClient()
    params: Dict[str, Any] = {}
    if expand:
        params['expand'] = expand
    if include_unavailable_transitions is not None:
        params['includeUnavailableTransitions'] = str(include_unavailable_transitions).lower()
    if skip_remote_only_condition is not None:
        params['skipRemoteOnlyCondition'] = str(skip_remote_only_condition).lower()
    if sort_by_ops_bar_and_status is not None:
        params['sortByOpsBarAndStatus'] = str(sort_by_ops_bar_and_status).lower()
    if transition_id:
        params['transitionId'] = transition_id
    result = await client.get(f"/issue/{issue_id_or_key}/transitions", params=params)
    return {"data": {"transitions": result.get('transitions', [])}, "successful": True}

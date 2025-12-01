"""
Tool to retrieve Jira issue fields metadata.

Use case:
    Discover field IDs and configurations before creating or editing issues.
"""
from typing import Any, Dict, Optional
from .client import JiraAPIClient


async def get_fields(
    custom_only: Optional[bool] = False,
    projectId: Optional[str] = None,
    issue_type: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Retrieves Jira issue field metadata, optionally filtered by project or issue type.

    Args:
        custom_only: If True, return only custom fields.
        projectId: Project ID to scope fields.
        issue_type: Issue type ID or name to scope fields (requires projectId).

    Returns:
        A dict with list of fields under 'data.fields' and success flag.
    """
    client = JiraAPIClient()
    params: Dict[str, Any] = {}
    # Use field search endpoint
    if custom_only:
        params['custom'] = 'true'
    if projectId:
        params['projectId'] = projectId
    if issue_type:
        params['issueType'] = issue_type
    # Call Jira field search
    result = await client.get('/field/search', params=params)
    fields = result.get('values', []) if isinstance(result, dict) else []
    return {'data': {'fields': fields}, 'successful': True}

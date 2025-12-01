"""
Tool to retrieve details of a Jira project by ID or key.

Use case:
    Fetch project metadata without listing all projects.
"""
from typing import Any, Dict, Optional
from .client import JiraAPIClient


async def get_project(
    project_id_or_key: str,
    expand: Optional[str] = None,
    properties: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Retrieves details of a Jira project by its ID or key.

    Args:
        project_id_or_key: Numeric ID or project key (e.g., 'PROJ').
        expand: Comma-separated entities to expand (description, issueTypes, lead, projectKeys).
        properties: Comma-separated project property keys to include.

    Returns:
        A dict with raw project data under 'data' and success flag.
    """
    client = JiraAPIClient()
    params: Dict[str, Any] = {}
    if expand:
        params['expand'] = expand
    if properties:
        params['properties'] = properties
    result = await client.get(f"/project/{project_id_or_key}", params=params)
    return {'data': result, 'successful': True}

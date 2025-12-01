from typing import Any
from .client import JiraAPIClient


async def get_issue(
    issue_id_or_key: str,
    expand: str | None = None,
    fields: list[str] | None = None,
    fields_by_keys: bool | None = None,
    properties: list[str] | None = None,
    update_history: bool = True,
) -> dict[str, Any]:
    """
    Retrieves a Jira issue by ID or key with optional query parameters.

    Note:
        This tool returns full issue details and serves as a fallback when no specialized tool applies.
        For listing comments on an issue, use the `list_issue_comments` tool instead of embedding them here.

    Args:
        issue_id_or_key: The ID (e.g., "10000") or key (e.g., "PROJ-123") of the Jira issue.
        expand: Comma-separated list of entities to expand (e.g., 'changelog').
        fields: List of field names or IDs to include (e.g., ['summary', 'status']).
        fields_by_keys: Interpret `fields` as field keys instead of IDs.
        properties: List of issue property keys to include in the response.
        update_history: Whether viewing the issue should be added to the 'Recently viewed' list (default: True).

    Returns:
        A dict representing the Jira issue JSON response.
    """
    client = JiraAPIClient()
    endpoint = f"/issue/{issue_id_or_key}"
    # Build query parameters
    params: dict[str, Any] = {}
    if expand is not None:
        params['expand'] = expand
    if fields is not None:
        # Jira expects comma-separated field list
        params['fields'] = ','.join(fields)
    if fields_by_keys is not None:
        params['fieldsByKeys'] = str(fields_by_keys).lower()
    if properties is not None:
        params['properties'] = ','.join(properties)
    # Always include updateHistory parameter (defaults to true)
    params['updateHistory'] = str(update_history).lower()
    return await client.get(endpoint, params=params)

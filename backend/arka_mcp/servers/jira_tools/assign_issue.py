"""
Tool to assign a Jira issue to a user, default assignee, or unassign.

Use case:
    Set or clear the assignee without fetching full issue details.
"""
from typing import Any, Dict, Optional
from .client import JiraAPIClient


async def assign_issue(
    issue_id_or_key: str,
    account_id: Optional[str] = None,
    assignee_name: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Assigns a Jira issue to the given account ID, default assignee ("-1"), or unassigns.

    Args:
        issue_id_or_key: The ID or key of the Jira issue.
        account_id: Atlassian account ID to assign, '-1' for project default, or None to unassign.
        assignee_name: Email or display name to assign if account_id is not provided.

    Returns:
        A dict with success flag.
    """
    client = JiraAPIClient()
    # Build payload
    payload: Dict[str, Any] = {}
    if account_id is not None:
        # Explicit assign or unassign (None yields null in JSON)
        payload['accountId'] = account_id
    elif assignee_name is not None:
        # Let Jira resolve name/email
        payload['name'] = assignee_name
    else:
        # No fields => unassign
        payload['accountId'] = None
    # Execute assignment
    await client.put(f"/issue/{issue_id_or_key}/assignee", json=payload)
    return {"data": {}, "successful": True}

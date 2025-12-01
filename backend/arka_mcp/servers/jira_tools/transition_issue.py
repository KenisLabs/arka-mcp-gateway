"""
Tool to transition a Jira issue to a different workflow state.

Use case:
    Apply a workflow transition without retrieving full issue details manually.
"""
from typing import Any, Dict, Optional
from .client import JiraAPIClient
"""import removed for no longer fetching updated issue status"""


async def transition_issue(
    issue_id_or_key: str,
    transition_id_or_name: str,
    assignee: Optional[str] = None,
    assignee_name: Optional[str] = None,
    comment: Optional[str] = None,
    resolution: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Transitions a Jira issue to a different workflow state with optional comment and field updates.

    Args:
        issue_id_or_key: The ID or key of the Jira issue (e.g., 'PROJ-123').
        transition_id_or_name: The ID or name of the transition to apply.
        assignee: Account ID of user to assign during transition.
        assignee_name: Name/email of user to assign if ID not provided.
        comment: Comment text to add with the transition.
        resolution: Resolution name to set if supported by the transition screen.

    Returns:
        A dict with transition_name, new_status, issue_key, browser_url, and success flag.
    """
    client = JiraAPIClient()
    # Build payload
    payload: Dict[str, Any] = {"transition": {}, "fields": {}, "update": {}}
    # Transition selector
    if transition_id_or_name.isdigit():
        payload["transition"]["id"] = transition_id_or_name
    else:
        payload["transition"]["name"] = transition_id_or_name
    # Field updates
    if assignee:
        payload["fields"]["assignee"] = {"accountId": assignee}
    elif assignee_name:
        payload["fields"]["assignee"] = assignee_name
    if resolution:
        payload["fields"]["resolution"] = {"name": resolution}
    # Add comment via update operations
    if comment:
        # Atlassian Document Format for comment
        adf = {
            "type": "doc",
            "version": 1,
            "content": [{"type": "paragraph", "content": [{"type": "text", "text": comment}]}],
        }
        payload["update"]["comment"] = [{"add": {"body": adf}}]
    # Clean up empty sections
    if not payload["fields"]:
        payload.pop("fields")
    if not payload["update"]:
        payload.pop("update")
    # Execute transition
    await client.post(f"/issue/{issue_id_or_key}/transitions", json=payload)
    # Construct browser URL
    base_url = client.instance_url.rstrip('/') if client.instance_url else ''
    browser_url = f"{base_url}/browse/{issue_id_or_key}"
    return {
        "data": {
            "success": True,
            "transition_name": transition_id_or_name,
            "issue_key": issue_id_or_key,
            "browser_url": browser_url,
        },
        "successful": True,
    }

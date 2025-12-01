"""
Tool to update an existing Jira issue with field values and operations.
"""
from typing import Any, Dict, Optional
from .client import JiraAPIClient
from .get_issue import get_issue


async def edit_issue(
    issue_id_or_key: str,
    fields: Optional[Dict[str, Any]] = None,
    summary: Optional[str] = None,
    description: Optional[str] = None,
    assignee: Optional[str] = None,
    assignee_name: Optional[str] = None,
    priority_id_or_name: Optional[str] = None,
    labels: Optional[list[str]] = None,
    due_date: Optional[str] = None,
    update: Optional[Dict[str, Any]] = None,
    notify_users: bool = True,
    override_editable_flag: bool = False,
    override_screen_security: bool = False,
    return_issue: bool = False,
) -> Dict[str, Any]:
    """
    Updates a Jira issue by merging provided direct field parameters with the `fields` dict.

    Args:
        issue_id_or_key: ID or key of the issue to update.
        fields: Raw fields dict for update.
        summary: New summary.
        description: New description.
        assignee: Account ID of assignee.
        assignee_name: Name/email of assignee if ID not provided.
        priority_id_or_name: Priority ID or name.
        labels: New list of labels (replaces existing).
        due_date: Due date in YYYY-MM-DD format.
        update: Advanced update operations dict.
        notify_users: Whether to send notifications (default: True).
        override_editable_flag: Bypass editable restrictions.
        override_screen_security: Bypass screen security restrictions.
        return_issue: If True, returns full updated issue data.

    Returns:
        Success flag and optionally full issue data.
    """
    client = JiraAPIClient()
    # Build payload
    payload: Dict[str, Any] = {"notifyUsers": notify_users,
                                "overrideEditableFlag": override_editable_flag,
                                "overrideScreenSecurity": override_screen_security,
                                "fields": {},
                                "update": update or {}}
    # Merge direct fields
    if summary is not None:
        payload["fields"]["summary"] = summary
    if description is not None:
        payload["fields"]["description"] = description
    # Assignee precedence
    if assignee:
        payload["fields"]["assignee"] = {"accountId": assignee}
    elif assignee_name is not None:
        payload["fields"]["assignee"] = assignee_name
    if priority_id_or_name:
        if priority_id_or_name.isdigit():
            payload["fields"]["priority"] = {"id": priority_id_or_name}
        else:
            payload["fields"]["priority"] = {"name": priority_id_or_name}
    if labels is not None:
        payload["fields"]["labels"] = labels
    if due_date is not None:
        payload["fields"]["duedate"] = due_date
    if fields:
        # fields param takes lowest precedence
        payload["fields"].update(fields)
    # Send update request
    await client.put(f"/issue/{issue_id_or_key}", json=payload)
    # Prepare response
    data: Dict[str, Any] = {"success": True, "issue_key": issue_id_or_key}
    if return_issue:
        # Fetch latest issue data
        issue_data = await get_issue(issue_id_or_key)
        data["issue_data"] = issue_data
    return {"data": data, "successful": True}

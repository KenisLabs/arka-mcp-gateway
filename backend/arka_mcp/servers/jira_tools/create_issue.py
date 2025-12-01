"""
Tool to create a new Jira issue (e.g., bug, task, story) in a specified project.
"""
from typing import Any, Dict, List, Optional
from .client import JiraAPIClient


async def create_issue(
    project_key: str,
    summary: str,
    issue_type: str = "Task",
    description: Optional[str] = None,
    environment: Optional[str] = None,
    components: Optional[List[str]] = None,
    fix_versions: Optional[List[str]] = None,
    versions: Optional[List[str]] = None,
    due_date: Optional[str] = None,
    labels: Optional[List[str]] = None,
    priority: Optional[str] = None,
    reporter: Optional[str] = None,
    assignee: Optional[str] = None,
    assignee_name: Optional[str] = None,
    sprint_id: Optional[int] = None,
) -> Dict[str, Any]:
    """
    Creates a new Jira issue using the REST API.

    Args:
        project_key: Key of the Jira project (e.g., 'PROJ').
        summary: Brief, descriptive title for the issue.
        issue_type: Type of the issue (e.g., 'Bug', 'Task'). Defaults to 'Task'.
        description: Detailed description in markdown format.
        environment: Environment details in markdown.
        components: List of component IDs.
        fix_versions: List of fix version IDs.
        versions: List of affected version IDs.
        due_date: Due date (YYYY-MM-DD).
        labels: List of labels to add.
        priority: Priority ID or name.
        reporter: Reporter account ID.
        assignee: Assignee account ID.
        assignee_name: Assignee name or email if account ID is not provided.
        sprint_id: Sprint ID to assign, if applicable.

    Returns:
        The created issue data including 'id', 'key', 'self', and 'browser_url'.
    """
    client = JiraAPIClient()
    # Build payload
    payload: Dict[str, Any] = {"fields": {"project": {"key": project_key}, "summary": summary, "issuetype": {"name": issue_type}}}
    fields = payload["fields"]
    if description is not None:
        # Jira Cloud expects Atlassian Document Format (ADF) for rich text description
        if isinstance(description, str):
            fields["description"] = {
                "type": "doc",
                "version": 1,
                "content": [
                    {"type": "paragraph", "content": [
                        {"type": "text", "text": description}
                    ]}
                ],
            }
        else:
            # assume provided in ADF format
            fields["description"] = description
    if environment is not None:
        # Jira Cloud expects Atlassian Document Format (ADF) for rich text environment
        if isinstance(environment, str):
            fields["environment"] = {
                "type": "doc",
                "version": 1,
                "content": [
                    {"type": "paragraph", "content": [
                        {"type": "text", "text": environment}
                    ]}
                ],
            }
        else:
            # assume provided in ADF format
            fields["environment"] = environment
    if components:
        # Jira API expects list of objects with id
        fields["components"] = [{"id": c} for c in components]
    if fix_versions:
        fields["fixVersions"] = [{"id": v} for v in fix_versions]
    if versions:
        fields["versions"] = [{"id": v} for v in versions]
    if due_date:
        fields["duedate"] = due_date
    if labels:
        fields["labels"] = labels
    if priority:
        # Accept numeric ID or name
        if priority.isdigit():
            fields["priority"] = {"id": priority}
        else:
            fields["priority"] = {"name": priority}
    if reporter:
        fields["reporter"] = {"accountId": reporter}
    # Assignee precedence: account ID over name
    if assignee:
        fields["assignee"] = {"accountId": assignee}
    elif assignee_name:
        fields["assignee"] = assignee_name
    if sprint_id is not None:
        # Common custom field for sprint, may vary per instance
        fields.setdefault("customfield_10007", sprint_id)
    # Send request
    result = await client.post("/issue", json=payload)
    # Construct browser URL using the instance URL if available
    key = result.get('key')
    base_url = client.instance_url or f"https://api.atlassian.com/ex/jira/{client.cloud_id}"
    # Ensure no trailing slash
    base_url = base_url.rstrip('/')
    browser_url = f"{base_url}/browse/{key}"
    return {
        "data": {
            "id": result.get("id"),
            "key": result.get("key"),
            "self": result.get("self"),
            "browser_url": browser_url,
        },
        "successful": True,
    }

from typing import Any, List, Optional

async def update_issue(
    owner: str,
    repo: str,
    issue_number: int,
    title: Optional[str] = None,
    body: Optional[str] = None,
    state: Optional[str] = None,
    milestone: Optional[str] = None,
    labels: Optional[List[str]] = None,
    assignee: Optional[str] = None,
    assignees: Optional[List[str]] = None,
    state_reason: Optional[str] = None,
) -> Any:
    """
    Updates an existing GitHub issue's attributes.

    Sends data to GitHub `/repos/{owner}/{repo}/issues/{issue_number}` endpoint.

    Args:
        owner: Repository owner's username or organization.
        repo: Repository name (without .git).
        issue_number: The number identifying the issue to update.
        title: New title for the issue.
        body: New body content; send None to clear.
        state: New state: 'open' or 'closed'.
        milestone: Milestone ID or title; send None to clear.
        labels: List of labels to set; send [] to clear.
        assignee: (Deprecated) Single assignee; send None to unassign.
        assignees: List of assignees to set; send [] to clear.
        state_reason: Reason for state change; only used if state changes.

    Returns:
        Parsed JSON response from the GitHub API.

    Example:
        result = await update_issue(
            owner="octocat",
            repo="Hello-World",
            issue_number=1347,
            state="closed",
            state_reason="completed",
        )
    """
    from .client import GitHubAPIClient

    client = GitHubAPIClient()
    endpoint = f"/repos/{owner}/{repo}/issues/{issue_number}"
    json_data: dict = {}
    if title is not None:
        json_data["title"] = title
    if body is not None:
        json_data["body"] = body
    if state is not None:
        json_data["state"] = state
    if state_reason is not None:
        json_data["state_reason"] = state_reason
    if milestone is not None:
        json_data["milestone"] = milestone
    if labels is not None:
        json_data["labels"] = labels
    if assignee is not None:
        json_data["assignee"] = assignee
    if assignees is not None:
        json_data["assignees"] = assignees
    return await client.patch(endpoint, json_data)

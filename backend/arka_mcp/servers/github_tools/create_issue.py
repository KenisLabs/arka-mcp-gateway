from typing import Any, List, Optional


async def create_issue(
    owner: str,
    repo: str,
    title: str,
    body: Optional[str] = None,
    assignee: Optional[str] = None,
    assignees: Optional[List[str]] = None,
    labels: Optional[List[str]] = None,
    milestone: Optional[str] = None,
) -> Any:
    """
    Creates a new issue in a GitHub repository.

    Sends data to GitHub `/repos/{owner}/{repo}/issues` endpoint.

    Args:
        owner: The username or organization that owns the repository.
        repo: The name of the repository (without .git).
        title: The title of the new issue.
        body: The detailed textual content of the issue.
        assignee: (Deprecated) Single user login to assign.
        assignees: List of user logins to assign.
        labels: List of labels to apply.
        milestone: Milestone ID to associate.

    Returns:
        Parsed JSON response from the GitHub API.

    Example:
        result = await create_issue(
            owner="octocat",
            repo="Hello-World",
            title="New Feature Request",
            body="Please add a dark mode.",
            assignees=["octocat", "hubot"],
            labels=["example-label"],
        )
    """
    from .client import GitHubAPIClient

    client = GitHubAPIClient()
    endpoint = f"/repos/{owner}/{repo}/issues"
    json_data = {"title": title}
    if body is not None:
        json_data["body"] = body
    if assignee is not None:
        json_data["assignee"] = assignee
    if assignees is not None:
        json_data["assignees"] = assignees
    if labels is not None:
        json_data["labels"] = labels
    if milestone is not None:
        json_data["milestone"] = milestone
    return await client.post(endpoint, json_data)

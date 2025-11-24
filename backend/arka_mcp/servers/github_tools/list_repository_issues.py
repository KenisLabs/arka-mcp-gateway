from typing import Any, Optional


async def list_repository_issues(
    owner: str,
    repo: str,
    assignee: Optional[str] = None,
    creator: Optional[str] = None,
    direction: str = "desc",
    labels: Optional[str] = None,
    mentioned: Optional[str] = None,
    milestone: Optional[str] = None,
    state: str = "open",
    since: Optional[str] = None,
    sort: str = "created",
    page: int = 1,
    per_page: int = 30,
) -> Any:
    """
    Lists issues (including pull requests) for a specified GitHub repository, with filtering, sorting, and pagination.

    Retrieves data via GitHub `/repos/{owner}/{repo}/issues` endpoint.

    Args:
        owner: Repository owner's username or organization.
        repo: Repository name (without .git).
        assignee: Filter by assignee's username ('none' for unassigned, '*' for any).
        creator: Filter by issue creator's username.
        direction: Sort direction 'asc' or 'desc' (default 'desc').
        labels: Comma-separated list of labels to filter by.
        mentioned: Filter issues mentioning a user by username.
        milestone: Filter by milestone number, '*' for any, or 'none'.
        state: Issue state: 'open', 'closed', or 'all' (default 'open').
        since: ISO 8601 timestamp to filter issues updated at or after this time.
        sort: Field to sort by: 'created', 'updated', or 'comments' (default 'created').
        page: Page number for results (default 1).
        per_page: Number of results per page (default 30).

    Returns:
        Parsed JSON response from the GitHub API.

    Example:
        result = await list_repository_issues(
            owner="octocat",
            repo="Hello-World",
            labels="bug,help wanted",
            state="open",
            page=1,
            per_page=20,
        )
    """
    from .client import GitHubAPIClient

    client = GitHubAPIClient()
    endpoint = f"/repos/{owner}/{repo}/issues"
    params = {
        "direction": direction,
        "state": state,
        "sort": sort,
        "page": page,
        "per_page": per_page,
    }
    if assignee is not None:
        params["assignee"] = assignee
    if creator is not None:
        params["creator"] = creator
    if labels:
        params["labels"] = labels
    if mentioned:
        params["mentioned"] = mentioned
    if milestone:
        params["milestone"] = milestone
    if since:
        params["since"] = since
    return await client.get(endpoint, params=params)

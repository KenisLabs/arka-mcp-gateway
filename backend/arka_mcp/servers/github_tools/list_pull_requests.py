from typing import Any, Optional

async def list_pull_requests(
    owner: str,
    repo: str,
    state: str = "open",
    base: Optional[str] = None,
    head: Optional[str] = None,
    sort: str = "created",
    direction: Optional[str] = None,
    page: int = 1,
    per_page: int = 30,
) -> Any:
    """
    Lists pull requests for a specified GitHub repository.

    Retrieves data via GitHub `/repos/{owner}/{repo}/pulls` endpoint.

    Args:
        owner: Repository owner's username or organization.
        repo: Repository name (without .git).
        state: Pull request state: 'open', 'closed', or 'all' (default 'open').
        base: Filter by base branch name (e.g., 'main').
        head: Filter by head branch name (e.g., 'user:feature-branch').
        sort: Sort field: 'created', 'updated', 'popularity', 'long-running' (default 'created').
        direction: Sort direction 'asc' or 'desc' (default depends on sort).
        page: Page number of results (default 1).
        per_page: Results per page (default 30).

    Returns:
        Parsed JSON response from the GitHub API.

    Example:
        result = await list_pull_requests(
            owner="octocat",
            repo="Hello-World",
            state="all",
            base="main",
            sort="updated",
            direction="desc",
            page=1,
            per_page=20,
        )
    """
    from .client import GitHubAPIClient

    client = GitHubAPIClient()
    endpoint = f"/repos/{owner}/{repo}/pulls"
    params = {"state": state, "sort": sort, "page": page, "per_page": per_page}
    if base:
        params["base"] = base
    if head:
        params["head"] = head
    if direction:
        params["direction"] = direction
    return await client.get(endpoint, params=params)

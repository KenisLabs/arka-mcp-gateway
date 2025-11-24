from typing import Any

async def get_pull_request(
    owner: str,
    repo: str,
    pull_number: int,
) -> Any:
    """
    Retrieves detailed information about a specific pull request.

    Retrieves data via GitHub `/repos/{owner}/{repo}/pulls/{pull_number}` endpoint.

    Args:
        owner: Repository owner's username or organization.
        repo: Repository name (without .git).
        pull_number: The number identifying the pull request.

    Returns:
        Parsed JSON response from the GitHub API.

    Example:
        result = await get_pull_request(owner="octocat", repo="Hello-World", pull_number=1347)
    """
    from .client import GitHubAPIClient

    client = GitHubAPIClient()
    endpoint = f"/repos/{owner}/{repo}/pulls/{pull_number}"
    return await client.get(endpoint)

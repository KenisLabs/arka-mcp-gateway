from typing import Any


async def get_repository(
    owner: str,
    repo: str,
) -> Any:
    """
    Retrieves detailed information about an existing and accessible GitHub repository.

    Retrieves data via GitHub `/repos/{owner}/{repo}` endpoint.

    Args:
        owner: The username or organization that owns the repository.
        repo: The name of the repository (without .git).

    Returns:
        Parsed JSON response from the GitHub API.

    Example:
        result = await get_repository(owner="octocat", repo="Hello-World")
    """
    from .client import GitHubAPIClient

    client = GitHubAPIClient()
    return await client.get(f"/repos/{owner}/{repo}")

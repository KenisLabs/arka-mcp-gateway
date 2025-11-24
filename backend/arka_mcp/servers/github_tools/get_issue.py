from typing import Any

async def get_issue(
    owner: str,
    repo: str,
    issue_number: int,
) -> Any:
    """
    Retrieves detailed information about a specific issue in a GitHub repository.

    Retrieves data via GitHub `/repos/{owner}/{repo}/issues/{issue_number}` endpoint.

    Args:
        owner: The username or organization that owns the repository.
        repo: The name of the repository (without .git).
        issue_number: The number identifying the issue.

    Returns:
        Parsed JSON response from the GitHub API.

    Example:
        result = await get_issue(owner="octocat", repo="Hello-World", issue_number=1347)
    """
    from .client import GitHubAPIClient

    client = GitHubAPIClient()
    endpoint = f"/repos/{owner}/{repo}/issues/{issue_number}"
    return await client.get(endpoint)

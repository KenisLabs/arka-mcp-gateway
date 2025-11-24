from typing import Any, Optional


async def get_repository_content(
    owner: str,
    repo: str,
    path: str,
    ref: Optional[str] = None,
) -> Any:
    """
    Retrieves a file's Base64 content or lists a directory's contents from a repository.

    Retrieves data via GitHub `/repos/{owner}/{repo}/contents/{path}` endpoint.

    Args:
        owner: Owner of the repository.
        repo: Name of the repository.
        path: File or directory path in the repository.
        ref: The name of the commit, branch, or tag. Defaults to default branch.

    Returns:
        Parsed JSON response from the GitHub API.
    """
    from .client import GitHubAPIClient

    client = GitHubAPIClient()
    endpoint = f"/repos/{owner}/{repo}/contents/{path}"
    params = {}
    if ref:
        params["ref"] = ref
    return await client.get(endpoint, params=params)

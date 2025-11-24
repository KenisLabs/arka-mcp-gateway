from typing import Any


async def list_organizations(
    page: int = 1,
    per_page: int = 30,
) -> Any:
    """
    Lists organizations the authenticated GitHub user is a member of, returning details for each organization.

    Retrieves data via GitHub `/user/orgs` endpoint.

    Args:
        page: Page number of results to retrieve (default: 1).
        per_page: Number of results per page (default: 30, maximum: 100).

    Returns:
        Parsed JSON response from the GitHub API.

    Example:
        result = await list_organizations(page=1, per_page=50)
    """
    from .client import GitHubAPIClient

    client = GitHubAPIClient()
    params = {"page": page, "per_page": per_page}
    return await client.get("/user/orgs", params=params)

from typing import Any


async def get_authenticated_user() -> Any:
    """
    Gets the profile information for the currently authenticated GitHub user.

    Retrieves data via GitHub `/user` endpoint.

    Returns:
        Parsed JSON response from the GitHub API.

    Example:
        result = await get_authenticated_user()
    """
    from .client import GitHubAPIClient

    client = GitHubAPIClient()
    return await client.get("/user")

from typing import Any, Optional


async def list_repositories_for_authenticated_user(
    page: int = 1,
    per_page: int = 30,
    sort: str = "full_name",
    direction: str = "asc",
    type: str = "all",
    since: Optional[str] = None,
    before: Optional[str] = None,
    raw_response: bool = False,
) -> Any:
    """
    Lists repositories for the authenticated user.

    Retrieves data via GitHub `/user/repos` endpoint.

    Args:
        page: Page number of results (default 1).
        per_page: Number of results per page (default 30).
        sort: Field to sort by (default "full_name").
        direction: Sort direction, "asc" or "desc" (default "asc").
        type: Repository type filter: all, owner, public, private, member.
        since: ISO 8601 timestamp to filter repos updated at or after this time.
        before: ISO 8601 timestamp to filter repos updated before this time.
        raw_response: If True, return full API response.

    Returns:
        Parsed JSON response from the GitHub API.
    """
    from .client import GitHubAPIClient

    client = GitHubAPIClient()
    params = {
        "page": page,
        "per_page": per_page,
        "sort": sort,
        "direction": direction,
        "type": type,
    }
    if since:
        params["since"] = since
    if before:
        params["before"] = before
    response = await client.get("/user/repos", params=params)
    filtered_repos = []
    for repo in response:
        filtered_repos.append(
            {
                "id": repo.get("id"),
                "name": repo.get("name"),
                "full_name": repo.get("full_name"),
                "private": repo.get("private"),
                "owner": {
                    "login": repo.get("owner", {}).get("login"),
                    "id": repo.get("owner", {}).get("id"),
                    "type": repo.get("owner", {}).get("type"),
                },
                "html_url": repo.get("html_url"),
                "description": repo.get("description"),
                "fork": repo.get("fork"),
                "language": repo.get("language"),
                "default_branch": repo.get("default_branch"),
                "archived": repo.get("archived"),
                "disabled": repo.get("disabled"),
                "permissions": repo.get("permissions"),
            }
        )
    return filtered_repos

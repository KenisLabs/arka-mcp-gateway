from typing import Any, Optional


async def search_issues_and_pull_requests(
    q: str,
    order: str = "desc",
    page: int = 1,
    per_page: int = 30,
    sort: Optional[str] = None,
) -> Any:
    """
    Search GitHub for issues and pull requests using a query string.

    Retrieves data via GitHub `/search/issues` endpoint.

    The `q` parameter must be a **GitHub search query string** with qualifiers to specify
    what to search for. This allows filtering for issues, pull requests, repositories, labels,
    authors, states, and more.

    **Examples of query construction:**

    - **Search open issues in a repo:**
        repo:owner/repo is:issue is:open
    - **Search closed pull requests in a repo:**
        repo:owner/repo is:pr is:closed
    - **Search by author:**
        author:username is:issue is:open
    - **Search by labels:**
        repo:owner/repo is:issue label:"bug"

    Args:
        q: GitHub search query string with qualifiers.
            - Use `is:issue` to search for issues.
            - Use `is:pr` to search for pull requests.
            - Combine with other qualifiers like `state:open`, `author:username`, `label:bug`.
        order: Sort order 'asc' or 'desc' (default 'desc').
        page: Page number of results (default 1).
        per_page: Number of results per page (default 30).
        sort: Field to sort by if specified (e.g., 'created', 'updated', 'comments').
        raw_response: If True, return full API response.

    Returns:
        Parsed JSON response from the GitHub API.

    Example:
        result = await search_issues_and_pull_requests(
            q="repo:octocat/Hello-World is:pr is:open",
            sort="created",
            order="desc",
            page=1,
            per_page=50,
        )

    """
    from .client import GitHubAPIClient

    client = GitHubAPIClient()
    params = {"q": q, "order": order, "page": page, "per_page": per_page}
    if sort:
        params["sort"] = sort
    return await client.get("/search/issues", params=params)

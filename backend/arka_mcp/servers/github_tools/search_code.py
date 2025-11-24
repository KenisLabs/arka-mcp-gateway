from typing import Any, Optional


async def search_code(
    q: str,
    sort: Optional[str] = None,
    order: str = "desc",
    page: int = 1,
    per_page: int = 30,
) -> Any:
    """
    Search code file contents and paths on GitHub repositories.

    Retrieves data via the GitHub `/search/code` endpoint.

    The `q` parameter must be a **GitHub code search query string** with qualifiers.
    Qualifiers allow filtering by repository, path, language, filename, and more.

    **Examples of query construction:**

    - **Search for a function in Python files in a specific repo:**
        function in:file repo:owner/repo language:python
    - **Search for a filename across all repositories:**
        filename:config.yaml
    - **Search within a specific path in a repository:**
        class in:file path:/src repo:owner/repo
    - **Search by user-owned repository:**
        TODO in:file user:username

    Args:
        q: Code search query string with qualifiers.
            - `in:file` to search within file contents.
            - `filename:name` to search for specific filenames.
            - `path:path/to/dir` to filter files in a specific path.
            - `repo:owner/repo` to search within a specific repository.
            - `language:lang` to filter by programming language.
        sort: Deprecated. Sort field (e.g., 'indexed').
        order: Sort order 'asc' or 'desc' (default 'desc').
        page: Page number of results (default 1).
        per_page: Results per page (default 30).

    Returns:
        Parsed JSON response from the GitHub API.

    Example:
        result = await search_code(
            q="function in:file repo:octocat/Hello-World language:python",
            sort="indexed",
            order="desc",
            page=1,
            per_page=30,
        )

    Reference:
        https://docs.github.com/en/search-github/searching-on-github/searching-code
    """
    from .client import GitHubAPIClient

    client = GitHubAPIClient()
    params = {"q": q, "order": order, "page": page, "per_page": per_page}
    if sort:
        params["sort"] = sort
    return await client.get("/search/code", params=params)

"""
Slack Search All Tool.

Searches for both messages and files across the workspace using search.all.

Slack API Reference:
https://api.slack.com/methods/search.all
"""
from typing import Dict, Any, Optional
from .client import SlackAPIClient


async def search_all(
    query: str,
    count: Optional[int] = 20,
    highlight: Optional[bool] = True,
    page: Optional[int] = 1,
    sort: Optional[str] = "score",
    sort_dir: Optional[str] = "desc",
    team_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Search for both messages and files across the Slack workspace.

    Args:
        query: Search query with optional operators (e.g., "budget from:@alice in:#finance")
        count: Results per page (default: 20, max: 100)
        highlight: Highlight matching terms (default: True)
        page: Page number for pagination (default: 1)
        sort: Sort order - "score" or "timestamp" (default: "score")
        sort_dir: Sort direction - "desc" or "asc" (default: "desc")
        team_id: Team ID for Enterprise Grid (optional)

    Returns:
        Dict containing:
        - ok: Success status
        - query: The search query used
        - messages: Messages search results with:
          - total: Total number of message matches
          - matches: Array of message objects
          - paging: Pagination info
        - files: Files search results with:
          - total: Total number of file matches
          - matches: Array of file objects
          - paging: Pagination info

    Raises:
        ValueError: If Slack API returns an error

    Example:
        # Search for everything containing "budget"
        result = await search_all(query="budget")

        # Search with operators
        result = await search_all(
            query="quarterly report from:@alice in:#finance after:2024-01-01"
        )

        # Search sorted by timestamp
        result = await search_all(
            query="meeting notes",
            sort="timestamp",
            sort_dir="desc"
        )

        # Paginate results
        result = await search_all(
            query="project update",
            count=50,
            page=2
        )

    Search Operators:
        - from:@username - From specific user
        - in:#channel - In specific channel
        - after:YYYY-MM-DD - After date
        - before:YYYY-MM-DD - Before date
        - has::emoji: - Has specific reaction
        - is:starred - Starred items only
        - from:me - From authenticated user
        - to:me - Mentioning authenticated user
        - "exact phrase" - Exact phrase match

    Notes:
        - Requires search:read scope
        - Searches both messages and files in a single query
        - Results respect user's channel membership and permissions
        - Highlighting wraps matches in <em> tags when enabled
        - Score sorting ranks by relevance
        - Timestamp sorting orders chronologically
        - Maximum 100 results per page
        - Use search.messages or search.files for type-specific searches
    """
    client = SlackAPIClient()

    params: Dict[str, Any] = {
        "query": query,
        "count": min(count, 100) if count else 20,
        "page": page
    }

    if highlight is not None:
        params["highlight"] = highlight
    if sort:
        params["sort"] = sort
    if sort_dir:
        params["sort_dir"] = sort_dir
    if team_id:
        params["team_id"] = team_id

    return await client.get("search.all", params)

"""
Slack Search Messages Tool.

Searches for messages across the workspace using search.messages.

Slack API Reference:
https://api.slack.com/methods/search.messages
"""
from typing import Dict, Any, Optional
from .client import SlackAPIClient


async def search_messages(
    query: str,
    count: Optional[int] = 20,
    highlight: Optional[bool] = True,
    page: Optional[int] = 1,
    sort: Optional[str] = "score",
    sort_dir: Optional[str] = "desc"
) -> Dict[str, Any]:
    """
    Search for messages across the Slack workspace.

    Args:
        query: Search query (supports operators like from:@user, in:#channel, etc.)
        count: Number of results to return per page (default: 20, max: 100)
        highlight: Highlight matching terms in results (default: True)
        page: Page number for pagination (1-indexed, default: 1)
        sort: Sort order - "score" (relevance) or "timestamp" (default: "score")
        sort_dir: Sort direction - "desc" or "asc" (default: "desc")

    Returns:
        Dict containing:
        - ok: Success status
        - query: The search query used
        - messages: Search results object with:
          - total: Total number of matching messages
          - matches: Array of message objects with:
            - type: "message"
            - user: User ID who posted
            - username: Username
            - text: Message text (with highlights if enabled)
            - ts: Message timestamp
            - channel: Channel object with id and name
            - permalink: Direct link to message
            - previous: Context message before match
            - previous_2: Second context message before match
            - next: Context message after match
            - next_2: Second context message after match
          - pagination: Pagination info with page, page_count, total_count
          - paging: Additional paging details

    Raises:
        ValueError: If Slack API returns an error

    Example:
        # Simple text search
        result = await search_messages(
            query="project update"
        )
        # Returns: {
        #   "ok": True,
        #   "query": "project update",
        #   "messages": {
        #     "total": 42,
        #     "matches": [
        #       {
        #         "type": "message",
        #         "user": "U1234567890",
        #         "username": "john",
        #         "text": "Here's the <em>project</em> <em>update</em> for this week",
        #         "ts": "1234567890.123456",
        #         "channel": {
        #           "id": "C1234567890",
        #           "name": "general"
        #         },
        #         "permalink": "https://workspace.slack.com/archives/C1234/p1234567890123456",
        #         ...
        #       },
        #       ...
        #     ],
        #     "pagination": {
        #       "page": 1,
        #       "page_count": 3,
        #       "total_count": 42
        #     }
        #   }
        # }

        # Search from specific user
        result = await search_messages(
            query="from:@john status update"
        )

        # Search in specific channel
        result = await search_messages(
            query="in:#engineering deployment"
        )

        # Search with date range
        result = await search_messages(
            query="meeting notes after:2024-01-01 before:2024-12-31"
        )

        # Search with multiple operators
        result = await search_messages(
            query='from:@sarah in:#design "final mockup" has:link'
        )

        # Get more results, sorted by date
        result = await search_messages(
            query="important announcement",
            count=50,
            sort="timestamp",
            sort_dir="desc"
        )

        # Paginate through results
        result = await search_messages(
            query="bug report",
            page=2,
            count=20
        )

    Search Query Operators:
        - from:@username - Messages from specific user
        - in:#channel - Messages in specific channel
        - "exact phrase" - Exact phrase match
        - after:YYYY-MM-DD - Messages after date
        - before:YYYY-MM-DD - Messages before date
        - on:YYYY-MM-DD - Messages on specific date
        - has:link - Messages with links
        - has:reaction - Messages with reactions
        - has:star - Starred messages
        - has:pin - Pinned messages
        - is:starred - User's starred messages
        - from:me - Messages from authenticated user
        - to:@username - DMs to specific user
        - in:@username - DMs with specific user

    Notes:
        - Requires search:read scope
        - Search is case-insensitive by default
        - Use quotes for exact phrase matching
        - Highlight wraps matches in <em> tags
        - Results include context messages before/after match
        - Maximum 100 results per page
        - Pagination uses 1-based indexing
        - sort="score" ranks by relevance (recommended)
        - sort="timestamp" orders chronologically
        - Returns error "invalid_query" for malformed queries
        - Rate limits apply (Tier 2: 20+ requests per minute)
        - Search includes all channels user has access to
        - Private channels only searchable if user is member
        - Does not search archived channels by default
        - Supports boolean AND/OR operators
    """
    client = SlackAPIClient()

    # Build request parameters
    params: Dict[str, Any] = {
        "query": query,
        "count": min(count, 100) if count else 20,  # Cap at API maximum
        "page": page
    }

    if highlight is not None:
        params["highlight"] = highlight
    if sort:
        params["sort"] = sort
    if sort_dir:
        params["sort_dir"] = sort_dir

    # Use GET method for search.messages
    return await client.get_method("search.messages", params)

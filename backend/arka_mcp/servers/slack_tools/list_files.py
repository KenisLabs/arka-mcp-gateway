"""
Slack List Files Tool.

Lists files with optional filters using files.list.

Slack API Reference:
https://api.slack.com/methods/files.list
"""
from typing import Dict, Any, Optional
from .client import SlackAPIClient


async def list_files(
    channel: Optional[str] = None,
    count: Optional[int] = 100,
    page: Optional[int] = 1,
    show_files_hidden_by_limit: Optional[bool] = False,
    team_id: Optional[str] = None,
    ts_from: Optional[str] = None,
    ts_to: Optional[str] = None,
    types: Optional[str] = None,
    user: Optional[str] = None
) -> Dict[str, Any]:
    """
    List files in Slack with optional filters.

    Args:
        channel: Filter by channel ID (e.g., "C1234567890")
        count: Number of items to return per page (default: 100, max: 1000)
        page: Page number of results (default: 1)
        show_files_hidden_by_limit: Show files hidden by limit (default: False)
        team_id: Team ID for Enterprise Grid workspaces
        ts_from: Filter files created after this timestamp (e.g., "1234567890")
        ts_to: Filter files created before this timestamp (e.g., "1234567890")
        types: Filter by file types, comma-separated (e.g., "images,pdfs,zips")
        user: Filter by user ID who created the file (e.g., "U1234567890")

    Returns:
        Dict containing:
        - ok: Success status
        - files: Array of file objects
        - paging: Pagination information with count, total, page, pages

    Raises:
        ValueError: If Slack API returns an error

    Example:
        # List all files
        result = await list_files()

        # List files in specific channel
        result = await list_files(channel="C1234567890")

        # List files by user
        result = await list_files(user="U1234567890")

        # List files by type
        result = await list_files(types="images,pdfs")

        # List files in date range
        result = await list_files(
            ts_from="1609459200",
            ts_to="1640995200"
        )

    Notes:
        - Requires files:read scope
        - Returns files visible to the authenticated user
        - Supports pagination with count and page parameters
        - File types: all, spaces, snippets, images, gdocs, zips, pdfs
        - Results ordered by created timestamp (newest first)
    """
    client = SlackAPIClient()

    params: Dict[str, Any] = {
        "count": min(count, 1000) if count else 100,
        "page": page
    }

    if channel:
        params["channel"] = channel
    if show_files_hidden_by_limit:
        params["show_files_hidden_by_limit"] = show_files_hidden_by_limit
    if team_id:
        params["team_id"] = team_id
    if ts_from:
        params["ts_from"] = ts_from
    if ts_to:
        params["ts_to"] = ts_to
    if types:
        params["types"] = types
    if user:
        params["user"] = user

    return await client.get("files.list", params)

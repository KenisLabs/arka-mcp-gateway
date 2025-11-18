"""
Slack Get File Info Tool.

Gets detailed information about a file using files.info.

Slack API Reference:
https://api.slack.com/methods/files.info
"""
from typing import Dict, Any, Optional
from .client import SlackAPIClient


async def get_file_info(
    file: str,
    count: Optional[int] = 100,
    cursor: Optional[str] = None,
    limit: Optional[int] = 0,
    page: Optional[int] = 1
) -> Dict[str, Any]:
    """
    Get detailed information about a Slack file.

    Args:
        file: File ID (e.g., "F1234567890")
        count: Number of items to return per page (default: 100, max: 1000)
        cursor: Pagination cursor for comments
        limit: Limit for file comments (default: 0 for all)
        page: Page number of results (default: 1)

    Returns:
        Dict containing:
        - ok: Success status
        - file: Detailed file object with all metadata
        - comments: Array of comment objects
        - paging: Pagination information

    Raises:
        ValueError: If Slack API returns an error

    Example:
        # Get file info
        result = await get_file_info(file="F1234567890")

        # Get file info with comments
        result = await get_file_info(
            file="F1234567890",
            count=50
        )

    Notes:
        - Requires files:read scope
        - Returns full file metadata including shares, comments, and reactions
        - File must be visible to the authenticated user
    """
    client = SlackAPIClient()

    params: Dict[str, Any] = {
        "file": file,
        "count": min(count, 1000) if count else 100,
        "page": page
    }

    if cursor:
        params["cursor"] = cursor
    if limit:
        params["limit"] = limit

    return await client.get("files.info", params)

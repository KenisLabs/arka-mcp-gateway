"""
Slack Delete File Tool.

Deletes a file by ID using files.delete.

Slack API Reference:
https://api.slack.com/methods/files.delete
"""
from typing import Dict, Any
from .client import SlackAPIClient


async def delete_file(file: str) -> Dict[str, Any]:
    """
    Delete a file from Slack.

    Args:
        file: File ID to delete (e.g., "F1234567890")

    Returns:
        Dict containing:
        - ok: Success status

    Raises:
        ValueError: If Slack API returns an error

    Example:
        # Delete a file
        result = await delete_file(file="F1234567890")
        # Returns: {"ok": True}

    Notes:
        - Requires files:write scope
        - Only the file owner or workspace admin can delete files
        - File deletion is permanent and cannot be undone
        - All comments and shares are also deleted
    """
    client = SlackAPIClient()

    params = {"file": file}

    return await client.post("files.delete", params)

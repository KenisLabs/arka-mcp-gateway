"""
Slack List Reminders Tool.

Lists all reminders using reminders.list.

Slack API Reference:
https://api.slack.com/methods/reminders.list
"""
from typing import Dict, Any, Optional
from .client import SlackAPIClient


async def list_reminders(
    team_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    List all reminders for the authenticated user.

    Args:
        team_id: Team ID for Enterprise Grid (optional)

    Returns:
        Dict containing:
        - ok: Success status
        - reminders: Array of reminder objects, each with:
          - id: Reminder ID
          - creator: User ID who created
          - user: User ID who will receive
          - text: Reminder text
          - recurring: Whether recurring
          - time: Unix timestamp when reminder fires
          - complete_ts: Completion timestamp (0 if not complete)

    Raises:
        ValueError: If Slack API returns an error

    Example:
        # List all reminders
        result = await list_reminders()
        # Returns: {
        #   "ok": True,
        #   "reminders": [
        #     {
        #       "id": "Rm1234567890",
        #       "creator": "U1234567890",
        #       "user": "U1234567890",
        #       "text": "Submit weekly report",
        #       "recurring": False,
        #       "time": 1640995200,
        #       "complete_ts": 0
        #     },
        #     ...
        #   ]
        # }

    Notes:
        - Requires reminders:read scope
        - Returns both active and completed reminders
        - Includes both one-time and recurring reminders
        - Results not paginated (returns all reminders)
        - Only returns reminders visible to authenticated user
    """
    client = SlackAPIClient()

    params: Dict[str, Any] = {}

    if team_id:
        params["team_id"] = team_id

    return await client.get("reminders.list", params)

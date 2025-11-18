"""
Slack Get Reminder Info Tool.

Gets information about a reminder using reminders.info.

Slack API Reference:
https://api.slack.com/methods/reminders.info
"""
from typing import Dict, Any, Optional
from .client import SlackAPIClient


async def get_reminder_info(
    reminder: str,
    team_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Get detailed information about a specific reminder.

    Args:
        reminder: Reminder ID (e.g., "Rm1234567890")
        team_id: Team ID for Enterprise Grid (optional)

    Returns:
        Dict containing:
        - ok: Success status
        - reminder: Reminder object with:
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
        # Get reminder details
        result = await get_reminder_info(reminder="Rm1234567890")
        # Returns: {
        #   "ok": True,
        #   "reminder": {
        #     "id": "Rm1234567890",
        #     "creator": "U1234567890",
        #     "user": "U1234567890",
        #     "text": "Submit weekly report",
        #     "recurring": False,
        #     "time": 1640995200,
        #     "complete_ts": 0
        #   }
        # }

    Notes:
        - Requires reminders:read scope
        - Can only view your own reminders
        - Returns error "not_found" if reminder doesn't exist
        - complete_ts is 0 for incomplete reminders
        - complete_ts contains Unix timestamp when reminder was completed
    """
    client = SlackAPIClient()

    params: Dict[str, Any] = {
        "reminder": reminder
    }

    if team_id:
        params["team_id"] = team_id

    return await client.get("reminders.info", params)

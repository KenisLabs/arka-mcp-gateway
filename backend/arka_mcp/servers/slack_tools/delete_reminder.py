"""
Slack Delete Reminder Tool.

Deletes a reminder using reminders.delete.

Slack API Reference:
https://api.slack.com/methods/reminders.delete
"""
from typing import Dict, Any, Optional
from .client import SlackAPIClient


async def delete_reminder(
    reminder: str,
    team_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Delete a Slack reminder.

    Args:
        reminder: Reminder ID to delete (e.g., "Rm1234567890")
        team_id: Team ID for Enterprise Grid (optional)

    Returns:
        Dict containing:
        - ok: Success status

    Raises:
        ValueError: If Slack API returns an error

    Example:
        # Delete a reminder
        result = await delete_reminder(reminder="Rm1234567890")
        # Returns: {"ok": True}

    Notes:
        - Requires reminders:write scope
        - Can only delete your own reminders
        - Returns error "not_found" if reminder doesn't exist
        - Returns error "cannot_delete_others" if trying to delete another user's reminder
        - Deleting a recurring reminder removes all future occurrences
    """
    client = SlackAPIClient()

    params: Dict[str, Any] = {
        "reminder": reminder
    }

    if team_id:
        params["team_id"] = team_id

    return await client.post("reminders.delete", params)

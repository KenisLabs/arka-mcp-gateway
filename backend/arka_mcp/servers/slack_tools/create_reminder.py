"""
Slack Create Reminder Tool.

Creates a reminder using reminders.add.

Slack API Reference:
https://api.slack.com/methods/reminders.add
"""
from typing import Dict, Any, Optional
from .client import SlackAPIClient


async def create_reminder(
    text: str,
    time: str,
    user: Optional[str] = None,
    recurrence: Optional[str] = None,
    team_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create a Slack reminder.

    Args:
        text: Reminder text (e.g., "Submit weekly report")
        time: When to remind - Unix timestamp or natural language (e.g., "in 20 minutes", "tomorrow at 9am")
        user: User ID to receive reminder (default: authenticated user)
        recurrence: Recurrence pattern (e.g., "every weekday", "every week")
        team_id: Team ID for Enterprise Grid

    Returns:
        Dict containing:
        - ok: Success status
        - reminder: Reminder object with:
          - id: Reminder ID
          - creator: User ID who created
          - user: User ID who will receive
          - text: Reminder text
          - recurring: Whether recurring
          - time: Unix timestamp
          - complete_ts: Completion timestamp (0 if not complete)

    Raises:
        ValueError: If Slack API returns an error

    Example:
        # Create reminder with natural language
        result = await create_reminder(
            text="Submit weekly report",
            time="tomorrow at 9am"
        )

        # Create reminder with Unix timestamp
        result = await create_reminder(
            text="Follow up with client",
            time="1640995200"
        )

        # Create recurring reminder
        result = await create_reminder(
            text="Daily standup",
            time="every weekday at 10am"
        )

        # Create reminder for another user
        result = await create_reminder(
            text="Review pull request",
            time="in 2 hours",
            user="U1234567890"
        )

    Notes:
        - Requires reminders:write scope
        - Supports natural language time (e.g., "in 20 minutes", "tomorrow at 3pm")
        - Supports Unix timestamps for precise scheduling
        - Recurring reminders: "every day", "every weekday", "every week", "every month"
        - Maximum text length is 1024 characters
        - Can create reminders for other users in your workspace
        - Reminders respect user's timezone
        - Returns error "cannot_parse" if time format invalid
    """
    client = SlackAPIClient()

    params: Dict[str, Any] = {
        "text": text,
        "time": time
    }

    if user:
        params["user"] = user
    if recurrence:
        params["recurrence"] = recurrence
    if team_id:
        params["team_id"] = team_id

    return await client.post("reminders.add", params)

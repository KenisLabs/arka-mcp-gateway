"""
Slack Find User by Email Tool.

Finds a user by their email address using users.lookupByEmail.

Slack API Reference:
https://api.slack.com/methods/users.lookupByEmail
"""
from typing import Dict, Any
from .client import SlackAPIClient


async def find_user_by_email(email: str) -> Dict[str, Any]:
    """
    Find a Slack user by their email address.

    Args:
        email: Email address to search for (e.g., "alice@example.com")

    Returns:
        Dict containing:
        - ok: Success status
        - user: User object with:
          - id: User ID (e.g., "U1234567890")
          - team_id: Team ID
          - name: Username
          - deleted: Whether user is deleted
          - real_name: Full name
          - tz: Timezone
          - tz_label: Timezone label
          - tz_offset: Timezone offset in seconds
          - profile: User profile with:
            - email: Email address
            - first_name: First name
            - last_name: Last name
            - real_name: Full name
            - display_name: Display name
            - phone: Phone number
            - image_*: Avatar URLs
            - status_text: Current status text
            - status_emoji: Current status emoji
          - is_admin: Whether user is admin
          - is_owner: Whether user is owner
          - is_primary_owner: Whether user is primary owner
          - is_restricted: Whether user is restricted
          - is_ultra_restricted: Whether user is ultra restricted
          - is_bot: Whether user is bot
          - is_app_user: Whether user is app user

    Raises:
        ValueError: If Slack API returns an error

    Example:
        # Find user by email
        result = await find_user_by_email(email="alice@example.com")
        # Returns: {
        #   "ok": True,
        #   "user": {
        #     "id": "U1234567890",
        #     "name": "alice",
        #     "real_name": "Alice Johnson",
        #     "profile": {
        #       "email": "alice@example.com",
        #       "first_name": "Alice",
        #       "last_name": "Johnson",
        #       ...
        #     },
        #     ...
        #   }
        # }

        # Get user ID from email for other operations
        result = await find_user_by_email(email="bob@example.com")
        user_id = result["user"]["id"]
        # Use user_id in other API calls...

    Notes:
        - Requires users:read.email scope
        - Email must match a workspace member's email
        - Returns error "users_not_found" if email doesn't match any user
        - Case-insensitive email matching
        - Only returns active workspace members
        - Useful for converting email to user ID for other operations
        - Does not work with guest accounts in some workspace configurations
    """
    client = SlackAPIClient()

    params = {"email": email}

    return await client.get("users.lookupByEmail", params)

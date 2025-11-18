"""
Slack Get User Info Tool.

Gets detailed information about a Slack user using users.info.

Slack API Reference:
https://api.slack.com/methods/users.info
"""
from typing import Dict, Any, Optional
from .client import SlackAPIClient


async def get_user_info(
    user: str,
    include_locale: Optional[bool] = False
) -> Dict[str, Any]:
    """
    Get detailed information about a Slack user.

    Args:
        user: User ID (e.g., U1234567890) or username
        include_locale: Include user locale information (default: False)

    Returns:
        Dict containing:
        - ok: Success status
        - user: User object with detailed information including:
          - id: User ID
          - team_id: Workspace/team ID
          - name: Username
          - real_name: Full name
          - deleted: True if user is deactivated
          - color: Hex color code for user
          - profile: User profile object with:
            - title: Job title
            - phone: Phone number
            - skype: Skype username
            - real_name: Full name
            - real_name_normalized: Normalized full name
            - display_name: Display name
            - display_name_normalized: Normalized display name
            - email: Email address (requires users:read.email scope)
            - image_*: Profile image URLs (24, 32, 48, 72, 192, 512, 1024)
            - status_text: Status text
            - status_emoji: Status emoji
            - status_expiration: Unix timestamp of status expiration
            - team: Team ID
          - is_admin: True if workspace admin
          - is_owner: True if workspace owner
          - is_primary_owner: True if primary workspace owner
          - is_restricted: True if guest user
          - is_ultra_restricted: True if single-channel guest
          - is_bot: True if bot user
          - is_app_user: True if app user
          - updated: Unix timestamp of last profile update
          - has_2fa: True if 2FA enabled
          - locale: User locale (if include_locale=True)
          - tz: Timezone identifier (e.g., "America/Los_Angeles")
          - tz_label: Timezone label (e.g., "Pacific Daylight Time")
          - tz_offset: Timezone offset in seconds

    Raises:
        ValueError: If Slack API returns an error

    Example:
        result = await get_user_info(
            user="U1234567890",
            include_locale=True
        )
        # Returns: {
        #   "ok": True,
        #   "user": {
        #     "id": "U1234567890",
        #     "name": "john.doe",
        #     "real_name": "John Doe",
        #     "profile": {
        #       "email": "john@example.com",
        #       "display_name": "John",
        #       "title": "Software Engineer",
        #       "image_72": "https://avatars.slack-edge.com/...",
        #       "status_text": "In a meeting",
        #       "status_emoji": ":calendar:",
        #       ...
        #     },
        #     "is_admin": False,
        #     "is_bot": False,
        #     "tz": "America/Los_Angeles",
        #     "locale": "en-US",
        #     ...
        #   }
        # }

    Notes:
        - Requires users:read scope
        - Email requires additional users:read.email scope
        - Can lookup by user ID or username
        - Returns full profile including avatar images
    """
    client = SlackAPIClient()

    # Build request parameters
    params: Dict[str, Any] = {
        "user": user
    }

    if include_locale:
        params["include_locale"] = include_locale

    # Use GET method for users.info
    return await client.get_method("users.info", params)

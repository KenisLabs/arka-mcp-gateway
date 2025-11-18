"""
Slack Create Channel Tool.

Creates a new Slack channel using conversations.create.

Slack API Reference:
https://api.slack.com/methods/conversations.create
"""
from typing import Dict, Any, Optional
from .client import SlackAPIClient


async def create_channel(
    name: str,
    is_private: Optional[bool] = False,
    team_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create a new Slack channel.

    Args:
        name: Channel name (lowercase, no spaces, max 80 chars, hyphens/underscores allowed)
        is_private: Create private channel if True (default: False for public)
        team_id: Team ID for Enterprise Grid workspaces

    Returns:
        Dict containing:
        - ok: Success status
        - channel: Channel object with:
          - id: Channel ID (e.g., C1234567890)
          - name: Channel name
          - is_channel: True
          - is_group: True if private
          - is_private: True if private
          - created: Unix timestamp of creation
          - creator: User ID who created the channel
          - is_archived: False (newly created)
          - is_general: False (unless creating general channel)
          - name_normalized: Normalized channel name
          - is_shared: False
          - is_org_shared: False
          - is_member: True (creator is automatically a member)
          - is_private: True if private channel
          - is_mpim: False
          - topic: Channel topic object
          - purpose: Channel purpose object
          - previous_names: Array of previous names
          - num_members: Number of members (1 initially)

    Raises:
        ValueError: If Slack API returns an error

    Example:
        # Create public channel
        result = await create_channel(
            name="project-alpha"
        )
        # Returns: {
        #   "ok": True,
        #   "channel": {
        #     "id": "C1234567890",
        #     "name": "project-alpha",
        #     "is_private": False,
        #     "created": 1234567890,
        #     "creator": "U1234567890",
        #     ...
        #   }
        # }

        # Create private channel
        result = await create_channel(
            name="secret-project",
            is_private=True
        )

        # Create channel in specific team (Enterprise Grid)
        result = await create_channel(
            name="team-channel",
            team_id="T1234567890"
        )

    Notes:
        - Requires channels:manage scope for public channels
        - Requires groups:write scope for private channels
        - Channel names must be lowercase, no spaces, max 80 characters
        - Valid characters: a-z, 0-9, hyphens, underscores
        - Channel names must be unique within workspace
        - Creator is automatically added as first member
        - Channel cannot be named "general", "archive", or start with "mpdm-"
        - Returns error "name_taken" if channel name already exists
        - Returns error "invalid_name_required" if name is empty
        - Returns error "invalid_name" if name contains invalid characters
        - Returns error "invalid_name_maxlength" if name exceeds 80 chars
    """
    client = SlackAPIClient()

    # Build request parameters
    params: Dict[str, Any] = {
        "name": name,
        "is_private": is_private
    }

    if team_id:
        params["team_id"] = team_id

    # Use POST method for conversations.create
    return await client.call_method("conversations.create", params)

"""
Slack Get Channel Info Tool.

Gets detailed information about a Slack channel using conversations.info.

Slack API Reference:
https://api.slack.com/methods/conversations.info
"""
from typing import Dict, Any, Optional
from .client import SlackAPIClient


async def get_channel_info(
    channel: str,
    include_locale: Optional[bool] = False,
    include_num_members: Optional[bool] = False
) -> Dict[str, Any]:
    """
    Get detailed information about a Slack channel.

    Args:
        channel: Channel ID (e.g., C1234567890)
        include_locale: Include locale information for channel (default: False)
        include_num_members: Include member count (default: False)

    Returns:
        Dict containing:
        - ok: Success status
        - channel: Channel object with detailed information including:
          - id: Channel ID
          - name: Channel name
          - is_channel: True if public channel
          - is_group: True if private channel
          - is_im: True if direct message
          - is_mpim: True if multi-party DM
          - is_private: True if private
          - created: Unix timestamp of creation
          - is_archived: True if archived
          - is_general: True if #general channel
          - unlinked: Number of unlinked users
          - creator: User ID who created the channel
          - is_shared: True if shared with another workspace
          - is_org_shared: True if shared across Enterprise Grid
          - is_member: True if authenticated user is a member
          - is_pending_ext_shared: True if pending external share
          - pending_shared: List of pending shared invitations
          - previous_names: List of previous channel names
          - num_members: Number of members (if include_num_members=True)
          - topic: Channel topic
          - purpose: Channel purpose
          - locale: Locale information (if include_locale=True)

    Raises:
        ValueError: If Slack API returns an error

    Example:
        result = await get_channel_info(
            channel="C1234567890",
            include_num_members=True
        )
        # Returns: {
        #   "ok": True,
        #   "channel": {
        #     "id": "C1234567890",
        #     "name": "general",
        #     "is_channel": True,
        #     "is_private": False,
        #     "is_archived": False,
        #     "created": 1449252889,
        #     "creator": "U024BE7LH",
        #     "is_member": True,
        #     "num_members": 42,
        #     "topic": {"value": "Company announcements", "creator": "U024BE7LH", ...},
        #     "purpose": {"value": "This channel is for team-wide communication", ...},
        #     ...
        #   }
        # }

    Notes:
        - Requires channels:read scope for public channels
        - Requires groups:read scope for private channels
        - Requires im:read scope for direct messages
        - Requires mpim:read scope for multi-party DMs
    """
    client = SlackAPIClient()

    # Build request parameters
    params: Dict[str, Any] = {
        "channel": channel
    }

    if include_locale:
        params["include_locale"] = include_locale
    if include_num_members:
        params["include_num_members"] = include_num_members

    # Use GET method for conversations.info
    return await client.get_method("conversations.info", params)

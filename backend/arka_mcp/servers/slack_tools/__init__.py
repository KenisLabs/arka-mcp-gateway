"""
Slack Tools MCP Server.

Provides 114 Slack API tools through MCP protocol with OAuth authentication.

Security features:
- Automatic OAuth token retrieval from worker context
- Per-user token isolation
- Comprehensive error handling
- Full Slack API coverage

Available tools:
- Messaging: send_message, update_message, delete_message
- Channels: create_channel, list_channels, archive_channel
- Users: list_users, get_user_info, set_user_status
- Files: upload_file, list_files, delete_file
- And 100+ more...

Usage:
    Tools are automatically registered with the MCP server.
    OAuth tokens are injected automatically via worker context.
"""

# Tool imports will be added here as tools are implemented
from .send_message import send_message

__all__ = [
    "send_message",
]

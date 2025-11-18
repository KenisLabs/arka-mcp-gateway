"""
Pydantic models for Slack tool requests.

This module contains all request models for the 22 Slack tools,
providing validation and type safety for API parameters.
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any


class SendMessageRequest(BaseModel):
    """Request model for send_message tool"""
    channel: str = Field(description="Channel, private group, or DM channel to send message to")
    text: Optional[str] = Field(default=None, description="Plain text message content")
    blocks: Optional[List[Dict[str, Any]]] = Field(default=None, description="Block Kit blocks")
    attachments: Optional[List[Dict[str, Any]]] = Field(default=None, description="Legacy attachments")
    thread_ts: Optional[str] = Field(default=None, description="Thread timestamp to reply to")
    reply_broadcast: Optional[bool] = Field(default=None, description="Broadcast thread reply to channel")
    unfurl_links: Optional[bool] = Field(default=None, description="Enable link unfurling")
    unfurl_media: Optional[bool] = Field(default=None, description="Enable media unfurling")
    link_names: Optional[bool] = Field(default=None, description="Link channel names and usernames")
    mrkdwn: Optional[bool] = Field(default=True, description="Enable markdown formatting")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Message metadata")


class ListChannelsRequest(BaseModel):
    """Request model for list_channels tool"""
    exclude_archived: bool = Field(default=True, description="Exclude archived channels")
    types: str = Field(default="public_channel,private_channel", description="Channel types to return")
    limit: int = Field(default=100, ge=1, le=1000, description="Max number of channels")
    cursor: Optional[str] = Field(default=None, description="Pagination cursor")
    team_id: Optional[str] = Field(default=None, description="Team ID for Enterprise Grid")


class ListUsersRequest(BaseModel):
    """Request model for list_users tool"""
    cursor: Optional[str] = Field(default=None, description="Pagination cursor")
    include_locale: bool = Field(default=False, description="Include locale info")
    limit: int = Field(default=100, ge=1, le=1000, description="Max number of users")
    team_id: Optional[str] = Field(default=None, description="Team ID for Enterprise Grid")


class GetChannelInfoRequest(BaseModel):
    """Request model for get_channel_info tool"""
    channel: str = Field(description="Channel ID")
    include_locale: bool = Field(default=False, description="Include locale info")
    include_num_members: bool = Field(default=False, description="Include member count")


class GetUserInfoRequest(BaseModel):
    """Request model for get_user_info tool"""
    user: str = Field(description="User ID")
    include_locale: bool = Field(default=False, description="Include locale info")


class ListMessagesRequest(BaseModel):
    """Request model for list_messages tool"""
    channel: str = Field(description="Channel ID")
    cursor: Optional[str] = Field(default=None, description="Pagination cursor")
    inclusive: bool = Field(default=False, description="Include messages with latest/oldest timestamp")
    latest: Optional[str] = Field(default=None, description="End of time range")
    limit: int = Field(default=100, ge=1, le=1000, description="Max number of messages")
    oldest: Optional[str] = Field(default=None, description="Start of time range")
    include_all_metadata: bool = Field(default=False, description="Include all message metadata")


class AddReactionRequest(BaseModel):
    """Request model for add_reaction tool"""
    channel: str = Field(description="Channel ID")
    timestamp: str = Field(description="Message timestamp")
    name: str = Field(description="Emoji name without colons")


class RemoveReactionRequest(BaseModel):
    """Request model for remove_reaction tool"""
    channel: str = Field(description="Channel ID")
    timestamp: str = Field(description="Message timestamp")
    name: str = Field(description="Emoji name without colons")


class CreateChannelRequest(BaseModel):
    """Request model for create_channel tool"""
    name: str = Field(description="Channel name")
    is_private: bool = Field(default=False, description="Create private channel")
    team_id: Optional[str] = Field(default=None, description="Team ID for Enterprise Grid")


class ArchiveChannelRequest(BaseModel):
    """Request model for archive_channel tool"""
    channel: str = Field(description="Channel ID to archive")


class InviteToChannelRequest(BaseModel):
    """Request model for invite_to_channel tool"""
    channel: str = Field(description="Channel ID")
    users: List[str] = Field(description="List of user IDs to invite")


class KickFromChannelRequest(BaseModel):
    """Request model for kick_from_channel tool"""
    channel: str = Field(description="Channel ID")
    user: str = Field(description="User ID to remove")


class UpdateMessageRequest(BaseModel):
    """Request model for update_message tool"""
    channel: str = Field(description="Channel ID")
    ts: str = Field(description="Message timestamp")
    text: Optional[str] = Field(default=None, description="New message text")
    blocks: Optional[List[Dict[str, Any]]] = Field(default=None, description="New blocks")
    attachments: Optional[List[Dict[str, Any]]] = Field(default=None, description="New attachments")
    as_user: Optional[bool] = Field(default=None, description="Update as authed user")
    link_names: Optional[bool] = Field(default=None, description="Link names")
    parse: Optional[str] = Field(default=None, description="Parse mode")
    reply_broadcast: Optional[bool] = Field(default=None, description="Broadcast reply")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Message metadata")


class DeleteMessageRequest(BaseModel):
    """Request model for delete_message tool"""
    channel: str = Field(description="Channel ID")
    ts: str = Field(description="Message timestamp")
    as_user: bool = Field(default=False, description="Delete as authed user")


class PinMessageRequest(BaseModel):
    """Request model for pin_message tool"""
    channel: str = Field(description="Channel ID")
    timestamp: str = Field(description="Message timestamp")


class UnpinMessageRequest(BaseModel):
    """Request model for unpin_message tool"""
    channel: str = Field(description="Channel ID")
    timestamp: str = Field(description="Message timestamp")


class ReplyToThreadRequest(BaseModel):
    """Request model for reply_to_thread tool"""
    channel: str = Field(description="Channel ID")
    thread_ts: str = Field(description="Thread parent timestamp")
    text: Optional[str] = Field(default=None, description="Reply text")
    blocks: Optional[List[Dict[str, Any]]] = Field(default=None, description="Reply blocks")
    attachments: Optional[List[Dict[str, Any]]] = Field(default=None, description="Reply attachments")
    reply_broadcast: bool = Field(default=False, description="Broadcast to channel")
    unfurl_links: Optional[bool] = Field(default=None, description="Enable link unfurling")
    unfurl_media: Optional[bool] = Field(default=None, description="Enable media unfurling")
    link_names: Optional[bool] = Field(default=None, description="Link names")
    mrkdwn: bool = Field(default=True, description="Enable markdown")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Message metadata")


class ListThreadRepliesRequest(BaseModel):
    """Request model for list_thread_replies tool"""
    channel: str = Field(description="Channel ID")
    ts: str = Field(description="Thread parent timestamp")
    cursor: Optional[str] = Field(default=None, description="Pagination cursor")
    inclusive: bool = Field(default=False, description="Include messages with latest/oldest timestamp")
    latest: Optional[str] = Field(default=None, description="End of time range")
    limit: int = Field(default=100, ge=1, le=1000, description="Max number of messages")
    oldest: Optional[str] = Field(default=None, description="Start of time range")


class SearchMessagesRequest(BaseModel):
    """Request model for search_messages tool"""
    query: str = Field(description="Search query with operators")
    count: int = Field(default=20, ge=1, le=100, description="Results per page")
    highlight: bool = Field(default=True, description="Highlight matching terms")
    page: int = Field(default=1, ge=1, description="Page number")
    sort: str = Field(default="score", description="Sort order: score or timestamp")
    sort_dir: str = Field(default="desc", description="Sort direction: desc or asc")


class SearchFilesRequest(BaseModel):
    """Request model for search_files tool"""
    query: str = Field(description="Search query with operators")
    count: int = Field(default=20, ge=1, le=100, description="Results per page")
    highlight: bool = Field(default=True, description="Highlight matching terms")
    page: int = Field(default=1, ge=1, description="Page number")
    sort: str = Field(default="score", description="Sort order: score or timestamp")
    sort_dir: str = Field(default="desc", description="Sort direction: desc or asc")


class ListPinsRequest(BaseModel):
    """Request model for list_pins tool"""
    channel: str = Field(description="Channel ID")


class ListReactionsRequest(BaseModel):
    """Request model for list_reactions tool"""
    channel: str = Field(description="Channel ID")
    timestamp: str = Field(description="Message timestamp")
    full: bool = Field(default=False, description="Return full user objects")


class UploadFileRequest(BaseModel):
    """Request model for upload_file tool"""
    channels: Optional[str] = Field(default=None, description="Comma-separated channel IDs")
    content: Optional[str] = Field(default=None, description="File contents as string")
    filename: Optional[str] = Field(default=None, description="Filename")
    filetype: Optional[str] = Field(default=None, description="File type identifier")
    initial_comment: Optional[str] = Field(default=None, description="Initial comment")
    thread_ts: Optional[str] = Field(default=None, description="Thread timestamp to upload to")
    title: Optional[str] = Field(default=None, description="Title of the file")


class ListFilesRequest(BaseModel):
    """Request model for list_files tool"""
    channel: Optional[str] = Field(default=None, description="Filter by channel ID")
    count: int = Field(default=100, ge=1, le=1000, description="Number of items to return")
    page: int = Field(default=1, ge=1, description="Page number")
    show_files_hidden_by_limit: bool = Field(default=False, description="Show files hidden by limit")
    team_id: Optional[str] = Field(default=None, description="Team ID for Enterprise Grid")
    ts_from: Optional[str] = Field(default=None, description="Filter from this timestamp")
    ts_to: Optional[str] = Field(default=None, description="Filter to this timestamp")
    types: Optional[str] = Field(default=None, description="Filter by file types")
    user: Optional[str] = Field(default=None, description="Filter by user ID")


class GetFileInfoRequest(BaseModel):
    """Request model for get_file_info tool"""
    file: str = Field(description="File ID")
    count: int = Field(default=100, ge=1, le=1000, description="Number of items per page")
    cursor: Optional[str] = Field(default=None, description="Pagination cursor")
    limit: int = Field(default=0, ge=0, le=1000, description="Limit of file comments")
    page: int = Field(default=1, ge=1, description="Page number")


class DeleteFileRequest(BaseModel):
    """Request model for delete_file tool"""
    file: str = Field(description="File ID to delete")


class SetStatusRequest(BaseModel):
    """Request model for set_status tool"""
    status_text: str = Field(description="Status text to display")
    status_emoji: str = Field(description="Status emoji (e.g., ':rocket:')")
    status_expiration: Optional[int] = Field(default=None, description="Unix timestamp when status expires")


class OpenDMRequest(BaseModel):
    """Request model for open_dm tool"""
    users: str = Field(description="User ID or comma-separated user IDs for group DM")
    return_im: bool = Field(default=False, description="Return full IM object")


class ScheduleMessageRequest(BaseModel):
    """Request model for schedule_message tool"""
    channel: str = Field(description="Channel ID")
    post_at: int = Field(description="Unix timestamp when to post")
    text: Optional[str] = Field(default=None, description="Message text")
    as_user: Optional[bool] = Field(default=None, description="Post as authed user")
    attachments: Optional[List[Dict[str, Any]]] = Field(default=None, description="Message attachments")
    blocks: Optional[List[Dict[str, Any]]] = Field(default=None, description="Block Kit blocks")
    link_names: Optional[bool] = Field(default=None, description="Link channel/user names")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Message metadata")
    parse: Optional[str] = Field(default=None, description="Parse mode")
    reply_broadcast: Optional[bool] = Field(default=None, description="Broadcast reply")
    thread_ts: Optional[str] = Field(default=None, description="Thread timestamp")
    unfurl_links: Optional[bool] = Field(default=None, description="Enable link unfurling")
    unfurl_media: Optional[bool] = Field(default=None, description="Enable media unfurling")


class ListScheduledMessagesRequest(BaseModel):
    """Request model for list_scheduled_messages tool"""
    channel: Optional[str] = Field(default=None, description="Channel ID to filter")
    cursor: Optional[str] = Field(default=None, description="Pagination cursor")
    latest: Optional[int] = Field(default=None, description="End of time range")
    limit: int = Field(default=100, ge=1, le=1000, description="Max number of messages")
    oldest: Optional[int] = Field(default=None, description="Start of time range")
    team_id: Optional[str] = Field(default=None, description="Team ID for Enterprise Grid")


class DeleteScheduledMessageRequest(BaseModel):
    """Request model for delete_scheduled_message tool"""
    channel: str = Field(description="Channel ID")
    scheduled_message_id: str = Field(description="Scheduled message ID")
    as_user: bool = Field(default=False, description="Delete as authed user")


class CreateReminderRequest(BaseModel):
    """Request model for create_reminder tool"""
    text: str = Field(description="Reminder text")
    time: str = Field(description="When to remind (Unix timestamp or natural language)")
    user: Optional[str] = Field(default=None, description="User ID to receive reminder")
    recurrence: Optional[str] = Field(default=None, description="Recurrence pattern")
    team_id: Optional[str] = Field(default=None, description="Team ID for Enterprise Grid")


class ListRemindersRequest(BaseModel):
    """Request model for list_reminders tool"""
    team_id: Optional[str] = Field(default=None, description="Team ID for Enterprise Grid")


class DeleteReminderRequest(BaseModel):
    """Request model for delete_reminder tool"""
    reminder: str = Field(description="Reminder ID to delete")
    team_id: Optional[str] = Field(default=None, description="Team ID for Enterprise Grid")


class GetReminderInfoRequest(BaseModel):
    """Request model for get_reminder_info tool"""
    reminder: str = Field(description="Reminder ID")
    team_id: Optional[str] = Field(default=None, description="Team ID for Enterprise Grid")


class SearchAllRequest(BaseModel):
    """Request model for search_all tool"""
    query: str = Field(description="Search query")
    count: int = Field(default=20, ge=1, le=100, description="Results per page")
    highlight: bool = Field(default=True, description="Highlight matching terms")
    page: int = Field(default=1, ge=1, description="Page number")
    sort: str = Field(default="score", description="Sort order: score or timestamp")
    sort_dir: str = Field(default="desc", description="Sort direction: desc or asc")
    team_id: Optional[str] = Field(default=None, description="Team ID for Enterprise Grid")


class FindUserByEmailRequest(BaseModel):
    """Request model for find_user_by_email tool"""
    email: str = Field(description="Email address to search for")

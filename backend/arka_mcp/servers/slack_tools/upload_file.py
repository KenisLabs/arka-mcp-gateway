"""
Slack Upload File Tool.

Uploads or creates a file in Slack using files.upload.

Slack API Reference:
https://api.slack.com/methods/files.upload
"""
from typing import Dict, Any, Optional
from .client import SlackAPIClient


async def upload_file(
    channels: Optional[str] = None,
    content: Optional[str] = None,
    filename: Optional[str] = None,
    filetype: Optional[str] = None,
    initial_comment: Optional[str] = None,
    thread_ts: Optional[str] = None,
    title: Optional[str] = None
) -> Dict[str, Any]:
    """
    Upload or create a file in Slack.

    Args:
        channels: Comma-separated list of channel IDs to share the file (e.g., "C1234567890,C0987654321")
        content: File contents as a string (for text files)
        filename: Filename for the uploaded file (e.g., "report.txt")
        filetype: File type identifier (e.g., "text", "python", "javascript")
        initial_comment: Initial comment to add to the file
        thread_ts: Thread timestamp to upload file to a thread
        title: Title of the file

    Returns:
        Dict containing:
        - ok: Success status
        - file: File object with:
          - id: File ID (e.g., "F1234567890")
          - created: Unix timestamp when created
          - timestamp: Unix timestamp
          - name: Filename
          - title: File title
          - mimetype: MIME type
          - filetype: File type
          - pretty_type: Human-readable file type
          - user: User ID who uploaded
          - size: File size in bytes
          - mode: File mode (snippet, hosted, etc.)
          - is_public: Whether file is public
          - public_url_shared: Whether public URL shared
          - url_private: Private download URL
          - url_private_download: Private download URL
          - permalink: Permanent link to file
          - permalink_public: Public permalink
          - channels: Array of channel IDs where shared
          - groups: Array of group IDs where shared
          - ims: Array of IM IDs where shared

    Raises:
        ValueError: If Slack API returns an error

    Example:
        # Upload text file
        result = await upload_file(
            channels="C1234567890",
            content="This is the file content",
            filename="report.txt",
            title="Daily Report",
            initial_comment="Here's today's report"
        )
        # Returns: {"ok": True, "file": {...}}

        # Upload to multiple channels
        result = await upload_file(
            channels="C1234567890,C0987654321",
            content="# Meeting Notes\\n\\n## Discussion\\n...",
            filename="meeting_notes.md",
            filetype="markdown",
            title="Team Meeting Notes"
        )

        # Upload to thread
        result = await upload_file(
            channels="C1234567890",
            content="Debug logs here...",
            filename="debug.log",
            thread_ts="1234567890.123456",
            title="Debug Logs"
        )

    Notes:
        - Requires files:write scope
        - Maximum file size depends on workspace plan
        - content parameter is for text-based files
        - For binary files, use the client.upload_file() method instead
        - filetype helps Slack syntax highlight code files
        - File is shared to channels specified, or kept private if channels not provided
        - If thread_ts provided, file appears in that thread
        - initial_comment appears as first comment on the file
        - Supported filetypes: text, python, javascript, java, etc.
        - Files can be edited after upload using files.edit
        - Files can be deleted using files.delete
        - File sharing permissions depend on workspace settings
    """
    client = SlackAPIClient()

    # Build request parameters
    params: Dict[str, Any] = {}

    if channels:
        params["channels"] = channels
    if content:
        params["content"] = content
    if filename:
        params["filename"] = filename
    if filetype:
        params["filetype"] = filetype
    if initial_comment:
        params["initial_comment"] = initial_comment
    if thread_ts:
        params["thread_ts"] = thread_ts
    if title:
        params["title"] = title

    # Use POST method for files.upload
    return await client.post("files.upload", params)

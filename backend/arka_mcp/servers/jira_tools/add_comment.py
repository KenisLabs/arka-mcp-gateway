"""
Tool to add a comment to a Jira issue using Atlassian Document Format (ADF).
"""
from typing import Any, Dict, Optional
from .client import JiraAPIClient


async def add_comment(
    issue_id_or_key: str,
    comment: str,
    visibility_type: Optional[str] = None,
    visibility_value: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Adds a comment to an existing Jira issue.

    Args:
        issue_id_or_key: The numeric ID or key of the Jira issue.
        comment: The comment text in markdown or plain text.
        visibility_type: Optional visibility restriction type ('group' or 'role').
        visibility_value: The name of the group or role for visibility.

    Returns:
        A dict with comment details including id, author_display_name, created timestamp,
        issue_key, comment_text, browser_url, and execution message.
    """
    client = JiraAPIClient()
    # Build ADF body for comment
    body: Dict[str, Any] = {
        "body": {
            "type": "doc",
            "version": 1,
            "content": [
                {
                    "type": "paragraph",
                    "content": [{"type": "text", "text": comment}],
                }
            ],
        }
    }
    # Add visibility if provided
    if visibility_type and visibility_value:
        body["visibility"] = {"type": visibility_type, "value": visibility_value}
    # Post comment
    result = await client.post(f"/issue/{issue_id_or_key}/comment", json=body)
    # Prepare browser URL anchor
    comment_id = result.get("id")
    issue_key = result.get("issueKey", issue_id_or_key)
    base_url = client.instance_url.rstrip('/') if client.instance_url else ''
    browser_url = f"{base_url}/browse/{issue_key}?focusedCommentId={comment_id}"
    # Return wrapper
    return {
        "data": {
            "id": comment_id,
            "issue_key": issue_key,
            "author_display_name": result.get("author", {}).get("displayName"),
            "created": result.get("created"),
            "comment_text": comment,
            "browser_url": browser_url,
            "composio_execution_message": None,
        },
        "successful": True,
    }

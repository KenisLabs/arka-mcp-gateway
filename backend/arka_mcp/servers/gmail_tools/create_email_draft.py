"""
Create a Gmail email draft.

Implements the GMAIL_CREATE_EMAIL_DRAFT tool specification from gmail.md.

Security features:
- Input validation with Pydantic
- Authenticated via worker_context OAuth tokens
- RFC 2822 compliant message construction
"""
from typing import Dict, Any, List, Optional
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import base64
from arka_mcp.servers.gmail_tools.client import GmailAPIClient


async def create_email_draft(
    subject: Optional[str] = None,
    body: Optional[str] = None,
    recipient_email: Optional[str] = None,
    cc: List[str] = [],
    bcc: List[str] = [],
    extra_recipients: List[str] = [],
    is_html: bool = False,
    thread_id: Optional[str] = None,
    user_id: str = "me"
) -> Dict[str, Any]:
    """
    Create a Gmail email draft.

    At least one of recipient_email, cc, or bcc must be provided.
    At least one of subject or body must be provided.

    Args:
        subject: Email subject line (leave empty for thread replies to stay in thread)
        body: Email body content (plain text or HTML)
        recipient_email: Primary recipient's email address
        cc: Carbon Copy recipients' email addresses
        bcc: Blind Carbon Copy recipients' email addresses
        extra_recipients: Additional 'To' recipients
        is_html: Set to True if body is HTML (default: false)
        thread_id: ID of existing Gmail thread to reply to
        user_id: User's email address or 'me' (default: 'me')

    Returns:
        Dict containing the created draft details

    Example:
        draft = await create_email_draft(
            subject="Project Update",
            body="Hello Team,\\n\\nHere's the status...",
            recipient_email="john.doe@example.com"
        )

    Gmail API Reference:
        https://developers.google.com/gmail/api/reference/rest/v1/users.drafts/create
    """
    # Validation: At least one recipient required
    all_recipients = []
    if recipient_email:
        all_recipients.append(recipient_email)
    all_recipients.extend(extra_recipients)
    all_recipients.extend(cc)
    all_recipients.extend(bcc)

    if not all_recipients:
        raise ValueError("At least one recipient (recipient_email, cc, or bcc) must be provided")

    # Validation: At least subject or body required
    if not subject and not body:
        raise ValueError("At least one of subject or body must be provided")

    # Create MIME message
    if is_html:
        message = MIMEMultipart('alternative')
        html_part = MIMEText(body or "", 'html')
        message.attach(html_part)
    else:
        message = MIMEText(body or "", 'plain')

    # Set headers
    if subject:
        message['Subject'] = subject

    # Build To field
    to_recipients = [recipient_email] if recipient_email else []
    to_recipients.extend(extra_recipients)
    if to_recipients:
        message['To'] = ', '.join(to_recipients)

    # Build CC field
    if cc:
        message['Cc'] = ', '.join(cc)

    # Build BCC field
    if bcc:
        message['Bcc'] = ', '.join(bcc)

    # Encode message to base64url format required by Gmail API
    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')

    # Build draft payload
    draft_payload = {
        "message": {
            "raw": raw_message
        }
    }

    # Add thread_id if provided (for replying in a thread)
    if thread_id:
        draft_payload["message"]["threadId"] = thread_id

    # Create draft via Gmail API
    client = GmailAPIClient()
    return await client.post(
        f"/users/{user_id}/drafts",
        draft_payload
    )

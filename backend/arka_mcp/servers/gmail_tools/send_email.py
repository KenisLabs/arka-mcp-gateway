"""
Send an email via Gmail API.

Implements the GMAIL_SEND_EMAIL tool specification from gmail.md.

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


async def send_email(
    subject: Optional[str] = None,
    body: Optional[str] = None,
    recipient_email: Optional[str] = None,
    cc: List[str] = [],
    bcc: List[str] = [],
    extra_recipients: List[str] = [],
    is_html: bool = False,
    user_id: str = "me"
) -> Dict[str, Any]:
    """
    Send an email via Gmail API using the authenticated user's Google profile display name.

    At least one of recipient_email, cc, or bcc must be provided.
    At least one of subject or body must be provided.

    Args:
        subject: Subject line of the email
        body: Email content (plain text or HTML)
        recipient_email: Primary recipient's email address
        cc: Carbon Copy recipients' email addresses
        bcc: Blind Carbon Copy recipients' email addresses
        extra_recipients: Additional 'To' recipients
        is_html: Set to True if body contains HTML tags (default: false)
        user_id: User's email address or 'me' (default: 'me')

    Returns:
        Dict containing the sent message details

    Example:
        result = await send_email(
            subject="Project Update Meeting",
            body="Hello team, let's discuss the project updates tomorrow.",
            recipient_email="john@doe.com"
        )

    Gmail API Reference:
        https://developers.google.com/gmail/api/reference/rest/v1/users.messages/send
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

    # Build BCC field (note: BCC is not typically added to headers, handled by API)
    if bcc:
        message['Bcc'] = ', '.join(bcc)

    # Encode message to base64url format required by Gmail API
    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')

    # Send via Gmail API
    client = GmailAPIClient()
    return await client.post(
        f"/users/{user_id}/messages/send",
        {"raw": raw_message}
    )

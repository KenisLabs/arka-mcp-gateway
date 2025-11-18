"""
Send a reply within a specific Gmail thread.

Implements the GMAIL_REPLY_TO_THREAD tool specification from gmail.md.

Security features:
- Input validation with Pydantic
- Authenticated via worker_context OAuth tokens
- Validates thread_id format
- RFC 2822 compliant message construction
"""
from typing import Dict, Any, List, Optional
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import base64
from arka_mcp.servers.gmail_tools.client import GmailAPIClient
from arka_mcp.servers.gmail_tools.validators import ThreadId


async def reply_to_thread(
    thread_id: str,
    message_body: str = "",
    recipient_email: Optional[str] = None,
    cc: List[str] = [],
    bcc: List[str] = [],
    extra_recipients: List[str] = [],
    is_html: bool = False,
    user_id: str = "me"
) -> Dict[str, Any]:
    """
    Send a reply within a specific Gmail thread using the original thread's subject.

    At least one of recipient_email, cc, or bcc must be provided.

    Args:
        thread_id: Identifier of the Gmail thread for the reply (required)
        message_body: Content of the reply message (plain text or HTML)
        recipient_email: Primary recipient's email address
        cc: Carbon Copy recipients' email addresses
        bcc: Blind Carbon Copy recipients' email addresses
        extra_recipients: Additional 'To' recipients
        is_html: Indicates if message_body is HTML (default: false)
        user_id: User's email address or 'me' (default: 'me')

    Returns:
        Dict containing the sent message details

    Example:
        await reply_to_thread(
            thread_id="x53r3vdevff",
            message_body="Thanks for your email!",
            recipient_email="john@doe.com"
        )

    Gmail API Reference:
        https://developers.google.com/gmail/api/reference/rest/v1/users.messages/send
    """
    # Validate thread_id
    validated = ThreadId(thread_id=thread_id)

    # Validation: At least one recipient required
    all_recipients = []
    if recipient_email:
        all_recipients.append(recipient_email)
    all_recipients.extend(extra_recipients)
    all_recipients.extend(cc)
    all_recipients.extend(bcc)

    if not all_recipients:
        raise ValueError("At least one recipient (recipient_email, cc, or bcc) must be provided")

    # Create MIME message
    if is_html:
        message = MIMEMultipart('alternative')
        html_part = MIMEText(message_body or "", 'html')
        message.attach(html_part)
    else:
        message = MIMEText(message_body or "", 'plain')

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

    # Note: Subject should be automatically handled by Gmail when replying to a thread
    # The Gmail API will use the thread's original subject with "Re:" prefix

    # Encode message to base64url format required by Gmail API
    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')

    # Send via Gmail API with threadId to keep it in the same thread
    client = GmailAPIClient()
    return await client.post(
        f"/users/{user_id}/messages/send",
        {
            "raw": raw_message,
            "threadId": validated.thread_id
        }
    )

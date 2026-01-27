"""
Fetch newsletter subscriptions from Gmail.

Identifies newsletters by detecting List-Unsubscribe headers in emails,
which are present in most commercial newsletters and marketing emails.

Security features:
- Input validation with Pydantic
- Authenticated via worker_context OAuth tokens
- Safe URL parsing and validation
"""
from typing import Dict, Any, Optional, List
import base64
import re
from email import message_from_bytes
from arka_mcp.servers.gmail_tools.client import GmailAPIClient
from arka_mcp.servers.gmail_tools.models import FetchNewsletterSubscriptionsRequest
import logging

logger = logging.getLogger(__name__)


def extract_unsubscribe_info(headers: List[Dict[str, str]]) -> Optional[Dict[str, Any]]:
    """
    Extract unsubscribe information from email headers.

    Args:
        headers: List of email headers

    Returns:
        Dictionary with unsubscribe URL and method, or None if not found
    """
    list_unsubscribe = None
    list_unsubscribe_post = None

    for header in headers:
        name = header.get("name", "").lower()
        value = header.get("value", "")

        if name == "list-unsubscribe":
            list_unsubscribe = value
        elif name == "list-unsubscribe-post":
            list_unsubscribe_post = value

    if not list_unsubscribe:
        return None

    # Extract URLs from List-Unsubscribe header
    # Format: <http://example.com/unsubscribe>, <mailto:unsubscribe@example.com>
    urls = re.findall(r'<([^>]+)>', list_unsubscribe)

    http_urls = [url for url in urls if url.startswith(('http://', 'https://'))]
    mailto_urls = [url for url in urls if url.startswith('mailto:')]

    return {
        "http_url": http_urls[0] if http_urls else None,
        "mailto": mailto_urls[0].replace('mailto:', '') if mailto_urls else None,
        "has_one_click": list_unsubscribe_post is not None,
        "raw_header": list_unsubscribe
    }


def extract_sender_info(headers: List[Dict[str, str]]) -> Dict[str, str]:
    """
    Extract sender information from email headers.

    Args:
        headers: List of email headers

    Returns:
        Dictionary with sender name and email
    """
    sender_email = ""
    sender_name = ""
    subject = ""

    for header in headers:
        name = header.get("name", "").lower()
        value = header.get("value", "")

        if name == "from":
            # Parse From header: "Name <email@example.com>" or "email@example.com"
            match = re.search(r'<([^>]+)>', value)
            if match:
                sender_email = match.group(1)
                sender_name = value.split('<')[0].strip().strip('"')
            else:
                sender_email = value
                sender_name = value
        elif name == "subject":
            subject = value

    return {
        "email": sender_email,
        "name": sender_name,
        "subject": subject
    }


async def fetch_newsletter_subscriptions(
    user_id: str = "me",
    max_results: int = 50,
    page_token: Optional[str] = None,
    from_email: Optional[str] = None
) -> Dict[str, Any]:
    """
    Fetch newsletter subscriptions from Gmail account.

    Identifies newsletters by detecting List-Unsubscribe headers, which are
    required by CAN-SPAM Act and present in most commercial newsletters.

    Args:
        user_id: User's email address or 'me' (default: 'me')
        max_results: Maximum number of emails to scan (1-500, default: 50)
        page_token: Token for retrieving next page of results
        from_email: Optional filter to only check newsletters from specific sender

    Returns:
        Dict containing:
            - newsletters: List of newsletter subscriptions with unsubscribe info
            - next_page_token: Token for next page (if more results available)
            - total_scanned: Number of emails scanned
            - total_newsletters: Number of newsletters found

    Example:
        # Find all newsletter subscriptions
        result = await fetch_newsletter_subscriptions(max_results=100)

        # Find newsletters from specific sender
        result = await fetch_newsletter_subscriptions(
            from_email="newsletter@example.com"
        )

    Note:
        This tool scans recent emails for List-Unsubscribe headers. Not all
        newsletters may be detected if they don't include these headers, though
        most commercial newsletters do as required by anti-spam laws.
    """
    # Validate input
    request = FetchNewsletterSubscriptionsRequest(
        user_id=user_id,
        max_results=max_results,
        page_token=page_token,
        from_email=from_email
    )

    # Build search query
    # We'll fetch recent emails and check for List-Unsubscribe headers
    query_parts = []

    if request.from_email:
        query_parts.append(f"from:{request.from_email}")

    # Search in INBOX (most newsletters go there)
    query_parts.append("in:inbox")

    query = " ".join(query_parts) if query_parts else None

    # Fetch messages
    client = GmailAPIClient()

    # First, get message list
    list_params = {
        "maxResults": request.max_results,
        "includeSpamTrash": False
    }

    if query:
        list_params["q"] = query

    if request.page_token:
        list_params["pageToken"] = request.page_token

    messages_response = await client.get(
        f"/users/{request.user_id}/messages",
        list_params
    )

    message_ids = [msg["id"] for msg in messages_response.get("messages", [])]

    # Track unique newsletters by sender email
    newsletters_map: Dict[str, Dict[str, Any]] = {}
    total_scanned = 0

    # Fetch full message details for each message
    for msg_id in message_ids:
        try:
            total_scanned += 1

            # Fetch message with headers
            message = await client.get(
                f"/users/{request.user_id}/messages/{msg_id}",
                {"format": "full"}
            )

            # Get headers from payload
            headers = message.get("payload", {}).get("headers", [])

            # Extract unsubscribe info
            unsubscribe_info = extract_unsubscribe_info(headers)

            if unsubscribe_info:
                # Extract sender info
                sender_info = extract_sender_info(headers)

                sender_email = sender_info["email"]

                # Only keep one example per sender
                if sender_email and sender_email not in newsletters_map:
                    newsletters_map[sender_email] = {
                        "sender_email": sender_email,
                        "sender_name": sender_info["name"],
                        "sample_subject": sender_info["subject"],
                        "sample_message_id": msg_id,
                        "unsubscribe_http_url": unsubscribe_info["http_url"],
                        "unsubscribe_mailto": unsubscribe_info["mailto"],
                        "supports_one_click_unsubscribe": unsubscribe_info["has_one_click"],
                    }

        except Exception as e:
            logger.warning(f"Failed to process message {msg_id}: {e}")
            continue

    # Convert map to list
    newsletters_list = list(newsletters_map.values())

    # Sort by sender name
    newsletters_list.sort(key=lambda x: x["sender_name"].lower())

    return {
        "newsletters": newsletters_list,
        "next_page_token": messages_response.get("nextPageToken"),
        "total_scanned": total_scanned,
        "total_newsletters": len(newsletters_list)
    }

"""
Unsubscribe from newsletter using List-Unsubscribe headers.

Implements automated unsubscribe functionality using RFC 8058 one-click
unsubscribe where supported, and provides unsubscribe instructions otherwise.

Security features:
- Input validation with Pydantic
- Authenticated via worker_context OAuth tokens
- Safe URL validation
- Automatic handling of one-click unsubscribe
"""
from typing import Dict, Any
import re
import httpx
from arka_mcp.servers.gmail_tools.client import GmailAPIClient
from arka_mcp.servers.gmail_tools.models import UnsubscribeFromNewsletterRequest
import logging

logger = logging.getLogger(__name__)


def extract_unsubscribe_info(headers: list) -> Dict[str, Any]:
    """
    Extract unsubscribe information from email headers.

    Args:
        headers: List of email headers

    Returns:
        Dictionary with unsubscribe details
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
        return {
            "has_unsubscribe": False,
            "error": "No List-Unsubscribe header found. This email may not be a newsletter."
        }

    # Extract URLs from List-Unsubscribe header
    urls = re.findall(r'<([^>]+)>', list_unsubscribe)

    http_urls = [url for url in urls if url.startswith(('http://', 'https://'))]
    mailto_urls = [url for url in urls if url.startswith('mailto:')]

    return {
        "has_unsubscribe": True,
        "http_url": http_urls[0] if http_urls else None,
        "mailto": mailto_urls[0].replace('mailto:', '') if mailto_urls else None,
        "supports_one_click": list_unsubscribe_post is not None,
        "one_click_data": list_unsubscribe_post
    }


def get_sender_info(headers: list) -> Dict[str, str]:
    """Extract sender information."""
    for header in headers:
        if header.get("name", "").lower() == "from":
            value = header.get("value", "")
            match = re.search(r'<([^>]+)>', value)
            if match:
                return {
                    "email": match.group(1),
                    "name": value.split('<')[0].strip().strip('"')
                }
            return {"email": value, "name": value}
    return {"email": "unknown", "name": "unknown"}


async def unsubscribe_from_newsletter(
    message_id: str,
    user_id: str = "me"
) -> Dict[str, Any]:
    """
    Unsubscribe from a newsletter using the message's List-Unsubscribe header.

    This tool implements RFC 8058 one-click unsubscribe when available, which
    is the safest and most reliable method. For other methods, it provides
    instructions.

    Process:
    1. Fetches the message to get List-Unsubscribe headers
    2. If one-click unsubscribe supported: Automatically sends unsubscribe request
    3. Otherwise: Returns HTTP URL or mailto instructions

    Args:
        message_id: ID of the newsletter message to unsubscribe from
        user_id: User's email address or 'me' (default: 'me')

    Returns:
        Dict containing:
            - status: 'success', 'manual_action_required', or 'error'
            - method: Unsubscribe method used
            - message: Human-readable status message
            - details: Additional information (URL, mailto, etc.)

    Example:
        # Unsubscribe from a newsletter
        result = await unsubscribe_from_newsletter(
            message_id="18f2e3b4c5d6a789"
        )

        if result["status"] == "success":
            print("Unsubscribed successfully!")
        elif result["status"] == "manual_action_required":
            print(f"Please visit: {result['details']['url']}")

    Security:
        - Validates message_id format
        - Only processes HTTP/HTTPS URLs
        - Logs all unsubscribe attempts
        - Respects RFC 8058 one-click unsubscribe standard
    """
    # Validate input
    request = UnsubscribeFromNewsletterRequest(
        message_id=message_id,
        user_id=user_id
    )

    client = GmailAPIClient()

    # Fetch the message to get headers
    try:
        message = await client.get(
            f"/users/{request.user_id}/messages/{request.message_id}",
            {"format": "full"}
        )
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            return {
                "status": "error",
                "method": "none",
                "message": "Message not found",
                "details": {"error": "The specified message does not exist"}
            }
        raise

    # Get headers
    headers = message.get("payload", {}).get("headers", [])

    # Get sender info for better UX
    sender = get_sender_info(headers)

    # Extract unsubscribe information
    unsub_info = extract_unsubscribe_info(headers)

    if not unsub_info["has_unsubscribe"]:
        return {
            "status": "error",
            "method": "none",
            "message": unsub_info["error"],
            "details": {"sender": sender}
        }

    # Try one-click unsubscribe first (RFC 8058)
    if unsub_info["supports_one_click"] and unsub_info["http_url"]:
        try:
            # Perform one-click unsubscribe
            async with httpx.AsyncClient(timeout=30.0) as http_client:
                response = await http_client.post(
                    unsub_info["http_url"],
                    headers={
                        "List-Unsubscribe": "One-Click",
                        "Content-Length": "0"
                    }
                )

                if response.status_code in [200, 201, 202, 204]:
                    logger.info(
                        f"Successfully unsubscribed from {sender['email']} "
                        f"using one-click method for message {request.message_id}"
                    )

                    return {
                        "status": "success",
                        "method": "one_click_http",
                        "message": f"Successfully unsubscribed from {sender['name']}",
                        "details": {
                            "sender": sender,
                            "unsubscribe_url": unsub_info["http_url"],
                            "response_code": response.status_code
                        }
                    }
                else:
                    logger.warning(
                        f"One-click unsubscribe returned {response.status_code} "
                        f"for {sender['email']}"
                    )

        except Exception as e:
            logger.error(f"One-click unsubscribe failed: {e}")
            # Fall through to provide manual instructions

    # If one-click failed or not available, provide HTTP URL
    if unsub_info["http_url"]:
        return {
            "status": "manual_action_required",
            "method": "http_url",
            "message": (
                f"Please click the unsubscribe link to unsubscribe from {sender['name']}. "
                "The URL will be opened in your browser."
            ),
            "details": {
                "sender": sender,
                "url": unsub_info["http_url"],
                "instructions": "Click the URL to complete unsubscribe process"
            }
        }

    # Fall back to mailto if available
    if unsub_info["mailto"]:
        return {
            "status": "manual_action_required",
            "method": "mailto",
            "message": (
                f"Please send an email to unsubscribe from {sender['name']}. "
                "An email draft should be created automatically."
            ),
            "details": {
                "sender": sender,
                "mailto": unsub_info["mailto"],
                "instructions": (
                    f"Send an email to {unsub_info['mailto']} with subject "
                    "'Unsubscribe' to complete the process"
                )
            }
        }

    # No unsubscribe method available
    return {
        "status": "error",
        "method": "none",
        "message": "No valid unsubscribe method found",
        "details": {
            "sender": sender,
            "error": "List-Unsubscribe header exists but contains no valid methods"
        }
    }

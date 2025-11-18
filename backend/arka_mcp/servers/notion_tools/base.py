import os
import logging
from notion_client import Client
from arka_mcp.servers.worker_context import get_oauth_token, has_token_for_server

logger = logging.getLogger(__name__)


def get_notion_client() -> Client:
    """
    Get Notion client with OAuth token from worker context.

    Returns:
        Authenticated Notion client

    Raises:
        ValueError: If Notion is not authorized
        RuntimeError: If no token context available
    """
    # Check if running in worker with token context
    if has_token_for_server("notion-mcp"):
        try:
            token_data = get_oauth_token("notion-mcp")
            access_token = token_data["access_token"]

            logger.debug("Using Notion OAuth token from worker context")
            return Client(auth=access_token)
        except Exception as e:
            logger.error(f"Failed to get Notion token from context: {e}")
            raise ValueError(
                f"Failed to get Notion authorization: {str(e)}"
            )

    # Fall back to environment variable (for development/testing)
    token = os.getenv("NOTION_API_KEY")
    if token:
        logger.warning("Using NOTION_API_KEY from environment (development mode)")
        return Client(auth=token)

    # No token available
    raise ValueError(
        "Notion not authorized. Please authorize Notion in the dashboard "
        "or set NOTION_API_KEY environment variable for development."
    )


def handle_notion_error(error: Exception) -> dict:
    """Handle Notion API errors and return formatted error response."""
    error_msg = str(error)

    if "Unauthorized" in error_msg:
        return {
            "error": "Authentication failed. Please check your Notion API key.",
            "type": "authentication_error",
        }
    elif "Not found" in error_msg:
        return {
            "error": "The requested resource was not found. Check the ID and permissions.",
            "type": "not_found_error",
        }
    elif "Forbidden" in error_msg:
        return {
            "error": "Access denied. The integration may not have permission to access this resource.",
            "type": "permission_error",
        }
    else:
        return {"error": f"Notion API error: {error_msg}", "type": "api_error"}


def validate_uuid(uuid_string: str) -> bool:
    """Validate if a string is a valid UUID format."""
    import re

    uuid_pattern = re.compile(
        r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$', re.IGNORECASE
    )
    return bool(uuid_pattern.match(uuid_string))


def format_notion_id(notion_id: str) -> str:
    """Format Notion ID by removing dashes if present."""
    return notion_id.replace('-', '')


def clean_notion_response(response: dict) -> dict:
    """Clean up Notion API response by removing unnecessary fields."""
    if isinstance(response, dict):
        # Remove common unnecessary fields
        cleaned = {
            k: v
            for k, v in response.items()
            if k not in ['request_id', 'developer_survey']
        }

        # Recursively clean nested dictionaries
        for key, value in cleaned.items():
            if isinstance(value, dict):
                cleaned[key] = clean_notion_response(value)
            elif isinstance(value, list):
                cleaned[key] = [
                    clean_notion_response(item) if isinstance(item, dict) else item
                    for item in value
                ]

        return cleaned
    return response

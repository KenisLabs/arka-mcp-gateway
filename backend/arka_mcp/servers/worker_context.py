"""
Worker Context Helper for MCP Tools.

Provides a unified interface for tools to access OAuth tokens regardless
of execution context (main process or worker subprocess).

Usage in tools:
    from arka_mcp.servers.worker_context import get_oauth_token

    async def my_tool():
        token = get_oauth_token("gmail-mcp")
        # Use token["access_token"] for API calls
"""
import os
import json
import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)


def get_token_context() -> Optional[Dict]:
    """
    Get the full token context from environment variable.

    Returns:
        Token context dictionary or None if not available

    Token context structure:
        {
            "user_id": "...",
            "user_email": "...",
            "created_at": "...",
            "tokens": {
                "server-id": {
                    "access_token": "...",
                    "refresh_token": "...",
                    "expires_at": "..."
                }
            }
        }
    """
    if "MCP_TOKEN_CONTEXT" not in os.environ:
        return None

    try:
        context_json = os.environ["MCP_TOKEN_CONTEXT"]
        context = json.loads(context_json)
        return context
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse MCP_TOKEN_CONTEXT: {e}")
        return None
    except Exception as e:
        logger.error(f"Error reading token context: {e}")
        return None


def get_oauth_token(server_id: str) -> Dict[str, Optional[str]]:
    """
    Get OAuth token for a specific MCP server.

    Args:
        server_id: MCP server ID (e.g., "gmail-mcp", "github-mcp")

    Returns:
        Dictionary with token data:
        {
            "access_token": "...",
            "refresh_token": "...",  # May be None
            "expires_at": "..."       # ISO timestamp or None
        }

    Raises:
        RuntimeError: If no token context available
        ValueError: If server not authorized

    Example:
        token = get_oauth_token("gmail-mcp")
        headers = {"Authorization": f"Bearer {token['access_token']}"}
    """
    context = get_token_context()

    if context is None:
        raise RuntimeError(
            "No token context available. Tools must be executed through "
            "the worker process with token_context provided."
        )

    tokens = context.get("tokens", {})

    if server_id not in tokens:
        available_servers = list(tokens.keys())
        raise ValueError(
            f"Server '{server_id}' not authorized. "
            f"Available servers: {available_servers}"
        )

    return tokens[server_id]


def get_user_email() -> str:
    """
    Get the current user's email from token context.

    Returns:
        User's email address

    Raises:
        RuntimeError: If no token context available
    """
    context = get_token_context()

    if context is None:
        raise RuntimeError("No token context available")

    return context.get("user_email", "unknown@example.com")


def get_user_id() -> str:
    """
    Get the current user's ID from token context.

    Returns:
        User's ID

    Raises:
        RuntimeError: If no token context available
    """
    context = get_token_context()

    if context is None:
        raise RuntimeError("No token context available")

    return context.get("user_id", "unknown")


def list_authorized_servers() -> list:
    """
    Get list of all authorized MCP servers for current user.

    Returns:
        List of server IDs (e.g., ["gmail-mcp", "github-mcp"])

    Raises:
        RuntimeError: If no token context available
    """
    context = get_token_context()

    if context is None:
        raise RuntimeError("No token context available")

    tokens = context.get("tokens", {})
    return list(tokens.keys())


def has_token_for_server(server_id: str) -> bool:
    """
    Check if user has authorized a specific MCP server.

    Args:
        server_id: MCP server ID to check

    Returns:
        True if server is authorized, False otherwise
    """
    context = get_token_context()

    if context is None:
        return False

    tokens = context.get("tokens", {})
    return server_id in tokens

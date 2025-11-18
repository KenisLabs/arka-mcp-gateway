"""
Slack API Client Abstraction.

Provides a thin wrapper over httpx for Slack API calls with automatic
OAuth token retrieval from worker context.

Follows the same pattern as Google Calendar tools for consistency.

Security features:
- Automatic OAuth token retrieval from worker_context
- Proper error handling and HTTP status checking
- Timeout configuration
- Clean RPC-style API for calling Slack methods
- Helper methods for common operations

Usage:
    from .client import SlackAPIClient

    client = SlackAPIClient()
    result = await client.post("chat.postMessage", {
        "channel": "C1234567890",
        "text": "Hello from MCP Gateway!"
    })

Slack API Reference:
https://api.slack.com/methods
"""
import httpx
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class SlackAPIClient:
    """
    Slack API client with automatic OAuth token management.

    Handles all HTTP communication with Slack API, including:
    - OAuth token retrieval from worker context
    - Request formatting (RPC-style method calls)
    - Error handling
    - Response parsing
    - Rate limit handling
    """

    BASE_URL = "https://slack.com/api"
    DEFAULT_TIMEOUT = 30.0

    def __init__(self, timeout: float = DEFAULT_TIMEOUT):
        """
        Initialize Slack API client.

        Args:
            timeout: Request timeout in seconds (default: 30.0)
        """
        self.timeout = timeout

    def _get_access_token(self) -> str:
        """
        Get OAuth access token from worker context.

        Returns:
            Access token string

        Raises:
            RuntimeError: If no token context available
            ValueError: If slack-mcp not authorized
        """
        from arka_mcp.servers.worker_context import get_oauth_token

        token_data = get_oauth_token("slack-mcp")
        return token_data["access_token"]

    async def post(
        self,
        method: str,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Call a Slack API method using POST (matches GCal pattern).

        Unlike REST APIs, Slack uses RPC-style method calls where each
        API endpoint is a method name (e.g., "chat.postMessage").

        Args:
            method: Slack API method name (e.g., "chat.postMessage", "users.list")
            params: Method parameters as dictionary

        Returns:
            API response as dictionary

        Raises:
            httpx.HTTPStatusError: If HTTP request fails
            ValueError: If Slack API returns an error (ok=false)

        Example:
            result = await client.post("chat.postMessage", {
                "channel": "C1234567890",
                "text": "Hello World!"
            })

        Slack API Methods:
            https://api.slack.com/methods
        """
        access_token = self._get_access_token()
        url = f"{self.BASE_URL}/{method}"

        if params is None:
            params = {}

        async with httpx.AsyncClient() as http_client:
            response = await http_client.post(
                url,
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Content-Type": "application/json; charset=utf-8"
                },
                json=params,
                timeout=self.timeout
            )
            response.raise_for_status()

            data = response.json()

            # Slack API returns {"ok": false, "error": "error_code"} on errors
            if not data.get("ok", False):
                error = data.get("error", "unknown_error")
                logger.error(f"Slack API error for {method}: {error}")
                raise ValueError(f"Slack API error: {error}")

            return data

    async def call_method(
        self,
        method: str,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Alias for post() method for backwards compatibility.

        This maintains compatibility with existing code while
        following the GCal pattern.
        """
        return await self.post(method, params)

    async def get(
        self,
        method: str,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Call a Slack API method using GET (matches GCal pattern).

        Some Slack methods prefer GET requests (e.g., listing methods).

        Args:
            method: Slack API method name
            params: Query parameters as dictionary

        Returns:
            API response as dictionary

        Raises:
            httpx.HTTPStatusError: If HTTP request fails
            ValueError: If Slack API returns an error

        Example:
            users = await client.get("users.list", {"limit": 100})
        """
        access_token = self._get_access_token()
        url = f"{self.BASE_URL}/{method}"

        async with httpx.AsyncClient() as http_client:
            response = await http_client.get(
                url,
                headers={"Authorization": f"Bearer {access_token}"},
                params=params,
                timeout=self.timeout
            )
            response.raise_for_status()

            data = response.json()

            if not data.get("ok", False):
                error = data.get("error", "unknown_error")
                logger.error(f"Slack API error for {method}: {error}")
                raise ValueError(f"Slack API error: {error}")

            return data

    async def get_method(
        self,
        method: str,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Alias for get() method for backwards compatibility.

        This maintains compatibility with existing code while
        following the GCal pattern.
        """
        return await self.get(method, params)

    async def upload_file(
        self,
        file_content: bytes,
        filename: str,
        channels: Optional[str] = None,
        title: Optional[str] = None,
        initial_comment: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Upload a file to Slack using the files.upload method.

        This is a special case that requires multipart/form-data encoding.

        Args:
            file_content: File contents as bytes
            filename: Name of the file
            channels: Comma-separated list of channel IDs
            title: Title of the file
            initial_comment: Initial comment to add

        Returns:
            API response with file information

        Raises:
            httpx.HTTPStatusError: If HTTP request fails
            ValueError: If Slack API returns an error

        Example:
            result = await client.upload_file(
                file_content=b"Hello World!",
                filename="hello.txt",
                channels="C1234567890",
                title="Test File"
            )
        """
        access_token = self._get_access_token()
        url = f"{self.BASE_URL}/files.upload"

        files = {"file": (filename, file_content)}
        data = {}

        if channels:
            data["channels"] = channels
        if title:
            data["title"] = title
        if initial_comment:
            data["initial_comment"] = initial_comment

        async with httpx.AsyncClient() as http_client:
            response = await http_client.post(
                url,
                headers={"Authorization": f"Bearer {access_token}"},
                files=files,
                data=data,
                timeout=self.timeout
            )
            response.raise_for_status()

            result = response.json()

            if not result.get("ok", False):
                error = result.get("error", "unknown_error")
                logger.error(f"Slack file upload error: {error}")
                raise ValueError(f"Slack API error: {error}")

            return result

"""
Gmail API Client Abstraction.

Provides a thin wrapper over httpx for Gmail API calls with automatic
OAuth token retrieval from worker context.

Security features:
- Automatic OAuth token retrieval from worker_context
- Proper error handling and HTTP status checking
- Timeout configuration
- Clean API for GET/POST/PATCH/DELETE operations

Usage:
    from gmail_tools.client import GmailAPIClient

    client = GmailAPIClient()
    labels = await client.get("/users/me/labels")
"""
import httpx
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class GmailAPIClient:
    """
    Gmail API client with automatic OAuth token management.

    Handles all HTTP communication with Gmail API, including:
    - OAuth token retrieval from worker context
    - Request formatting
    - Error handling
    - Response parsing
    """

    BASE_URL = "https://gmail.googleapis.com/gmail/v1"
    DEFAULT_TIMEOUT = 30.0

    def __init__(self, timeout: float = DEFAULT_TIMEOUT):
        """
        Initialize Gmail API client.

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
            ValueError: If gmail-mcp not authorized
        """
        from arka_mcp.servers.worker_context import get_oauth_token

        token_data = get_oauth_token("gmail-mcp")
        return token_data["access_token"]

    async def get(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Make GET request to Gmail API.

        Args:
            endpoint: API endpoint (e.g., "/users/me/labels")
            params: Optional query parameters

        Returns:
            API response as dictionary

        Raises:
            httpx.HTTPStatusError: If request fails

        Example:
            labels = await client.get("/users/me/labels")
            messages = await client.get("/users/me/messages", {"q": "is:unread"})
        """
        access_token = self._get_access_token()
        url = f"{self.BASE_URL}{endpoint}"

        async with httpx.AsyncClient() as http_client:
            response = await http_client.get(
                url,
                headers={"Authorization": f"Bearer {access_token}"},
                params=params,
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()

    async def post(
        self,
        endpoint: str,
        json_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Make POST request to Gmail API.

        Args:
            endpoint: API endpoint
            json_data: Request body as dictionary

        Returns:
            API response as dictionary

        Raises:
            httpx.HTTPStatusError: If request fails

        Example:
            result = await client.post(
                "/users/me/messages/123/modify",
                {"addLabelIds": ["STARRED"]}
            )
        """
        access_token = self._get_access_token()
        url = f"{self.BASE_URL}{endpoint}"

        async with httpx.AsyncClient() as http_client:
            response = await http_client.post(
                url,
                headers={"Authorization": f"Bearer {access_token}"},
                json=json_data,
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()

    async def patch(
        self,
        endpoint: str,
        json_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Make PATCH request to Gmail API.

        Args:
            endpoint: API endpoint
            json_data: Request body as dictionary

        Returns:
            API response as dictionary

        Raises:
            httpx.HTTPStatusError: If request fails

        Example:
            result = await client.patch(
                "/users/me/labels/Label_123",
                {"name": "Updated Label"}
            )
        """
        access_token = self._get_access_token()
        url = f"{self.BASE_URL}{endpoint}"

        async with httpx.AsyncClient() as http_client:
            response = await http_client.patch(
                url,
                headers={"Authorization": f"Bearer {access_token}"},
                json=json_data,
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()

    async def delete(self, endpoint: str) -> Dict[str, Any]:
        """
        Make DELETE request to Gmail API.

        Args:
            endpoint: API endpoint

        Returns:
            Empty dict (most DELETE operations return 204 No Content)

        Raises:
            httpx.HTTPStatusError: If request fails

        Example:
            await client.delete("/users/me/labels/Label_123")
        """
        access_token = self._get_access_token()
        url = f"{self.BASE_URL}{endpoint}"

        async with httpx.AsyncClient() as http_client:
            response = await http_client.delete(
                url,
                headers={"Authorization": f"Bearer {access_token}"},
                timeout=self.timeout
            )
            response.raise_for_status()

            # DELETE often returns 204 No Content, which has no body
            if response.status_code == 204:
                return {}
            return response.json()

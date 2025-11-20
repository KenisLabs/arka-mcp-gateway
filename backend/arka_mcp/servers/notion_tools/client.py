"""
Notion API Client Abstraction.

Provides a thin wrapper over httpx for Notion API calls with automatic
OAuth token retrieval from worker context.

Security features:
- Automatic OAuth token retrieval from worker_context
- Proper error handling and HTTP status checking
- Rate limit handling (3 requests/second with retry-after support)
- Timeout configuration
- Clean API for GET/POST/PATCH/DELETE operations

Usage:
    from notion_tools.client import NotionAPIClient

    client = NotionAPIClient()
    page = await client.get("/pages/PAGE_ID")
"""
import httpx
import logging
import asyncio
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class NotionAPIClient:
    """
    Notion API client with automatic OAuth token management.

    Handles all HTTP communication with Notion API, including:
    - OAuth token retrieval from worker context
    - Request formatting with Notion-Version header
    - Rate limit handling (3 req/sec)
    - Error handling
    - Response parsing

    Rate Limits:
        Notion enforces a rate limit of 3 requests per second per integration.
        This client handles 429 responses automatically with exponential backoff.

    Security:
        - Tokens retrieved from worker_context (environment)
        - No database access in client
        - No secret leakage in logs
    """

    BASE_URL = "https://api.notion.com/v1"
    NOTION_VERSION = "2022-06-28"  # API version required by Notion
    DEFAULT_TIMEOUT = 30.0
    MAX_RETRIES = 3

    def __init__(self, timeout: float = DEFAULT_TIMEOUT):
        """
        Initialize Notion API client.

        Args:
            timeout: Request timeout in seconds (default: 30.0)

        Note:
            NO user_id or db parameters! Token comes from worker_context.
        """
        self.timeout = timeout

    def _get_access_token(self) -> str:
        """
        Get OAuth access token from worker context.

        Tokens are passed via MCP_TOKEN_CONTEXT environment variable
        by the gateway when spawning worker processes. This is a
        synchronous operation (no database access).

        Returns:
            Access token string

        Raises:
            RuntimeError: If no token context available
            ValueError: If notion-mcp not authorized

        Security:
            - Does not log token value
            - Fails fast if token unavailable
        """
        from arka_mcp.servers.worker_context import get_oauth_token

        token_data = get_oauth_token("notion-mcp")
        return token_data["access_token"]

    def _get_headers(self) -> Dict[str, str]:
        """
        Get headers for Notion API requests.

        Returns:
            Headers dictionary with Authorization and Notion-Version

        Note:
            Notion-Version header is REQUIRED on all requests.
            Using version 2022-06-28 (stable version).
        """
        access_token = self._get_access_token()
        return {
            "Authorization": f"Bearer {access_token}",
            "Notion-Version": self.NOTION_VERSION,
        }

    async def _handle_rate_limit(
        self,
        response: httpx.Response,
        retry_count: int
    ) -> bool:
        """
        Handle rate limit (429) responses.

        Args:
            response: HTTP response object
            retry_count: Current retry attempt number

        Returns:
            True if should retry, False otherwise

        Rate Limiting:
            Notion rate limit is 3 requests/second.
            If 429 received:
            1. Check retry-after header
            2. Wait specified time (or exponential backoff)
            3. Retry up to MAX_RETRIES times
        """
        if response.status_code != 429:
            return False

        if retry_count >= self.MAX_RETRIES:
            logger.error(
                f"Max retries ({self.MAX_RETRIES}) exceeded for rate limit"
            )
            return False

        # Get retry-after from response (in seconds)
        retry_after = response.headers.get("retry-after")
        if retry_after:
            wait_time = float(retry_after)
            logger.warning(
                f"Rate limited by Notion API. Retrying after {wait_time}s "
                f"(attempt {retry_count + 1}/{self.MAX_RETRIES})"
            )
        else:
            # Exponential backoff: 1s, 2s, 4s
            wait_time = 2 ** retry_count
            logger.warning(
                f"Rate limited by Notion API. Backing off for {wait_time}s "
                f"(attempt {retry_count + 1}/{self.MAX_RETRIES})"
            )

        await asyncio.sleep(wait_time)
        return True

    async def get(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Make GET request to Notion API.

        Args:
            endpoint: API endpoint (e.g., "/pages/PAGE_ID")
            params: Optional query parameters

        Returns:
            API response as dictionary

        Raises:
            httpx.HTTPStatusError: If request fails (after retries)

        Example:
            page = await client.get("/pages/abc-123")
            database = await client.get("/databases/def-456")

        Rate Limiting:
            Automatically handles 429 responses with retry-after.
        """
        url = f"{self.BASE_URL}{endpoint}"
        headers = self._get_headers()

        for retry_count in range(self.MAX_RETRIES + 1):
            async with httpx.AsyncClient() as http_client:
                response = await http_client.get(
                    url,
                    headers=headers,
                    params=params,
                    timeout=self.timeout
                )

                # Handle rate limiting
                if await self._handle_rate_limit(response, retry_count):
                    continue

                # Raise for other HTTP errors
                response.raise_for_status()
                return response.json()

        # Should not reach here, but handle gracefully
        raise httpx.HTTPStatusError(
            "Max retries exceeded",
            request=response.request,
            response=response
        )

    async def post(
        self,
        endpoint: str,
        json_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Make POST request to Notion API.

        Args:
            endpoint: API endpoint
            json_data: Request body as dictionary

        Returns:
            API response as dictionary

        Raises:
            httpx.HTTPStatusError: If request fails (after retries)

        Example:
            # Create a page
            result = await client.post("/pages", {
                "parent": {"database_id": "abc-123"},
                "properties": {...}
            })

            # Query database
            results = await client.post("/databases/abc-123/query", {
                "filter": {...}
            })

        Rate Limiting:
            Automatically handles 429 responses with retry-after.
        """
        url = f"{self.BASE_URL}{endpoint}"
        headers = self._get_headers()

        for retry_count in range(self.MAX_RETRIES + 1):
            async with httpx.AsyncClient() as http_client:
                response = await http_client.post(
                    url,
                    headers=headers,
                    json=json_data,
                    timeout=self.timeout
                )

                # Handle rate limiting
                if await self._handle_rate_limit(response, retry_count):
                    continue

                # Raise for other HTTP errors
                response.raise_for_status()
                return response.json()

        # Should not reach here, but handle gracefully
        raise httpx.HTTPStatusError(
            "Max retries exceeded",
            request=response.request,
            response=response
        )

    async def patch(
        self,
        endpoint: str,
        json_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Make PATCH request to Notion API.

        Args:
            endpoint: API endpoint
            json_data: Request body as dictionary

        Returns:
            API response as dictionary

        Raises:
            httpx.HTTPStatusError: If request fails (after retries)

        Example:
            # Update page properties
            result = await client.patch("/pages/abc-123", {
                "properties": {
                    "Name": {"title": [{"text": {"content": "Updated"}}]}
                }
            })

            # Archive a page
            result = await client.patch("/pages/abc-123", {
                "archived": True
            })

        Rate Limiting:
            Automatically handles 429 responses with retry-after.
        """
        url = f"{self.BASE_URL}{endpoint}"
        headers = self._get_headers()

        for retry_count in range(self.MAX_RETRIES + 1):
            async with httpx.AsyncClient() as http_client:
                response = await http_client.patch(
                    url,
                    headers=headers,
                    json=json_data,
                    timeout=self.timeout
                )

                # Handle rate limiting
                if await self._handle_rate_limit(response, retry_count):
                    continue

                # Raise for other HTTP errors
                response.raise_for_status()
                return response.json()

        # Should not reach here, but handle gracefully
        raise httpx.HTTPStatusError(
            "Max retries exceeded",
            request=response.request,
            response=response
        )

    async def delete(self, endpoint: str) -> Dict[str, Any]:
        """
        Make DELETE request to Notion API.

        Note: Notion API doesn't have many DELETE endpoints.
        Most deletions are done via PATCH with "archived": true.

        Args:
            endpoint: API endpoint

        Returns:
            API response as dictionary (or empty dict if 204)

        Raises:
            httpx.HTTPStatusError: If request fails (after retries)

        Example:
            # Delete a comment (if supported)
            await client.delete("/comments/abc-123")

        Rate Limiting:
            Automatically handles 429 responses with retry-after.
        """
        url = f"{self.BASE_URL}{endpoint}"
        headers = self._get_headers()

        for retry_count in range(self.MAX_RETRIES + 1):
            async with httpx.AsyncClient() as http_client:
                response = await http_client.delete(
                    url,
                    headers=headers,
                    timeout=self.timeout
                )

                # Handle rate limiting
                if await self._handle_rate_limit(response, retry_count):
                    continue

                # Raise for other HTTP errors
                response.raise_for_status()

                # DELETE often returns 204 No Content, which has no body
                if response.status_code == 204:
                    return {}
                return response.json()

        # Should not reach here, but handle gracefully
        raise httpx.HTTPStatusError(
            "Max retries exceeded",
            request=response.request,
            response=response
        )

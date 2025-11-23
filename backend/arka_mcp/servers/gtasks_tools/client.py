"""
Google Tasks API Client Abstraction.

Provides a thin wrapper over httpx for Google Tasks API calls with automatic
OAuth token retrieval from worker context.

Security features:
- Automatic OAuth token retrieval via worker_context
- Proper error handling and HTTP status checking
- Timeout configuration
- Clean API for GET/POST/PATCH/DELETE operations

Usage:
    from gtasks_tools.client import TasksAPIClient

    client = TasksAPIClient()
    lists = await client.get("/users/@me/lists")
"""
import httpx
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class TasksAPIClient:
    """
    Google Tasks API client with automatic OAuth token management.

    Handles all HTTP communication with Google Tasks API, including:
    - OAuth token retrieval from worker_context
    - Request formatting
    - Error handling
    - Response parsing
    """

    BASE_URL = "https://tasks.googleapis.com/tasks/v1"
    DEFAULT_TIMEOUT = 30.0

    def __init__(self, timeout: float = DEFAULT_TIMEOUT):
        """
        Initialize Google Tasks API client.

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
            ValueError: If gtasks-mcp not authorized
        """
        from arka_mcp.servers.worker_context import get_oauth_token

        token_data = get_oauth_token("gtasks-mcp")
        return token_data["access_token"]

    async def get(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Make GET request to Google Tasks API.

        Args:
            endpoint: API endpoint (e.g., "/users/@me/lists")
            params: Optional query parameters

        Returns:
            API response as dictionary

        Raises:
            httpx.HTTPStatusError: If request fails

        Example:
            lists = await client.get("/users/@me/lists")
            tasks = await client.get(f"/lists/{list_id}/tasks", {"maxResults": 10})
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
        json_data: Dict[str, Any],
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Make POST request to Google Tasks API.

        Args:
            endpoint: API endpoint
            json_data: Request body as dictionary
            params: Optional query parameters

        Returns:
            API response as dictionary

        Raises:
            httpx.HTTPStatusError: If request fails

        Example:
            new_list = await client.post(
                "/users/@me/lists",
                {"title": "My Tasks"}
            )
        """
        access_token = self._get_access_token()
        url = f"{self.BASE_URL}{endpoint}"

        async with httpx.AsyncClient() as http_client:
            response = await http_client.post(
                url,
                headers={"Authorization": f"Bearer {access_token}"},
                json=json_data,
                params=params,
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()

    async def patch(
        self,
        endpoint: str,
        json_data: Dict[str, Any],
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Make PATCH request to Google Tasks API.

        Args:
            endpoint: API endpoint
            json_data: Request body as dictionary
            params: Optional query parameters

        Returns:
            API response as dictionary

        Raises:
            httpx.HTTPStatusError: If request fails

        Example:
            updated = await client.patch(
                f"/lists/{list_id}/tasks/{task_id}",
                {"status": "completed"}
            )
        """
        access_token = self._get_access_token()
        url = f"{self.BASE_URL}{endpoint}"

        async with httpx.AsyncClient() as http_client:
            response = await http_client.patch(
                url,
                headers={"Authorization": f"Bearer {access_token}"},
                json=json_data,
                params=params,
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()

    async def delete(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Make DELETE request to Google Tasks API.

        Args:
            endpoint: API endpoint
            params: Optional query parameters

        Returns:
            True if deletion successful, False otherwise

        Raises:
            httpx.HTTPStatusError: If request fails

        Example:
            success = await client.delete(f"/lists/{list_id}")
        """
        access_token = self._get_access_token()
        url = f"{self.BASE_URL}{endpoint}"

        async with httpx.AsyncClient() as http_client:
            response = await http_client.delete(
                url,
                headers={"Authorization": f"Bearer {access_token}"},
                params=params,
                timeout=self.timeout
            )
            if response.status_code in (200, 204):
                return True
            response.raise_for_status()
            return False

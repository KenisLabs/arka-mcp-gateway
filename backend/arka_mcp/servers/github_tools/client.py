"""
GitHub API Client Abstraction.

Provides a thin wrapper over httpx for GitHub API calls with automatic
OAuth token retrieval from worker context.
"""

import httpx
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class GitHubAPIClient:
    """
    GitHub API client with automatic OAuth token management.

    Handles HTTP communication with GitHub API, including:
    - OAuth token retrieval from worker context
    - Request formatting
    - Error handling
    - Response parsing
    """

    BASE_URL = "https://api.github.com"
    DEFAULT_TIMEOUT = 30.0

    def __init__(self, timeout: float = DEFAULT_TIMEOUT):
        """
        Initialize GitHub API client.

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
            ValueError: If github-mcp not authorized
        """
        from arka_mcp.servers.worker_context import get_oauth_token

        token_data = get_oauth_token("github-mcp")
        return token_data["access_token"]

    async def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Any:
        """
        Make GET request to GitHub API.

        Args:
            endpoint: API endpoint (e.g., "/user")
            params: Optional query parameters

        Returns:
            Parsed JSON response

        Raises:
            httpx.HTTPStatusError: If request fails
        """
        access_token = self._get_access_token()
        url = f"{self.BASE_URL}{endpoint}"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        async with httpx.AsyncClient() as http_client:
            response = await http_client.get(
                url,
                headers=headers,
                params=params,
                timeout=self.timeout,
            )
            response.raise_for_status()
            return response.json()

    async def post(
        self,
        endpoint: str,
        json_data: Dict[str, Any],
        params: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """
        Make POST request to GitHub API.

        Args:
            endpoint: API endpoint (e.g., "/repos/{owner}/{repo}/issues")
            json_data: Request body as dictionary
            params: Optional query parameters

        Returns:
            Parsed JSON response

        Raises:
            httpx.HTTPStatusError: If request fails
        """
        access_token = self._get_access_token()
        url = f"{self.BASE_URL}{endpoint}"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "Content-Type": "application/json",
        }
        async with httpx.AsyncClient() as http_client:
            response = await http_client.post(
                url,
                headers=headers,
                json=json_data,
                params=params,
                timeout=self.timeout,
            )
            response.raise_for_status()
            return response.json()

    async def patch(
        self,
        endpoint: str,
        json_data: Dict[str, Any],
        params: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """
        Make PATCH request to GitHub API.

        Args:
            endpoint: API endpoint
            json_data: Request body as dictionary
            params: Optional query parameters

        Returns:
            Parsed JSON response

        Raises:
            httpx.HTTPStatusError: If request fails
        """
        access_token = self._get_access_token()
        url = f"{self.BASE_URL}{endpoint}"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "Content-Type": "application/json",
        }
        async with httpx.AsyncClient() as http_client:
            response = await http_client.patch(
                url,
                headers=headers,
                json=json_data,
                params=params,
                timeout=self.timeout,
            )
            response.raise_for_status()
            return response.json()

    async def put(
        self,
        endpoint: str,
        json_data: Dict[str, Any],
        params: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """
        Make PUT request to GitHub API.

        Args:
            endpoint: API endpoint (e.g., "/repos/{owner}/{repo}/pulls/{number}/merge").
            json_data: Request body as dictionary.
            params: Optional query parameters.

        Returns:
            Parsed JSON response.

        Raises:
            httpx.HTTPStatusError: If request fails.
        """
        access_token = self._get_access_token()
        url = f"{self.BASE_URL}{endpoint}"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "Content-Type": "application/json",
        }
        async with httpx.AsyncClient() as http_client:
            response = await http_client.put(
                url,
                headers=headers,
                json=json_data,
                params=params,
                timeout=self.timeout,
            )
            response.raise_for_status()
            return response.json()

    async def delete(
        self, endpoint: str, params: Optional[Dict[str, Any]] = None
    ) -> Any:
        """
        Make DELETE request to GitHub API.

        Args:
            endpoint: API endpoint (e.g., "/repos/{owner}/{repo}")
            params: Optional query parameters

        Returns:
            Parsed JSON response or empty dict

        Raises:
            httpx.HTTPStatusError: If request fails
        """
        access_token = self._get_access_token()
        url = f"{self.BASE_URL}{endpoint}"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        async with httpx.AsyncClient() as http_client:
            response = await http_client.delete(
                url,
                headers=headers,
                params=params,
                timeout=self.timeout,
            )
            response.raise_for_status()
            # Some DELETE endpoints return no content
            if response.text:
                return response.json()
            return {}

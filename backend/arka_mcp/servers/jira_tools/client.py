"""
Jira API Client Abstraction.

Provides a thin wrapper over httpx for Jira Cloud REST API calls with automatic
OAuth token retrieval from worker context.
"""

import httpx
import logging
from typing import Any, Dict, Optional

from arka_mcp.servers.worker_context import get_oauth_token

logger = logging.getLogger(__name__)


class JiraAPIClient:
    """
    Jira API client with automatic OAuth token management.

    Handles HTTP communication with Jira Cloud REST API, including:
    - OAuth token retrieval from worker context
    - Dynamic discovery of Jira Cloud ID via accessible-resources
    - GET requests to REST API endpoints
    """
    # Template for base URL; {cloud_id} to be filled dynamically
    BASE_URL_TEMPLATE = "https://api.atlassian.com/ex/jira/{cloud_id}/rest/api/3"
    ACCESSIBLE_RESOURCES = "https://api.atlassian.com/oauth/token/accessible-resources"
    DEFAULT_TIMEOUT = 30.0

    def __init__(self, timeout: float = DEFAULT_TIMEOUT):
        self.timeout = timeout
        self.cloud_id: str | None = None
        # Base Atlassian instance URL (e.g., https://your-domain.atlassian.net)
        self.instance_url: str | None = None

    async def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Any:
        """
        Make GET request to Jira REST API.

        Args:
            endpoint: API endpoint path (e.g., "/issue/KEY-123")
            params: Optional query parameters

        Returns:
            Parsed JSON response
        """
        token = get_oauth_token("jira-mcp")
        access_token = token.get("access_token")
        # Ensure cloud_id is discovered
        if not self.cloud_id:
            await self._ensure_cloud_id(access_token)
        base_url = self.BASE_URL_TEMPLATE.format(cloud_id=self.cloud_id)
        url = f"{base_url}{endpoint}"
        async with httpx.AsyncClient() as client:
            response = await client.get(
                url,
                headers={"Authorization": f"Bearer {access_token}"},
                params=params,
                timeout=self.timeout,
            )
            response.raise_for_status()
            return response.json()
    
    async def post(self, endpoint: str, json: Optional[Dict[str, Any]] = None, params: Optional[Dict[str, Any]] = None) -> Any:
        """
        Make POST request to Jira REST API.

        Args:
            endpoint: API endpoint path (e.g., "/issue")
            json: Optional JSON body
            params: Optional query parameters

        Returns:
            Parsed JSON response
        """
        token = get_oauth_token("jira-mcp")
        access_token = token.get("access_token")
        if not self.cloud_id:
            await self._ensure_cloud_id(access_token)
        base_url = self.BASE_URL_TEMPLATE.format(cloud_id=self.cloud_id)
        url = f"{base_url}{endpoint}"
        async with httpx.AsyncClient() as client:
            response = await client.post(
                url,
                headers={"Authorization": f"Bearer {access_token}"},
                json=json,
                params=params,
                timeout=self.timeout,
            )
            response.raise_for_status()
            # Some POST endpoints (e.g., transitions) return no content
            if response.content:
                return response.json()
            return {}
    
    async def put(self, endpoint: str, json: Optional[Dict[str, Any]] = None, params: Optional[Dict[str, Any]] = None) -> Any:
        """
        Make PUT request to Jira REST API.

        Args:
            endpoint: API endpoint path (e.g., "/issue/{id}")
            json: Optional JSON body
            params: Optional query parameters

        Returns:
            Parsed JSON response or empty dict
        """
        token = get_oauth_token("jira-mcp")
        access_token = token.get("access_token")
        if not self.cloud_id:
            await self._ensure_cloud_id(access_token)
        base_url = self.BASE_URL_TEMPLATE.format(cloud_id=self.cloud_id)
        url = f"{base_url}{endpoint}"
        async with httpx.AsyncClient() as client:
            response = await client.put(
                url,
                headers={"Authorization": f"Bearer {access_token}"},
                json=json,
                params=params,
                timeout=self.timeout,
            )
            response.raise_for_status()
            # Some endpoints return no content
            if response.content:
                return response.json()
            return {}
    
    async def _ensure_cloud_id(self, access_token: str) -> None:
        """
        Discover Jira Cloud ID via accessible-resources endpoint.
        Caches the cloud_id for subsequent requests.
        """
        headers = {"Authorization": f"Bearer {access_token}", "Accept": "application/json"}
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                self.ACCESSIBLE_RESOURCES,
                headers=headers,
                timeout=self.timeout,
            )
            resp.raise_for_status()
            resources = resp.json()
            if not resources or not isinstance(resources, list):
                raise RuntimeError("No accessible Jira resources found for token")
            # Use the first accessible resource as cloud_id
            # Extract cloud_id and instance URL from accessible-resources
            resource = resources[0]
            self.cloud_id = resource.get("id")
            self.instance_url = resource.get("url")
            if not self.cloud_id or not self.instance_url:
                raise RuntimeError("Invalid resource data, missing cloud_id or instance_url")

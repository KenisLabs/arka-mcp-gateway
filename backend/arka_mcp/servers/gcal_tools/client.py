"""
Google Calendar API Client Abstraction.

Provides a thin wrapper over httpx for Google Calendar API calls with automatic
OAuth token retrieval from worker context.

Security features:
- Automatic OAuth token retrieval from worker_context
- Proper error handling and HTTP status checking
- Timeout configuration
- Clean API for GET/POST/PATCH/DELETE/PUT operations

Usage:
    from google_calendar_tools.client import CalendarAPIClient

    client = CalendarAPIClient()
    calendars = await client.get("/users/me/calendarList")
"""
import httpx
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class CalendarAPIClient:
    """
    Google Calendar API client with automatic OAuth token management.

    Handles all HTTP communication with Google Calendar API, including:
    - OAuth token retrieval from worker context
    - Request formatting
    - Error handling
    - Response parsing
    """

    BASE_URL = "https://www.googleapis.com/calendar/v3"
    DEFAULT_TIMEOUT = 30.0

    def __init__(self, timeout: float = DEFAULT_TIMEOUT):
        """
        Initialize Google Calendar API client.

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
            ValueError: If gcal-mcp not authorized
        """
        from arka_mcp.servers.worker_context import get_oauth_token

        token_data = get_oauth_token("gcal-mcp")
        return token_data["access_token"]

    async def get(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Make GET request to Google Calendar API.

        Args:
            endpoint: API endpoint (e.g., "/users/me/calendarList")
            params: Optional query parameters

        Returns:
            API response as dictionary

        Raises:
            httpx.HTTPStatusError: If request fails

        Example:
            calendars = await client.get("/users/me/calendarList")
            events = await client.get("/calendars/primary/events", {"maxResults": 10})
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
        Make POST request to Google Calendar API.

        Args:
            endpoint: API endpoint
            json_data: Request body as dictionary
            params: Optional query parameters

        Returns:
            API response as dictionary

        Raises:
            httpx.HTTPStatusError: If request fails

        Example:
            result = await client.post(
                "/calendars/primary/events",
                {
                    "summary": "Team Meeting",
                    "start": {"dateTime": "2025-01-20T10:00:00-05:00"},
                    "end": {"dateTime": "2025-01-20T11:00:00-05:00"}
                }
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
        Make PATCH request to Google Calendar API.

        Args:
            endpoint: API endpoint
            json_data: Request body as dictionary
            params: Optional query parameters

        Returns:
            API response as dictionary

        Raises:
            httpx.HTTPStatusError: If request fails

        Example:
            result = await client.patch(
                "/calendars/primary/events/event123",
                {"summary": "Updated Meeting Title"}
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

    async def put(
        self,
        endpoint: str,
        json_data: Dict[str, Any],
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Make PUT request to Google Calendar API.

        Args:
            endpoint: API endpoint
            json_data: Request body as dictionary
            params: Optional query parameters

        Returns:
            API response as dictionary

        Raises:
            httpx.HTTPStatusError: If request fails

        Example:
            result = await client.put(
                "/calendars/primary/events/event123",
                {
                    "summary": "Complete Event Details",
                    "start": {"dateTime": "2025-01-20T10:00:00-05:00"},
                    "end": {"dateTime": "2025-01-20T11:00:00-05:00"}
                }
            )
        """
        access_token = self._get_access_token()
        url = f"{self.BASE_URL}{endpoint}"

        async with httpx.AsyncClient() as http_client:
            response = await http_client.put(
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
    ) -> Dict[str, Any]:
        """
        Make DELETE request to Google Calendar API.

        Args:
            endpoint: API endpoint
            params: Optional query parameters

        Returns:
            Empty dict (most DELETE operations return 204 No Content)

        Raises:
            httpx.HTTPStatusError: If request fails

        Example:
            await client.delete("/calendars/primary/events/event123")
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
            response.raise_for_status()

            # DELETE often returns 204 No Content, which has no body
            if response.status_code == 204:
                return {}
            return response.json()

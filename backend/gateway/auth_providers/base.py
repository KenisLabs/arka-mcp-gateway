"""
Base OAuth Provider class for MCP authentication.

This provides a common interface for all OAuth 2.0 providers.
"""
from abc import ABC, abstractmethod
from typing import Dict, Optional, List
from pydantic import BaseModel


class OAuthConfig(BaseModel):
    """OAuth configuration for a provider"""
    provider_name: str  # e.g., "github", "gmail", "google_calendar"
    client_id: str
    client_secret: str
    redirect_uri: str
    scopes: List[str]


class OAuthTokenResponse(BaseModel):
    """Response from OAuth token exchange"""
    access_token: str
    refresh_token: Optional[str] = None
    expires_in: Optional[int] = None
    token_type: str = "Bearer"
    scope: Optional[str] = None


class OAuthProvider(ABC):
    """
    Abstract base class for OAuth providers.

    Each MCP that requires OAuth should implement this interface.
    """

    def __init__(self, config: OAuthConfig):
        """
        Initialize the OAuth provider.

        Args:
            config: OAuth configuration (client_id, secret, etc.)
        """
        self.config = config

    @abstractmethod
    def get_authorization_url(self, state: str) -> str:
        """
        Generate the OAuth authorization URL for the user to visit.

        Args:
            state: Random state parameter for CSRF protection

        Returns:
            Authorization URL to redirect the user to
        """
        pass

    @abstractmethod
    async def exchange_code_for_token(self, code: str) -> OAuthTokenResponse:
        """
        Exchange authorization code for access token.

        Args:
            code: Authorization code from OAuth callback

        Returns:
            Token response with access_token and optional refresh_token

        Raises:
            HTTPException: If token exchange fails
        """
        pass

    @abstractmethod
    async def refresh_access_token(self, refresh_token: str) -> OAuthTokenResponse:
        """
        Refresh an expired access token using refresh token.

        Args:
            refresh_token: The refresh token

        Returns:
            New token response

        Raises:
            HTTPException: If refresh fails
        """
        pass

    @abstractmethod
    async def revoke_token(self, access_token: str) -> bool:
        """
        Revoke an access token.

        Args:
            access_token: The access token to revoke

        Returns:
            True if revocation successful, False otherwise
        """
        pass

    @abstractmethod
    async def validate_token(self, access_token: str) -> bool:
        """
        Validate that an access token is still valid.

        Args:
            access_token: The access token to validate

        Returns:
            True if token is valid, False otherwise
        """
        pass

"""
Shared Google OAuth Provider base class.

This base class provides common OAuth 2.0 functionality for all Google APIs
(Gmail, Calendar, Drive, Docs, etc.) to eliminate code duplication.

All Google services share the same OAuth endpoints and flow, differing only
in their API scopes and validation endpoints.

Security features:
- Token refresh with rotation
- Sanitized error messages
- Comprehensive logging
- CSRF protection via state parameter
"""
import httpx
from typing import Optional, List
from fastapi import HTTPException
from urllib.parse import urlencode
from .base import OAuthProvider, OAuthConfig, OAuthTokenResponse
import logging

logger = logging.getLogger(__name__)


class GoogleOAuthProvider(OAuthProvider):
    """
    Shared OAuth 2.0 provider for all Google APIs.

    Provides common OAuth flow implementation that can be extended by
    specific Google service providers (Gmail, Calendar, Drive, etc.).
    """

    # Shared OAuth endpoints for all Google services
    AUTHORIZATION_BASE_URL = "https://accounts.google.com/o/oauth2/v2/auth"
    TOKEN_URL = "https://oauth2.googleapis.com/token"
    REVOKE_URL = "https://oauth2.googleapis.com/revoke"

    # Subclasses must define their own validation endpoint
    USER_INFO_URL: Optional[str] = None

    def get_authorization_url(self, state: str) -> str:
        """
        Generate Google OAuth authorization URL.

        Args:
            state: Random state parameter for CSRF protection

        Returns:
            Authorization URL to redirect the user to
        """
        params = {
            "client_id": self.config.client_id,
            "redirect_uri": self.config.redirect_uri,
            "response_type": "code",
            "scope": " ".join(self.config.scopes),
            "state": state,
            "access_type": "offline",  # Request refresh token
            "prompt": "consent"  # Force consent screen to ensure refresh token
        }
        return f"{self.AUTHORIZATION_BASE_URL}?{urlencode(params)}"

    async def exchange_code_for_token(self, code: str) -> OAuthTokenResponse:
        """
        Exchange authorization code for access token.

        Args:
            code: Authorization code from OAuth callback

        Returns:
            Token response with access_token and refresh_token

        Raises:
            HTTPException: If token exchange fails
        """
        data = {
            "client_id": self.config.client_id,
            "client_secret": self.config.client_secret,
            "code": code,
            "redirect_uri": self.config.redirect_uri,
            "grant_type": "authorization_code"
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.TOKEN_URL,
                    data=data,
                    timeout=30.0
                )
                response.raise_for_status()
                token_data = response.json()

                if "error" in token_data:
                    # Log detailed error server-side
                    logger.error(f"Google OAuth error during code exchange: {token_data}")
                    # Return sanitized error to client
                    raise HTTPException(
                        status_code=400,
                        detail="Failed to authorize with Google. Please try again."
                    )

                # Google provides refresh_token and expires_in
                return OAuthTokenResponse(
                    access_token=token_data["access_token"],
                    refresh_token=token_data.get("refresh_token"),
                    expires_in=token_data.get("expires_in", 3600),
                    token_type=token_data.get("token_type", "Bearer"),
                    scope=token_data.get("scope")
                )

        except httpx.HTTPError as e:
            # Log detailed error server-side
            logger.error(f"Failed to exchange Google code for token: {e}")
            # Return sanitized error to client
            raise HTTPException(
                status_code=500,
                detail="Failed to complete Google authorization. Please try again."
            )

    async def refresh_access_token(self, refresh_token: str) -> OAuthTokenResponse:
        """
        Refresh an expired access token.

        Security: Checks for new refresh token from Google (token rotation).

        Args:
            refresh_token: The refresh token

        Returns:
            New token response with fresh access_token

        Raises:
            HTTPException: If refresh fails
        """
        data = {
            "client_id": self.config.client_id,
            "client_secret": self.config.client_secret,
            "refresh_token": refresh_token,
            "grant_type": "refresh_token"
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.TOKEN_URL,
                    data=data,
                    timeout=30.0
                )
                response.raise_for_status()
                token_data = response.json()

                if "error" in token_data:
                    # Log detailed error server-side
                    logger.error(f"Google token refresh error: {token_data}")
                    # Return sanitized error to client
                    raise HTTPException(
                        status_code=401,
                        detail="Google authorization expired. Please re-authorize."
                    )

                # Check if Google provided new refresh token (token rotation)
                new_refresh_token = token_data.get("refresh_token", refresh_token)

                if new_refresh_token != refresh_token:
                    logger.info("Google provided new refresh token (token rotation)")

                return OAuthTokenResponse(
                    access_token=token_data["access_token"],
                    refresh_token=new_refresh_token,  # Use new token if provided
                    expires_in=token_data.get("expires_in", 3600),
                    token_type=token_data.get("token_type", "Bearer"),
                    scope=token_data.get("scope")
                )

        except httpx.HTTPError as e:
            # Log detailed error server-side
            logger.error(f"Failed to refresh Google token: {e}")
            # Return sanitized error to client
            raise HTTPException(
                status_code=401,
                detail="Google authorization expired. Please re-authorize."
            )

    async def revoke_token(self, access_token: str) -> bool:
        """
        Revoke a Google access token.

        Args:
            access_token: The access token to revoke

        Returns:
            True if revocation successful, False otherwise
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.REVOKE_URL,
                    params={"token": access_token},
                    timeout=30.0
                )
                success = response.status_code == 200

                if success:
                    logger.info("Successfully revoked Google token")
                else:
                    logger.warning(f"Failed to revoke Google token: {response.status_code}")

                return success

        except httpx.HTTPError as e:
            logger.error(f"Failed to revoke Google token: {e}")
            return False

    async def validate_token(self, access_token: str) -> bool:
        """
        Validate that a Google access token is still valid.

        Subclasses must define USER_INFO_URL to provide service-specific validation.

        Args:
            access_token: The access token to validate

        Returns:
            True if token is valid, False otherwise
        """
        if not self.USER_INFO_URL:
            logger.error("USER_INFO_URL not defined for token validation")
            return False

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    self.USER_INFO_URL,
                    headers={"Authorization": f"Bearer {access_token}"},
                    timeout=30.0
                )
                is_valid = response.status_code == 200

                if not is_valid:
                    logger.debug(f"Google token validation failed: {response.status_code}")

                return is_valid

        except httpx.HTTPError as e:
            logger.error(f"Failed to validate Google token: {e}")
            return False

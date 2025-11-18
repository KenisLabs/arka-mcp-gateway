"""
Gmail OAuth Provider implementation.

Gmail API OAuth 2.0 documentation:
https://developers.google.com/gmail/api/auth/web-server

Security features:
- Token refresh with rotation
- Sanitized error messages
- Comprehensive logging
"""
import httpx
from typing import Optional, List
from fastapi import HTTPException
from urllib.parse import urlencode
from .base import OAuthProvider, OAuthConfig, OAuthTokenResponse
import logging

logger = logging.getLogger(__name__)


class GmailOAuthProvider(OAuthProvider):
    """
    Gmail OAuth 2.0 provider.

    Handles authorization flow for Gmail MCP server with security best practices.
    """

    AUTHORIZATION_BASE_URL = "https://accounts.google.com/o/oauth2/v2/auth"
    TOKEN_URL = "https://oauth2.googleapis.com/token"
    REVOKE_URL = "https://oauth2.googleapis.com/revoke"
    USER_INFO_URL = "https://gmail.googleapis.com/gmail/v1/users/me/profile"

    def get_authorization_url(self, state: str) -> str:
        """
        Generate Gmail OAuth authorization URL.

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
            "prompt": "consent"  # Force consent screen to ensure refresh token is provided
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
                    logger.error(f"Gmail OAuth error during code exchange: {token_data}")
                    # Return sanitized error to client
                    raise HTTPException(
                        status_code=400,
                        detail="Failed to authorize Gmail. Please try again."
                    )

                # Gmail provides refresh_token and expires_in
                return OAuthTokenResponse(
                    access_token=token_data["access_token"],
                    refresh_token=token_data.get("refresh_token"),
                    expires_in=token_data.get("expires_in", 3600),
                    token_type=token_data.get("token_type", "Bearer"),
                    scope=token_data.get("scope")
                )

        except httpx.HTTPError as e:
            # Log detailed error server-side
            logger.error(f"Failed to exchange Gmail code for token: {e}")
            # Return sanitized error to client
            raise HTTPException(
                status_code=500,
                detail="Failed to complete Gmail authorization. Please try again."
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
                    logger.error(f"Gmail token refresh error: {token_data}")
                    # Return sanitized error to client
                    raise HTTPException(
                        status_code=401,
                        detail="Gmail authorization expired. Please re-authorize."
                    )

                # Check if Google provided new refresh token (token rotation)
                new_refresh_token = token_data.get("refresh_token", refresh_token)

                if new_refresh_token != refresh_token:
                    logger.info("Gmail provided new refresh token (token rotation)")

                return OAuthTokenResponse(
                    access_token=token_data["access_token"],
                    refresh_token=new_refresh_token,  # Use new token if provided
                    expires_in=token_data.get("expires_in", 3600),
                    token_type=token_data.get("token_type", "Bearer"),
                    scope=token_data.get("scope")
                )

        except httpx.HTTPError as e:
            # Log detailed error server-side
            logger.error(f"Failed to refresh Gmail token: {e}")
            # Return sanitized error to client
            raise HTTPException(
                status_code=401,
                detail="Gmail authorization expired. Please re-authorize."
            )

    async def revoke_token(self, access_token: str) -> bool:
        """
        Revoke a Gmail access token.

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
                    logger.info("Successfully revoked Gmail token")
                else:
                    logger.warning(f"Failed to revoke Gmail token: {response.status_code}")

                return success

        except httpx.HTTPError as e:
            logger.error(f"Failed to revoke Gmail token: {e}")
            return False

    async def validate_token(self, access_token: str) -> bool:
        """
        Validate that a Gmail access token is still valid.

        Args:
            access_token: The access token to validate

        Returns:
            True if token is valid, False otherwise
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    self.USER_INFO_URL,
                    headers={"Authorization": f"Bearer {access_token}"},
                    timeout=30.0
                )
                is_valid = response.status_code == 200

                if not is_valid:
                    logger.debug(f"Gmail token validation failed: {response.status_code}")

                return is_valid

        except httpx.HTTPError as e:
            logger.error(f"Failed to validate Gmail token: {e}")
            return False


def create_gmail_oauth_provider(
    client_id: str,
    client_secret: str,
    redirect_uri: str,
    scopes: Optional[List[str]] = None
) -> GmailOAuthProvider:
    """
    Factory function to create a Gmail OAuth provider.

    Args:
        client_id: Google OAuth client ID
        client_secret: Google OAuth client secret
        redirect_uri: Callback URL for OAuth flow
        scopes: List of Gmail API scopes

    Returns:
        Configured GmailOAuthProvider instance
    """
    if scopes is None:
        # Default scopes - comprehensive Gmail access
        scopes = [
            "https://www.googleapis.com/auth/gmail.readonly",
            "https://www.googleapis.com/auth/gmail.modify",
            "https://www.googleapis.com/auth/gmail.labels",
            "https://www.googleapis.com/auth/gmail.send"
        ]

    config = OAuthConfig(
        provider_name="gmail",
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri=redirect_uri,
        scopes=scopes
    )

    return GmailOAuthProvider(config)

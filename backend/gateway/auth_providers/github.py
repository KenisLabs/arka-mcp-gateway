"""
GitHub OAuth Provider implementation.

GitHub OAuth 2.0 documentation:
https://docs.github.com/en/apps/oauth-apps/building-oauth-apps/authorizing-oauth-apps
"""

import httpx
import json
from typing import Optional, List
from fastapi import HTTPException
from urllib.parse import urlencode
from .base import OAuthProvider, OAuthConfig, OAuthTokenResponse
import logging

logger = logging.getLogger(__name__)


class GitHubOAuthProvider(OAuthProvider):
    """
    GitHub OAuth 2.0 provider.

    Handles authorization flow for GitHub MCP server.
    """

    AUTHORIZATION_BASE_URL = "https://github.com/login/oauth/authorize"
    TOKEN_URL = "https://github.com/login/oauth/access_token"
    REVOKE_URL = "https://api.github.com/applications/{client_id}/grant"  # Changed from /token to /grant to force re-consent
    USER_URL = "https://api.github.com/user"

    def get_authorization_url(self, state: str) -> str:
        """
        Generate GitHub OAuth authorization URL.

        Args:
            state: Random state parameter for CSRF protection

        Returns:
            Authorization URL to redirect the user to
        """
        params = {
            "client_id": self.config.client_id,
            "redirect_uri": self.config.redirect_uri,
            "scope": " ".join(self.config.scopes),
            "state": state,
            "allow_signup": "false",  # Only allow existing GitHub users
            "prompt": "select_account",  # Force re-consent to ensure fresh authentication
        }
        return f"{self.AUTHORIZATION_BASE_URL}?{urlencode(params)}"

    async def exchange_code_for_token(self, code: str) -> OAuthTokenResponse:
        """
        Exchange authorization code for access token.

        Args:
            code: Authorization code from OAuth callback

        Returns:
            Token response with access_token

        Raises:
            HTTPException: If token exchange fails
        """
        data = {
            "client_id": self.config.client_id,
            "client_secret": self.config.client_secret,
            "code": code,
            "redirect_uri": self.config.redirect_uri,
        }

        headers = {"Accept": "application/json"}

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.TOKEN_URL, data=data, headers=headers, timeout=30.0
                )
                response.raise_for_status()
                token_data = response.json()

                if "error" in token_data:
                    logger.error(f"GitHub OAuth error: {token_data}")
                    raise HTTPException(
                        status_code=400,
                        detail=f"GitHub OAuth error: {token_data.get('error_description', token_data['error'])}",
                    )

                # GitHub doesn't provide refresh tokens or expiry for OAuth Apps
                # Only GitHub Apps have refresh tokens
                return OAuthTokenResponse(
                    access_token=token_data["access_token"],
                    token_type=token_data.get("token_type", "bearer"),
                    scope=token_data.get("scope"),
                )

        except httpx.HTTPError as e:
            logger.error(f"Failed to exchange GitHub code for token: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to exchange authorization code: {str(e)}",
            )

    async def refresh_access_token(self, refresh_token: str) -> OAuthTokenResponse:
        """
        Refresh an expired access token.

        Note: GitHub OAuth Apps don't support refresh tokens.
        This is only available for GitHub Apps.

        Args:
            refresh_token: The refresh token (not supported)

        Raises:
            HTTPException: Always raises as not supported for OAuth Apps
        """
        raise HTTPException(
            status_code=501,
            detail="GitHub OAuth Apps do not support refresh tokens. Use GitHub Apps for token refresh.",
        )

    async def revoke_token(self, access_token: str) -> bool:
        """
        Revoke a GitHub access token.

        Args:
            access_token: The access token to revoke

        Returns:
            True if revocation successful, False otherwise
        """
        url = self.REVOKE_URL.format(client_id=self.config.client_id)

        try:
            async with httpx.AsyncClient() as client:
                response = await client.delete(
                    url,
                    content=json.dumps({"access_token": access_token}),
                    headers={"Content-Type": "application/json"},
                    auth=(self.config.client_id, self.config.client_secret),
                    timeout=30.0,
                )
                return response.status_code == 204

        except httpx.HTTPError as e:
            logger.error(f"Failed to revoke GitHub token: {e}")
            return False

    async def validate_token(self, access_token: str) -> bool:
        """
        Validate that a GitHub access token is still valid.

        Makes a simple API call to check if the token works.

        Args:
            access_token: The access token to validate

        Returns:
            True if token is valid, False otherwise
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    self.USER_URL,
                    headers={
                        "Authorization": f"Bearer {access_token}",
                        "Accept": "application/vnd.github+json",
                        "X-GitHub-Api-Version": "2022-11-28",
                    },
                    timeout=30.0,
                )
                return response.status_code == 200

        except httpx.HTTPError as e:
            logger.error(f"Failed to validate GitHub token: {e}")
            return False


def create_github_oauth_provider(
    client_id: str,
    client_secret: str,
    redirect_uri: str,
    scopes: Optional[List[str]] = None,
) -> GitHubOAuthProvider:
    """
    Factory function to create a GitHub OAuth provider.

    Args:
        client_id: GitHub OAuth App client ID
        client_secret: GitHub OAuth App client secret
        redirect_uri: Callback URL for OAuth flow
        scopes: List of GitHub OAuth scopes (defaults to repo, user)

    Returns:
        Configured GitHubOAuthProvider instance
    """
    if scopes is None:
        scopes = ["repo", "user"]  # Default scopes for GitHub MCP

    config = OAuthConfig(
        provider_name="github",
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri=redirect_uri,
        scopes=scopes,
    )

    return GitHubOAuthProvider(config)

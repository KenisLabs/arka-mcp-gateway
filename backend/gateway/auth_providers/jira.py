"""
Jira OAuth Provider implementation.

Jira OAuth 2.0 documentation:
https://developer.atlassian.com/cloud/jira/platform/oauth-2-3lo-apps/
"""

import logging
from typing import Optional, List
from urllib.parse import urlencode
import httpx
from fastapi import HTTPException

from .base import OAuthProvider, OAuthConfig, OAuthTokenResponse

logger = logging.getLogger(__name__)


class JiraOAuthProvider(OAuthProvider):
    """
    Jira OAuth 2.0 provider for MCP.
    """

    AUTHORIZATION_BASE_URL = "https://auth.atlassian.com/authorize"
    TOKEN_URL = "https://auth.atlassian.com/oauth/token"

    def get_authorization_url(self, state: str) -> str:
        """
        Generate Jira OAuth authorization URL.
        """
        params = {
            "audience": "api.atlassian.com",
            "client_id": self.config.client_id,
            "scope": " ".join(self.config.scopes),
            "redirect_uri": self.config.redirect_uri,
            "response_type": "code",
            "state": state,
        }

        url = f"{self.AUTHORIZATION_BASE_URL}?{urlencode(params)}"
        logger.debug(f"Jira auth URL: {url}")
        return url

    async def exchange_code_for_token(self, code: str) -> OAuthTokenResponse:
        """
        Exchange authorization code for access and refresh tokens.
        """
        data = {
            "grant_type": "authorization_code",
            "client_id": self.config.client_id,
            "client_secret": self.config.client_secret,
            "code": code,
            "redirect_uri": self.config.redirect_uri,
        }
        headers = {"Content-Type": "application/json"}
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.post(
                    self.TOKEN_URL, json=data, headers=headers, timeout=30.0
                )
                resp.raise_for_status()
                token_data = resp.json()
            return OAuthTokenResponse(
                access_token=token_data.get("access_token"),
                refresh_token=token_data.get("refresh_token"),
                expires_in=token_data.get("expires_in"),
                token_type=token_data.get("token_type", "Bearer"),
                scope=token_data.get("scope"),
            )
        except httpx.HTTPError as e:
            logger.error(f"Jira token exchange error: {e}")
            raise HTTPException(
                status_code=400, detail="Failed to authorize Jira integration"
            )

    async def refresh_access_token(self, refresh_token: str) -> OAuthTokenResponse:
        """
        Refresh an expired access token.
        """
        data = {
            "grant_type": "refresh_token",
            "client_id": self.config.client_id,
            "client_secret": self.config.client_secret,
            "refresh_token": refresh_token,
        }
        headers = {"Content-Type": "application/json"}
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.post(
                    self.TOKEN_URL, json=data, headers=headers, timeout=30.0
                )
                resp.raise_for_status()
                token_data = resp.json()
            return OAuthTokenResponse(
                access_token=token_data.get("access_token"),
                refresh_token=token_data.get("refresh_token"),
                expires_in=token_data.get("expires_in"),
                token_type=token_data.get("token_type", "Bearer"),
                scope=token_data.get("scope"),
            )
        except httpx.HTTPError as e:
            logger.error(f"Jira refresh token error: {e}")
            raise HTTPException(status_code=500, detail="Failed to refresh Jira token")

    async def revoke_token(self, access_token: str) -> bool:
        """
        Jira does not support token revocation via API.
        """
        logger.warning("Jira revoke_token is not supported")
        return False

    async def validate_token(self, access_token: str) -> bool:
        """
        Validate token by checking accessible resources.
        """
        try:
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Accept": "application/json",
            }
            async with httpx.AsyncClient() as client:
                resp = await client.get(
                    "https://api.atlassian.com/oauth/token/accessible-resources",
                    headers=headers,
                    timeout=30.0,
                )
                return resp.status_code == 200
        except httpx.HTTPError as e:
            logger.error(f"Failed to validate Jira token: {e}")
            return False


def create_jira_oauth_provider(
    client_id: str,
    client_secret: str,
    redirect_uri: str,
    scopes: Optional[List[str]] = None,
) -> JiraOAuthProvider:
    """
    Factory for Jira OAuth provider.
    """
    if not scopes:
        # Default Jira scopes in specific order for authorization URL
        scopes = [
            "read:jira-work",
            "read:jira-user",
            "write:jira-work",
            "manage:jira-webhook",
            "manage:jira-data-provider",
            "manage:jira-project",
            # Include offline_access for refresh token capability
            "offline_access",
        ]
    config = OAuthConfig(
        provider_name="jira",
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri=redirect_uri,
        scopes=scopes,
    )
    return JiraOAuthProvider(config)

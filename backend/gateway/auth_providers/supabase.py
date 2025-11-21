"""
Supabase OAuth Provider implementation.

Supabase integration docs:
https://supabase.com/docs/guides/integrations/build-a-supabase-integration
"""

import logging
import base64
import httpx
from typing import Optional, List
from fastapi import HTTPException
from urllib.parse import urlencode
from .base import OAuthProvider, OAuthConfig, OAuthTokenResponse

logger = logging.getLogger(__name__)


class SupabaseOAuthProvider(OAuthProvider):
    """
    Supabase OAuth 2.0 provider for MCP.
    """

    AUTHORIZATION_BASE_URL = "https://api.supabase.com/v1/oauth/authorize"
    TOKEN_URL = "https://api.supabase.com/v1/oauth/token"

    def get_authorization_url(self, state: str) -> str:
        """
        Generate Supabase OAuth authorization URL.
        """
        params = {
            "client_id": self.config.client_id,
            "redirect_uri": self.config.redirect_uri,
            "response_type": "code",
            "scope": " ".join(self.config.scopes),
            "state": state,
        }
        url = f"{self.AUTHORIZATION_BASE_URL}?{urlencode(params)}"
        logger.debug(f"Supabase auth URL: {url}")
        return url

    async def exchange_code_for_token(self, code: str) -> OAuthTokenResponse:
        """
        Exchange authorization code for access and refresh tokens.
        """
        data = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": self.config.redirect_uri,
        }
        basic_auth = base64.b64encode(
            f"{self.config.client_id}:{self.config.client_secret}".encode()
        ).decode()
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json",
            "Authorization": f"Basic {basic_auth}",
        }

        try:
            async with httpx.AsyncClient() as client:
                resp = await client.post(
                    self.TOKEN_URL,
                    data=data,
                    headers=headers,
                    timeout=30.0,
                )
                resp.raise_for_status()
                token_data = resp.json()
            if "access_token" not in token_data:
                logger.error("Supabase token response missing access_token")
                raise HTTPException(
                    status_code=500, detail="Invalid Supabase token response"
                )
            return OAuthTokenResponse(
                access_token=token_data.get("access_token"),
                refresh_token=token_data.get("refresh_token"),
                expires_in=token_data.get("expires_in"),
                token_type=token_data.get("token_type", "Bearer"),
                scope=token_data.get("scope"),
            )
        except httpx.HTTPStatusError as e:
            logger.error(f"Supabase token exchange error: {e.response.text}")
            raise HTTPException(
                status_code=400, detail="Failed to authorize Supabase integration"
            )
        except httpx.HTTPError as e:
            logger.error(f"Supabase token exchange network error: {e}")
            raise HTTPException(
                status_code=500, detail="Supabase token exchange failed"
            )

    async def refresh_access_token(self, refresh_token: str) -> OAuthTokenResponse:
        """
        Refresh an expired access token.
        """
        data = {
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
            "client_id": self.config.client_id,
            "client_secret": self.config.client_secret,
        }
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.post(
                    self.TOKEN_URL,
                    json=data,
                    headers={"Content-Type": "application/json"},
                    timeout=30.0,
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
        except Exception as e:
            logger.error(f"Supabase refresh token error: {e}")
            raise HTTPException(
                status_code=500, detail="Failed to refresh Supabase token"
            )

    async def revoke_token(self, access_token: str) -> bool:
        """
        Supabase does not support token revocation via API.
        """
        logger.warning("Supabase revoke_token is not supported")
        return False

    async def validate_token(self, access_token: str) -> bool:
        """
        Validate token by assuming valid until expired.
        """
        return True


def create_supabase_oauth_provider(
    client_id: str,
    client_secret: str,
    redirect_uri: str,
    scopes: Optional[List[str]] = None,
) -> SupabaseOAuthProvider:
    """
    Factory for Supabase OAuth provider.
    """
    if scopes is None:
        scopes = ["all"]
    config = OAuthConfig(
        provider_name="supabase",
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri=redirect_uri,
        scopes=scopes,
    )
    return SupabaseOAuthProvider(config)

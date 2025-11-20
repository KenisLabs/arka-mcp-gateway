"""
Notion OAuth Provider implementation.

Notion OAuth 2.0 documentation:
https://developers.notion.com/docs/authorization

Security features:
- Token encryption at rest (handled by gateway)
- Non-expiring tokens (Notion tokens don't expire)
- Sanitized error messages (no secret leakage)
- Comprehensive logging
- Workspace-scoped authorization

Implementation notes:
- Notion uses workspace-based OAuth (user selects workspace during authorization)
- Access tokens are permanent until explicitly revoked by user
- No refresh tokens provided (tokens don't expire)
- Requires Notion-Version header on API requests (handled by API client)

Rate limits:
- 3 requests per second per integration
- Burst handling via retry-after header
"""
import httpx
import logging
from typing import Optional, List
from fastapi import HTTPException
from urllib.parse import urlencode
from .base import OAuthProvider, OAuthConfig, OAuthTokenResponse

logger = logging.getLogger(__name__)


class NotionOAuthProvider(OAuthProvider):
    """
    Notion OAuth 2.0 provider.

    Handles authorization flow for Notion MCP server with workspace-based authentication.
    Notion tokens are permanent and do not require refresh.

    Security considerations:
    - Workspace isolation: Each authorization is workspace-specific
    - No token expiration: Tokens remain valid until revoked by user
    - Integration permissions: Set during integration creation, not OAuth scope
    """

    # Notion OAuth endpoints
    AUTHORIZATION_BASE_URL = "https://api.notion.com/v1/oauth/authorize"
    TOKEN_URL = "https://api.notion.com/v1/oauth/token"
    # Note: Notion doesn't have a dedicated revoke endpoint
    # Tokens are revoked through workspace settings

    def get_authorization_url(self, state: str) -> str:
        """
        Generate Notion OAuth authorization URL.

        Notion uses workspace-based OAuth where the user selects which workspace
        to connect during the authorization flow.

        Args:
            state: Random state parameter for CSRF protection

        Returns:
            Authorization URL to redirect the user to

        Security:
            - State parameter prevents CSRF attacks
            - Owner type restricts authorization scope

        Example:
            >>> provider = NotionOAuthProvider(config)
            >>> url = provider.get_authorization_url("random_state_123")
            >>> # User visits URL and authorizes workspace access
        """
        params = {
            "client_id": self.config.client_id,
            "redirect_uri": self.config.redirect_uri,
            "response_type": "code",
            "owner": "user",  # Notion-specific: user vs workspace owner
            "state": state,
        }

        logger.debug(f"Generated Notion authorization URL with state={state[:8]}...")
        return f"{self.AUTHORIZATION_BASE_URL}?{urlencode(params)}"

    async def exchange_code_for_token(self, code: str) -> OAuthTokenResponse:
        """
        Exchange authorization code for access token.

        Notion returns workspace information along with the access token.
        The token is permanent and doesn't expire.

        Args:
            code: Authorization code from OAuth callback

        Returns:
            Token response with access_token (no refresh_token)

        Raises:
            HTTPException: If token exchange fails

        Response structure from Notion:
            {
                "access_token": "secret_xxx",
                "workspace_id": "xxx",
                "workspace_name": "My Workspace",
                "workspace_icon": "https://...",
                "bot_id": "xxx",
                "owner": {"type": "user", "user": {...}}
            }

        Security:
            - Validates response structure before returning
            - Logs errors server-side without exposing secrets
            - Returns sanitized errors to client
        """
        # Notion requires Basic authentication for token exchange
        auth = (self.config.client_id, self.config.client_secret)

        data = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": self.config.redirect_uri,
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.TOKEN_URL,
                    auth=auth,  # Basic auth with client_id:client_secret
                    json=data,  # Notion expects JSON body
                    headers={"Content-Type": "application/json"},
                    timeout=30.0
                )

                # Log response status (not body, to avoid leaking secrets)
                logger.debug(f"Notion token exchange response: {response.status_code}")

                response.raise_for_status()
                token_data = response.json()

                # Validate response structure
                if "error" in token_data:
                    # Log detailed error server-side
                    logger.error(f"Notion OAuth error: {token_data.get('error')}")
                    # Return sanitized error to client
                    raise HTTPException(
                        status_code=400,
                        detail="Failed to authorize Notion workspace. Please try again."
                    )

                # Validate required fields
                if "access_token" not in token_data:
                    logger.error("Notion token response missing access_token")
                    raise HTTPException(
                        status_code=500,
                        detail="Invalid response from Notion. Please try again."
                    )

                # Extract workspace information for logging (not returned to client)
                workspace_name = token_data.get("workspace_name", "Unknown")
                workspace_id = token_data.get("workspace_id", "Unknown")
                logger.info(
                    f"Successfully authorized Notion workspace: {workspace_name} "
                    f"(ID: {workspace_id[:8]}...)"
                )

                # Return token response
                # Note: expires_in is None because Notion tokens don't expire
                return OAuthTokenResponse(
                    access_token=token_data["access_token"],
                    refresh_token=None,  # Notion doesn't provide refresh tokens
                    expires_in=None,  # Tokens don't expire
                    token_type="Bearer",
                    scope=None  # Notion uses integration permissions, not OAuth scopes
                )

        except httpx.HTTPStatusError as e:
            # Log detailed error server-side
            logger.error(
                f"Failed to exchange Notion code for token: "
                f"status={e.response.status_code}, "
                f"body={e.response.text[:200]}"  # Log first 200 chars only
            )
            # Return sanitized error to client
            raise HTTPException(
                status_code=500,
                detail="Failed to complete Notion authorization. Please try again."
            )
        except httpx.HTTPError as e:
            # Log detailed error server-side
            logger.error(f"Network error during Notion token exchange: {e}")
            # Return sanitized error to client
            raise HTTPException(
                status_code=500,
                detail="Failed to connect to Notion. Please try again."
            )

    async def refresh_access_token(self, refresh_token: str) -> OAuthTokenResponse:
        """
        Refresh access token (NOT SUPPORTED by Notion).

        Notion OAuth tokens are permanent and do not expire. They remain valid
        indefinitely until explicitly revoked by the user or workspace admin
        through the Notion workspace settings.

        This is by design in Notion's OAuth implementation and simplifies the
        authentication flow. Revoked tokens must be handled through token
        validation checks in the API client.

        Args:
            refresh_token: The refresh token (not used, Notion doesn't provide refresh tokens)

        Raises:
            HTTPException: Always raises 501 Not Implemented

        Note:
            If Notion changes their OAuth behavior in the future to support
            token expiration, this method will need to be updated accordingly.

        Security:
            - Tokens remain valid until revoked, so validation is critical
            - API client should handle 401 errors and prompt re-authorization
        """
        logger.warning(
            "Attempted to refresh Notion token, but Notion OAuth tokens do not expire. "
            "Token remains valid until explicitly revoked by user or workspace admin."
        )
        raise HTTPException(
            status_code=501,
            detail=(
                "Notion OAuth tokens do not expire and do not require refresh. "
                "Token remains valid until revoked by user or workspace admin."
            )
        )

    async def revoke_token(self, access_token: str) -> bool:
        """
        Revoke a Notion access token.

        Note: Notion doesn't provide a programmatic token revocation endpoint.
        Users must revoke access through workspace settings:
        https://www.notion.so/my-integrations

        This method returns False to indicate programmatic revocation is not supported.

        Args:
            access_token: The access token to revoke

        Returns:
            False (programmatic revocation not supported by Notion)

        Security:
            - Users can revoke tokens through Notion workspace settings
            - Revoked tokens will return 401 errors on API calls
        """
        logger.warning(
            "Notion doesn't support programmatic token revocation. "
            "Users must revoke access through workspace settings: "
            "https://www.notion.so/my-integrations"
        )
        # Return False to indicate revocation is not supported programmatically
        return False

    async def validate_token(self, access_token: str) -> bool:
        """
        Validate that a Notion access token is still valid.

        Makes a lightweight API call to check if the token works.
        Uses the /users/me endpoint which requires minimal permissions.

        Args:
            access_token: The access token to validate

        Returns:
            True if token is valid, False otherwise

        Security:
            - Does not log token value
            - Returns boolean only (no sensitive info)
            - Uses minimal permission endpoint
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    "https://api.notion.com/v1/users/me",
                    headers={
                        "Authorization": f"Bearer {access_token}",
                        "Notion-Version": "2022-06-28",  # Required API version
                    },
                    timeout=30.0
                )
                is_valid = response.status_code == 200

                if not is_valid:
                    logger.debug(
                        f"Notion token validation failed: status={response.status_code}"
                    )
                else:
                    logger.debug("Notion token validation successful")

                return is_valid

        except httpx.HTTPError as e:
            logger.error(f"Failed to validate Notion token: {e}")
            return False


def create_notion_oauth_provider(
    client_id: str,
    client_secret: str,
    redirect_uri: str,
    scopes: Optional[List[str]] = None
) -> NotionOAuthProvider:
    """
    Factory function to create a Notion OAuth provider.

    Notion OAuth doesn't use traditional OAuth scopes. Instead, permissions are
    configured when creating the integration in the Notion developer portal:
    https://www.notion.so/my-integrations

    Integration capabilities that can be configured:
    - Read content
    - Update content
    - Insert content
    - Read comments
    - Create comments
    - Read user information (including email)

    Args:
        client_id: Notion OAuth client ID (from integration settings)
        client_secret: Notion OAuth client secret (from integration settings)
        redirect_uri: Callback URL for OAuth flow
        scopes: Not used by Notion (permissions set in integration settings)

    Returns:
        Configured NotionOAuthProvider instance

    Example:
        >>> provider = create_notion_oauth_provider(
        ...     client_id="your-client-id",
        ...     client_secret="your-client-secret",
        ...     redirect_uri="http://localhost:8000/servers/notion-mcp/auth-callback"
        ... )

    Security:
        - Client secret should never be logged or exposed
        - Redirect URI must match integration settings exactly
        - Provider name must match server ID without -mcp suffix
    """
    # Notion doesn't use OAuth scopes (permissions set in integration settings)
    # The scopes parameter is accepted for API consistency but not used
    if scopes:
        logger.warning(
            "Notion OAuth doesn't use scopes. Permissions are configured in "
            "integration settings at https://www.notion.so/my-integrations"
        )

    config = OAuthConfig(
        provider_name="notion",  # CRITICAL: Must match server ID without -mcp
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri=redirect_uri,
        scopes=[]  # Empty list (Notion doesn't use OAuth scopes)
    )

    logger.debug(f"Created Notion OAuth provider with redirect_uri={redirect_uri}")
    return NotionOAuthProvider(config)

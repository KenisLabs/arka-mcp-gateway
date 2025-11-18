"""
Slack OAuth Provider implementation.

Slack OAuth 2.0 documentation:
https://api.slack.com/authentication/oauth-v2

Security features:
- Non-expiring tokens (Slack OAuth v2 tokens do not expire)
- Token validation support
- Sanitized error messages
- Comprehensive logging
- Workspace-level authentication
"""
import httpx
from typing import Optional, List
from fastapi import HTTPException
from urllib.parse import urlencode
from .base import OAuthConfig, OAuthProvider, OAuthTokenResponse
import logging

logger = logging.getLogger(__name__)


class SlackOAuthProvider(OAuthProvider):
    """
    Slack OAuth 2.0 provider.

    Implements Slack's OAuth 2.0 flow with workspace-level authentication.
    Supports both user tokens and bot tokens based on scopes requested.
    """

    # Slack OAuth endpoints
    AUTH_URL = "https://slack.com/oauth/v2/authorize"
    TOKEN_URL = "https://slack.com/api/oauth.v2.access"
    USER_INFO_URL = "https://slack.com/api/auth.test"
    REVOKE_URL = "https://slack.com/api/auth.revoke"

    # Slack API base URL
    BASE_URL = "https://slack.com/api"

    def get_authorization_url(self, state: str) -> str:
        """
        Generate Slack OAuth authorization URL.

        For MCP server use case, we request USER scopes so actions are performed
        as the authenticated user (not as a bot).

        Args:
            state: Random state parameter for CSRF protection

        Returns:
            Authorization URL to redirect the user to
        """
        params = {
            "client_id": self.config.client_id,
            "redirect_uri": self.config.redirect_uri,
            "scope": "",  # Bot scopes (empty for user-only auth)
            "state": state,
            "user_scope": ",".join(self.config.scopes),  # User scopes for acting as user
        }
        return f"{self.AUTH_URL}?{urlencode(params)}"

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
            "redirect_uri": self.config.redirect_uri
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

                if not token_data.get("ok"):
                    error = token_data.get("error", "unknown_error")
                    logger.error(f"Slack OAuth error: {error}")
                    raise HTTPException(
                        status_code=400,
                        detail=f"Slack OAuth error: {error}"
                    )

                # Extract USER access token (prioritize user token over bot token)
                # For MCP use case, we want the user token so actions are performed as the user
                access_token = token_data.get("authed_user", {}).get("access_token")

                if not access_token:
                    # Fallback to bot token if user token not available (shouldn't happen with user_scope)
                    access_token = token_data.get("access_token")
                    logger.warning("Using bot token instead of user token - actions will appear from bot")

                if not access_token:
                    raise HTTPException(
                        status_code=500,
                        detail="No access token in Slack response"
                    )

                return OAuthTokenResponse(
                    access_token=access_token,
                    token_type="Bearer",
                    scope=token_data.get("scope"),
                    expires_in=token_data.get("expires_in")  # Slack may provide this
                )

        except httpx.HTTPError as e:
            logger.error(f"Failed to exchange Slack code for token: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to exchange authorization code: {str(e)}"
            )

    async def refresh_access_token(self, refresh_token: str) -> OAuthTokenResponse:
        """
        Slack OAuth v2 user tokens do not expire and do not support token refresh.

        This is by design in Slack's OAuth v2 implementation. User tokens remain
        valid indefinitely until explicitly revoked by the user or workspace admin.

        Unlike Google OAuth tokens which expire after 1 hour, Slack tokens are
        long-lived and do not require periodic refresh. This simplifies the
        authentication flow but means that revoked tokens must be handled
        through token validation checks.

        If you need to verify a token is still valid, use validate_token() instead.

        Reference: https://api.slack.com/authentication/oauth-v2

        Args:
            refresh_token: The refresh token (not used, Slack doesn't provide refresh tokens)

        Raises:
            HTTPException: Always raises 501 Not Implemented

        Note:
            If Slack changes their OAuth v2 behavior in the future to support
            token expiration, this method will need to be updated accordingly.
        """
        logger.warning(
            "Attempted to refresh Slack token, but Slack OAuth v2 tokens do not expire. "
            "Token remains valid until explicitly revoked."
        )
        raise HTTPException(
            status_code=501,
            detail="Slack OAuth v2 tokens do not expire and do not require refresh. "
                   "Token remains valid until revoked by user or workspace admin."
        )

    async def revoke_token(self, access_token: str) -> bool:
        """
        Revoke a Slack access token.

        Args:
            access_token: The access token to revoke

        Returns:
            True if revocation successful, False otherwise
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.REVOKE_URL,
                    headers={
                        "Authorization": f"Bearer {access_token}",
                        "Content-Type": "application/x-www-form-urlencoded"
                    },
                    timeout=30.0
                )
                data = response.json()
                return data.get("ok", False)

        except httpx.HTTPError as e:
            logger.error(f"Failed to revoke Slack token: {e}")
            return False

    async def validate_token(self, access_token: str) -> bool:
        """
        Validate that a Slack access token is still valid.

        Uses auth.test to check if the token works.

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
                data = response.json()
                return data.get("ok", False)

        except httpx.HTTPError as e:
            logger.error(f"Failed to validate Slack token: {e}")
            return False

    async def get_user_info(self, access_token: str) -> dict:
        """
        Get user information from Slack.

        Uses auth.test to validate token and get user/workspace info.

        Args:
            access_token: OAuth access token

        Returns:
            Dict containing user_id, team_id, and other workspace info

        Raises:
            httpx.HTTPStatusError: If request fails
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(
                self.USER_INFO_URL,
                headers={"Authorization": f"Bearer {access_token}"}
            )
            response.raise_for_status()
            data = response.json()

            if not data.get("ok"):
                raise ValueError(f"Slack auth.test failed: {data.get('error')}")

            return {
                "user_id": data.get("user_id"),
                "team_id": data.get("team_id"),
                "url": data.get("url"),
                "team": data.get("team"),
                "user": data.get("user"),
                "bot_id": data.get("bot_id"),  # Present if bot token
            }


def create_slack_oauth_provider(
    client_id: str,
    client_secret: str,
    redirect_uri: str,
    scopes: Optional[List[str]] = None
) -> SlackOAuthProvider:
    """
    Factory function to create a Slack OAuth provider.

    Args:
        client_id: Slack OAuth client ID
        client_secret: Slack OAuth client secret
        redirect_uri: Callback URL for OAuth flow
        scopes: List of Slack API scopes

    Returns:
        Configured SlackOAuthProvider instance

    Note:
        These are USER scopes (not bot scopes) so actions are performed
        as the authenticated user in the MCP server context.
    """
    if scopes is None:
        # Default USER scopes for MCP server - actions performed as user
        # These map to all 38 implemented Slack tools
        scopes = [
            # Channel/Conversation permissions (PUBLIC)
            "channels:read",        # list_channels, get_channel_info, list_pins
            "channels:write",       # send_message, create_channel, invite_to_channel, kick_from_channel, archive_channel, open_dm
            "channels:history",     # list_messages, list_thread_replies, search_messages

            # Private channel permissions
            "groups:read",          # list_channels (private), get_channel_info (private)
            "groups:write",         # send_message (private), invite/kick (private), archive_channel (private), open_dm (group)
            "groups:history",       # list_messages (private), list_thread_replies (private)

            # Direct message permissions
            "im:read",              # List DMs, get_channel_info (DM)
            "im:write",             # send_message (DM), open_dm
            "im:history",           # list_messages (DM), search_messages (DM)

            # Group DM permissions
            "mpim:read",            # List group DMs
            "mpim:write",           # send_message (group DM), open_dm (multi-person)
            "mpim:history",         # list_messages (group DM)

            # Messaging permissions
            "chat:write",           # send_message, update_message, delete_message, schedule_message, reply_to_thread

            # User permissions
            "users:read",           # list_users, get_user_info, find_user_by_email
            "users:read.email",     # find_user_by_email, get_user_info (with email)
            "users.profile:read",   # get_user_info (profile details)
            "users.profile:write",  # set_status, clear_status

            # Reaction permissions
            "reactions:read",       # list_reactions, view reactions on messages
            "reactions:write",      # add_reaction, remove_reaction

            # Pin permissions
            "pins:read",            # list_pins
            "pins:write",           # pin_message, unpin_message

            # File permissions
            "files:read",           # list_files, get_file_info, search_files
            "files:write",          # upload_file, delete_file

            # Search permissions
            "search:read",          # search_messages, search_files, search_all

            # Reminder permissions
            "reminders:read",       # list_reminders, get_reminder_info
            "reminders:write",      # create_reminder, delete_reminder
        ]

    config = OAuthConfig(
        provider_name="slack",
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri=redirect_uri,
        scopes=scopes
    )

    return SlackOAuthProvider(config)

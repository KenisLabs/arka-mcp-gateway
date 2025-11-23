"""
Google Tasks OAuth Provider implementation.

Google Tasks API OAuth 2.0 documentation:
https://developers.google.com/tasks/auth

Security features:
- Token refresh with rotation (inherited from GoogleOAuthProvider)
- Sanitized error messages
- Comprehensive logging
"""
from typing import Optional, List
from .base import OAuthConfig
from .google_base import GoogleOAuthProvider
import logging

logger = logging.getLogger(__name__)


class GoogleTasksOAuthProvider(GoogleOAuthProvider):
    """
    Google Tasks OAuth 2.0 provider.

    Extends GoogleOAuthProvider with Tasks-specific configuration.
    Inherits all OAuth flow logic from the base class.
    """

    # Tasks-specific validation endpoint
    USER_INFO_URL = "https://tasks.googleapis.com/tasks/v1/users/@me/lists"


def create_google_tasks_oauth_provider(
    client_id: str,
    client_secret: str,
    redirect_uri: str,
    scopes: Optional[List[str]] = None
) -> GoogleTasksOAuthProvider:
    """
    Factory function to create a Google Tasks OAuth provider.

    Args:
        client_id: Google OAuth client ID
        client_secret: Google OAuth client secret
        redirect_uri: Callback URL for OAuth flow
        scopes: List of Google Tasks API scopes

    Returns:
        Configured GoogleTasksOAuthProvider instance
    """
    if scopes is None:
        # Default scopes - full Tasks access
        scopes = [
            "https://www.googleapis.com/auth/tasks",
        ]

    config = OAuthConfig(
        provider_name="google_tasks",
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri=redirect_uri,
        scopes=scopes
    )

    return GoogleTasksOAuthProvider(config)

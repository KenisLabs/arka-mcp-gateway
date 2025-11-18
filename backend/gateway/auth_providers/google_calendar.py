"""
Google Calendar OAuth Provider implementation.

Google Calendar API OAuth 2.0 documentation:
https://developers.google.com/calendar/api/guides/auth

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


class GoogleCalendarOAuthProvider(GoogleOAuthProvider):
    """
    Google Calendar OAuth 2.0 provider.

    Extends GoogleOAuthProvider with Calendar-specific configuration.
    Inherits all OAuth flow logic from the base class.
    """

    # Calendar-specific validation endpoint
    USER_INFO_URL = "https://www.googleapis.com/calendar/v3/users/me/calendarList"


def create_google_calendar_oauth_provider(
    client_id: str,
    client_secret: str,
    redirect_uri: str,
    scopes: Optional[List[str]] = None
) -> GoogleCalendarOAuthProvider:
    """
    Factory function to create a Google Calendar OAuth provider.

    Args:
        client_id: Google OAuth client ID
        client_secret: Google OAuth client secret
        redirect_uri: Callback URL for OAuth flow
        scopes: List of Google Calendar API scopes

    Returns:
        Configured GoogleCalendarOAuthProvider instance
    """
    if scopes is None:
        # Default scopes - comprehensive Google Calendar access
        scopes = [
            "https://www.googleapis.com/auth/calendar",         # Full calendar access
            "https://www.googleapis.com/auth/calendar.events",  # Event management
        ]

    config = OAuthConfig(
        provider_name="google_calendar",
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri=redirect_uri,
        scopes=scopes
    )

    return GoogleCalendarOAuthProvider(config)

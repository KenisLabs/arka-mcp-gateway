"""
OAuth Provider Registry - Factory for creating OAuth providers.
"""
from typing import Dict, Optional
from .base import OAuthProvider
from .github import create_github_oauth_provider
from .gmail import create_gmail_oauth_provider
from .google_calendar import create_google_calendar_oauth_provider
from .slack import create_slack_oauth_provider
from .notion import create_notion_oauth_provider
from config import settings
from database import get_db
from gateway.oauth_db import get_oauth_credentials
import logging
import asyncio

logger = logging.getLogger(__name__)


class OAuthProviderRegistry:
    """
    Registry for OAuth providers.

    Creates and caches OAuth provider instances based on server type.
    """

    def __init__(self):
        """Initialize the OAuth provider registry"""
        self._providers: Dict[str, OAuthProvider] = {}
        self._initialize_providers()

    def _initialize_providers(self):
        """
        Initialize OAuth providers from database or environment variables.

        Precedence:
        1. Check database for OAuth credentials (configured via admin UI)
        2. Fall back to environment variables for backward compatibility

        Expected environment variables (if not in database):
        - GITHUB_OAUTH_CLIENT_ID
        - GITHUB_OAUTH_CLIENT_SECRET
        - GITHUB_OAUTH_REDIRECT_URI
        """
        # Note: This is synchronous initialization. For dynamic loading from database,
        # use get_provider_async() method instead.

        # Initialize GitHub provider from environment variables (backward compatibility)
        github_client_id = getattr(settings, 'github_oauth_client_id', None)
        github_client_secret = getattr(settings, 'github_oauth_client_secret', None)
        github_redirect_uri = getattr(settings, 'github_oauth_redirect_uri', None)

        if github_client_id and github_client_secret:
            try:
                self._providers["github-mcp"] = create_github_oauth_provider(
                    client_id=github_client_id,
                    client_secret=github_client_secret,
                    redirect_uri=github_redirect_uri or f"{settings.backend_url}/servers/github-mcp/auth-callback"
                )
                logger.info("GitHub OAuth provider initialized from environment variables")
            except Exception as e:
                logger.error(f"Failed to initialize GitHub OAuth provider: {e}")
        else:
            logger.info(
                "GitHub OAuth credentials not found in environment. "
                "Will check database when provider is requested."
            )

        # Initialize Gmail provider from environment variables (backward compatibility)
        gmail_client_id = getattr(settings, 'gmail_oauth_client_id', None)
        gmail_client_secret = getattr(settings, 'gmail_oauth_client_secret', None)
        gmail_redirect_uri = getattr(settings, 'gmail_oauth_redirect_uri', None)

        if gmail_client_id and gmail_client_secret:
            try:
                self._providers["gmail-mcp"] = create_gmail_oauth_provider(
                    client_id=gmail_client_id,
                    client_secret=gmail_client_secret,
                    redirect_uri=gmail_redirect_uri or f"{settings.backend_url}/servers/gmail-mcp/auth-callback"
                )
                logger.info("Gmail OAuth provider initialized from environment variables")
            except Exception as e:
                logger.error(f"Failed to initialize Gmail OAuth provider: {e}")
        else:
            logger.info(
                "Gmail OAuth credentials not found in environment. "
                "Will check database when provider is requested."
            )

        # Initialize Notion provider from environment variables (backward compatibility)
        notion_client_id = getattr(settings, 'notion_oauth_client_id', None)
        notion_client_secret = getattr(settings, 'notion_oauth_client_secret', None)
        notion_redirect_uri = getattr(settings, 'notion_oauth_redirect_uri', None)

        if notion_client_id and notion_client_secret:
            try:
                self._providers["notion-mcp"] = create_notion_oauth_provider(
                    client_id=notion_client_id,
                    client_secret=notion_client_secret,
                    redirect_uri=notion_redirect_uri or f"{settings.backend_url}/servers/notion-mcp/auth-callback"
                )
                logger.info("Notion OAuth provider initialized from environment variables")
            except Exception as e:
                logger.error(f"Failed to initialize Notion OAuth provider: {e}")
        else:
            logger.info(
                "Notion OAuth credentials not found in environment. "
                "Will check database when provider is requested."
            )

        # TODO: Initialize other providers when implemented (Jira, etc.)

    def get_provider(self, server_id: str) -> Optional[OAuthProvider]:
        """
        Get OAuth provider for a specific server.

        Args:
            server_id: MCP server ID (e.g., "github-mcp", "jira-mcp")

        Returns:
            OAuthProvider instance if available, None otherwise
        """
        return self._providers.get(server_id)

    def has_provider(self, server_id: str) -> bool:
        """
        Check if OAuth provider is available for a server.

        Args:
            server_id: MCP server ID

        Returns:
            True if provider is configured, False otherwise
        """
        return server_id in self._providers

    def clear_provider_cache(self, server_id: str):
        """
        Clear cached OAuth provider for a specific server.

        This should be called when OAuth credentials are updated or deleted
        to ensure the next request loads fresh credentials from the database.

        Args:
            server_id: MCP server ID to clear from cache
        """
        if server_id in self._providers:
            del self._providers[server_id]
            logger.info(f"Cleared OAuth provider cache for {server_id}")

    async def get_provider_async(self, server_id: str, db) -> Optional[OAuthProvider]:
        """
        Get OAuth provider for a specific server, checking database first.

        This method checks the database for OAuth credentials before falling back
        to the cached provider from environment variables.

        Args:
            server_id: MCP server ID (e.g., "github-mcp")
            db: Database session

        Returns:
            OAuthProvider instance if available, None otherwise
        """
        # Check if provider is already cached
        if server_id in self._providers:
            logger.debug(f"Using cached OAuth provider for {server_id}")
            return self._providers[server_id]

        # Try to load from database
        try:
            credentials = await get_oauth_credentials(db, server_id)
            if credentials:
                logger.info(f"Loading OAuth provider for {server_id} from database")

                # Create provider based on provider_name
                if credentials['provider_name'] == 'github':
                    provider = create_github_oauth_provider(
                        client_id=credentials['client_id'],
                        client_secret=credentials['client_secret'],  # Already decrypted
                        redirect_uri=credentials['redirect_uri'],
                        scopes=credentials['scopes']
                    )
                    # Cache the provider
                    self._providers[server_id] = provider
                    return provider
                elif credentials['provider_name'] == 'gmail':
                    provider = create_gmail_oauth_provider(
                        client_id=credentials['client_id'],
                        client_secret=credentials['client_secret'],  # Already decrypted
                        redirect_uri=credentials['redirect_uri'],
                        scopes=credentials['scopes']
                    )
                    # Cache the provider
                    self._providers[server_id] = provider
                    return provider
                elif credentials['provider_name'] == 'google_calendar':
                    provider = create_google_calendar_oauth_provider(
                        client_id=credentials['client_id'],
                        client_secret=credentials['client_secret'],  # Already decrypted
                        redirect_uri=credentials['redirect_uri'],
                        scopes=credentials['scopes']
                    )
                    # Cache the provider
                    self._providers[server_id] = provider
                    return provider
                elif credentials['provider_name'] == 'slack':
                    provider = create_slack_oauth_provider(
                        client_id=credentials['client_id'],
                        client_secret=credentials['client_secret'],  # Already decrypted
                        redirect_uri=credentials['redirect_uri'],
                        scopes=credentials['scopes']
                    )
                    # Cache the provider
                    self._providers[server_id] = provider
                    return provider
                elif credentials['provider_name'] == 'notion':
                    provider = create_notion_oauth_provider(
                        client_id=credentials['client_id'],
                        client_secret=credentials['client_secret'],  # Already decrypted
                        redirect_uri=credentials['redirect_uri'],
                        scopes=credentials['scopes']
                    )
                    # Cache the provider
                    self._providers[server_id] = provider
                    return provider
                else:
                    logger.warning(
                        f"Unknown provider_name '{credentials['provider_name']}' for {server_id}"
                    )
                    return None
        except Exception as e:
            logger.error(f"Failed to load OAuth provider from database for {server_id}: {e}")

        # No provider found
        logger.warning(f"No OAuth provider found for {server_id}")
        return None


# Global provider registry instance
_provider_registry: Optional[OAuthProviderRegistry] = None


def get_oauth_provider_registry() -> OAuthProviderRegistry:
    """
    Get the global OAuth provider registry instance.

    Returns:
        The global OAuthProviderRegistry instance
    """
    global _provider_registry
    if _provider_registry is None:
        _provider_registry = OAuthProviderRegistry()
    return _provider_registry


async def get_oauth_provider(server_id: str, db) -> Optional[OAuthProvider]:
    """
    Helper function to get OAuth provider for a server.

    This is a convenience function used by token refresh logic.
    It wraps get_oauth_provider_registry().get_provider_async()

    Args:
        server_id: MCP server ID (e.g., "gmail-mcp")
        db: Database session (for loading from database)

    Returns:
        OAuthProvider instance if available, None otherwise
    """
    registry = get_oauth_provider_registry()
    return await registry.get_provider_async(server_id, db)

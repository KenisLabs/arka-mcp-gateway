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
from .google_tasks import create_google_tasks_oauth_provider
from .supabase import create_supabase_oauth_provider
from .jira import create_jira_oauth_provider
from gateway.oauth_db import get_oauth_credentials
import logging

logger = logging.getLogger(__name__)


class OAuthProviderRegistry:
    """
    Registry for OAuth providers.

    Loads and caches OAuth provider instances from database configuration.
    All MCP server OAuth credentials must be configured via the admin UI.
    Environment variables are NOT supported for MCP server OAuth configuration.
    """

    def __init__(self):
        """
        Initialize the OAuth provider registry.

        Providers are loaded on-demand from the database when first requested.
        """
        self._providers: Dict[str, OAuthProvider] = {}
        logger.info(
            "OAuth provider registry initialized. "
            "Providers will be loaded from database on demand."
        )

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
        Get OAuth provider for a specific server from database.

        Checks cache first for performance, then loads from database if not cached.
        All MCP server OAuth credentials must be configured via admin UI.

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

                # Supabase integration
                if credentials['provider_name'] == 'supabase':
                    provider = create_supabase_oauth_provider(
                        client_id=credentials['client_id'],
                        client_secret=credentials['client_secret'],
                        redirect_uri=credentials['redirect_uri'],
                        scopes=credentials.get('scopes', []),
                    )
                    self._providers[server_id] = provider
                    return provider
                # Create provider based on provider_name
                if credentials['provider_name'] == 'github':
                    provider = create_github_oauth_provider(
                        client_id=credentials['client_id'],
                        client_secret=credentials['client_secret'],  # Already decrypted
                        redirect_uri=credentials['redirect_uri'],
                        scopes=credentials['scopes'],
                    )
                    # Cache the provider
                    self._providers[server_id] = provider
                    return provider
                elif credentials['provider_name'] == 'gmail':
                    provider = create_gmail_oauth_provider(
                        client_id=credentials['client_id'],
                        client_secret=credentials['client_secret'],  # Already decrypted
                        redirect_uri=credentials['redirect_uri'],
                        scopes=credentials['scopes'],
                    )
                    # Cache the provider
                    self._providers[server_id] = provider
                    return provider
                elif credentials['provider_name'] == 'google_calendar':
                    provider = create_google_calendar_oauth_provider(
                        client_id=credentials['client_id'],
                        client_secret=credentials['client_secret'],  # Already decrypted
                        redirect_uri=credentials['redirect_uri'],
                        scopes=credentials['scopes'],
                    )
                    # Cache the provider
                    self._providers[server_id] = provider
                    return provider
                elif credentials['provider_name'] == 'google_tasks':
                    provider = create_google_tasks_oauth_provider(
                        client_id=credentials['client_id'],
                        client_secret=credentials['client_secret'],  # Already decrypted
                        redirect_uri=credentials['redirect_uri'],
                        scopes=credentials.get('scopes', []),
                    )
                    # Cache the provider
                    self._providers[server_id] = provider
                    return provider
                elif credentials['provider_name'] == 'slack':
                    provider = create_slack_oauth_provider(
                        client_id=credentials['client_id'],
                        client_secret=credentials['client_secret'],  # Already decrypted
                        redirect_uri=credentials['redirect_uri'],
                        scopes=credentials['scopes'],
                    )
                    # Cache the provider
                    self._providers[server_id] = provider
                    return provider
                elif credentials['provider_name'] == 'notion':
                    provider = create_notion_oauth_provider(
                        client_id=credentials['client_id'],
                        client_secret=credentials['client_secret'],  # Already decrypted
                        redirect_uri=credentials['redirect_uri'],
                        scopes=credentials['scopes'],
                    )
                    # Cache the provider
                    self._providers[server_id] = provider
                    return provider
                # Jira integration
                elif credentials['provider_name'] == 'jira':
                    provider = create_jira_oauth_provider(
                        client_id=credentials['client_id'],
                        client_secret=credentials['client_secret'],
                        redirect_uri=credentials['redirect_uri'],
                        scopes=credentials.get('scopes', []),
                    )
                    self._providers[server_id] = provider
                    return provider
                else:
                    logger.warning(
                        f"Unknown provider_name '{credentials['provider_name']}' for {server_id}"
                    )
                    return None
        except Exception as e:
            logger.error(
                f"Failed to load OAuth provider from database for {server_id}: {e}"
            )

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

"""
Database operations for OAuth provider credentials.

Provides functions to fetch and decrypt OAuth credentials from the database.
"""
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from gateway.models import OAuthProviderCredentials
from gateway.crypto_utils import decrypt_string
from typing import Optional, Dict
import logging

logger = logging.getLogger(__name__)


async def get_oauth_credentials(
    db: AsyncSession,
    server_id: str
) -> Optional[Dict[str, any]]:
    """
    Get OAuth provider credentials for a specific MCP server.
    
    Automatically decrypts the client_secret field.
    
    Args:
        db: Database session
        server_id: MCP server ID (e.g., 'github-mcp')
        
    Returns:
        Dictionary with OAuth credentials, or None if not found:
        {
            'provider_name': str,
            'client_id': str,
            'client_secret': str (decrypted),
            'redirect_uri': str,
            'auth_url': str,
            'token_url': str,
            'scopes': list,
            'additional_config': dict
        }
    """
    result = await db.execute(
        select(OAuthProviderCredentials).where(
            OAuthProviderCredentials.mcp_server_id == server_id
        )
    )
    provider = result.scalar_one_or_none()
    
    if not provider:
        logger.warning(f"No OAuth credentials found for server: {server_id}")
        return None
    
    try:
        # Decrypt the client_secret
        decrypted_secret = decrypt_string(provider.client_secret)
        
        return {
            'provider_name': provider.provider_name,
            'client_id': provider.client_id,
            'client_secret': decrypted_secret,
            'redirect_uri': provider.redirect_uri,
            'auth_url': provider.auth_url,
            'token_url': provider.token_url,
            'scopes': provider.scopes or [],
            'additional_config': provider.additional_config or {}
        }
    except Exception as e:
        logger.error(f"Failed to decrypt OAuth credentials for {server_id}: {e}")
        raise


async def has_oauth_credentials(db: AsyncSession, server_id: str) -> bool:
    """
    Check if OAuth credentials exist for a specific MCP server.
    
    Args:
        db: Database session
        server_id: MCP server ID
        
    Returns:
        True if credentials exist, False otherwise
    """
    result = await db.execute(
        select(OAuthProviderCredentials).where(
            OAuthProviderCredentials.mcp_server_id == server_id
        )
    )
    provider = result.scalar_one_or_none()
    return provider is not None

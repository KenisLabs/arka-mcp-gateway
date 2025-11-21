"""
API endpoints for MCP server management.

Provides endpoints to:
- List all available MCP servers
- Get information about a specific server
- Get user's MCP preferences (with auth/enabled status)
- Toggle MCP enabled/disabled for user
- OAuth authorization flow (URL generation and callback)
"""

from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import RedirectResponse
from typing import List, Optional, Dict
from pydantic import BaseModel
from datetime import datetime
from .registry import get_registry, ServerRegistry
from .models import (
    MCPServerMetadata,
    OrganizationToolAccess,
    UserToolAccess,
    MCPServerConfiguration,
)
from .user_preferences import (
    get_preferences_store,
    UserPreferencesStore,
    UserMCPPreference,
    MCPCredentials,
)
from .auth_providers.registry import get_oauth_provider_registry, OAuthProviderRegistry
from auth.middleware import get_user_email
from config import settings
from database import get_db
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
import logging
import secrets

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/servers", tags=["servers"])

# In-memory store for OAuth states (for CSRF protection)
# TODO: Migrate to Redis or database for production
_oauth_states: Dict[str, Dict[str, str]] = {}


class UserMCPInfo(BaseModel):
    """MCP server info combined with user's authorization/enabled status"""

    # Metadata from registry
    id: str
    name: str
    description: str
    status: str
    type: str
    icon: str
    requires_auth: bool
    auth_type: Optional[str]

    # User-specific status
    is_authorized: bool
    is_enabled: bool
    authorized_at: Optional[str] = None
    expires_at: Optional[str] = None  # Token expiration timestamp


class ToggleRequest(BaseModel):
    """Request body for toggling MCP enabled/disabled"""

    enabled: bool


# get_current_user function removed - now using JWT middleware from auth.middleware


@router.get("", response_model=List[MCPServerMetadata])
async def list_servers(registry: ServerRegistry = Depends(get_registry)):
    """
    Get list of all available MCP servers.

    Returns static metadata about servers that can be connected to,
    regardless of user's authorization status.
    """
    return registry.get_available_servers()


@router.get("/me", response_model=List[UserMCPInfo])
async def list_user_servers(
    registry: ServerRegistry = Depends(get_registry),
    preferences_store: UserPreferencesStore = Depends(get_preferences_store),
    user_email: str = Depends(get_user_email),
    db: AsyncSession = Depends(get_db),
):
    """
    Get list of MCP servers for the current user with their preferences.

    Returns MCP metadata combined with user's authorization and enabled status.
    Filters servers based on cascade permissions (organization + user overrides).

    Requires authentication.
    """
    available_servers = registry.get_available_servers()
    user_prefs = await preferences_store.get_user_preferences(user_email)

    # Get configured servers (added by admin)
    result = await db.execute(
        select(MCPServerConfiguration).where(MCPServerConfiguration.is_enabled == True)
    )
    configured_server_ids = {config.server_id for config in result.scalars().all()}

    # Get organization-level access settings
    result = await db.execute(select(OrganizationToolAccess))
    org_access_map = {
        access.mcp_server_id: access.enabled for access in result.scalars().all()
    }

    # Get user-level access overrides
    result = await db.execute(
        select(UserToolAccess).where(UserToolAccess.user_email == user_email)
    )
    user_access_map = {
        access.mcp_server_id: access.enabled for access in result.scalars().all()
    }

    result = []
    for server in available_servers:
        # Check cascade permissions
        server_id = server.id

        # SECURITY FIX: Only show servers that admin has explicitly configured
        if server_id not in configured_server_ids:
            continue

        org_enabled = org_access_map.get(
            server_id, True
        )  # Default to enabled for configured servers
        user_override = user_access_map.get(server_id)

        # Calculate effective access: org must be enabled, then check user override
        if not org_enabled:
            effective_access = False
        elif user_override is not None:
            effective_access = user_override
        else:
            effective_access = True

        # Only include servers the user has effective access to
        if not effective_access:
            continue

        pref = user_prefs.mcp_preferences.get(server.id)

        # Extract expires_at from credentials if available
        expires_at = None
        if pref and pref.credentials and pref.credentials.expires_at:
            expires_at = pref.credentials.expires_at.isoformat()

        result.append(
            UserMCPInfo(
                id=server.id,
                name=server.name,
                description=server.description,
                status=server.status,
                type=server.type,
                icon=server.icon,
                requires_auth=server.requires_auth,
                auth_type=server.auth_type,
                is_authorized=pref.is_authorized if pref else False,
                is_enabled=pref.is_enabled if pref else server.default_enabled,
                authorized_at=(
                    pref.authorized_at.isoformat()
                    if pref and pref.authorized_at
                    else None
                ),
                expires_at=expires_at,
            )
        )

    return result


@router.get("/{server_id}", response_model=MCPServerMetadata)
async def get_server(server_id: str, registry: ServerRegistry = Depends(get_registry)):
    """
    Get detailed information about a specific server.

    Args:
        server_id: The unique identifier of the server

    Returns:
        MCPServerMetadata

    Raises:
        HTTPException 404: If server is not found in registry
    """
    server_metadata = registry.get_server_metadata(server_id)

    if server_metadata is None:
        raise HTTPException(status_code=404, detail=f"Server '{server_id}' not found")

    return server_metadata


@router.put("/{server_id}/toggle", response_model=UserMCPPreference)
async def toggle_server_enabled(
    server_id: str,
    toggle_request: ToggleRequest,
    preferences_store: UserPreferencesStore = Depends(get_preferences_store),
    user_email: str = Depends(get_user_email),
):
    """
    Toggle MCP enabled/disabled for the current user.

    Args:
        server_id: The unique identifier of the server
        toggle_request: Request body with enabled flag

    Returns:
        Updated UserMCPPreference

    Raises:
        HTTPException 401: If user is not authenticated
        HTTPException 404: If server is not found
    """
    try:
        updated_pref = await preferences_store.toggle_mcp_enabled(
            user_email, server_id, toggle_request.enabled
        )
        return updated_pref
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/{server_id}/disconnect")
async def disconnect_server(
    server_id: str,
    preferences_store: UserPreferencesStore = Depends(get_preferences_store),
    provider_registry: OAuthProviderRegistry = Depends(get_oauth_provider_registry),
    user_email: str = Depends(get_user_email),
    db: AsyncSession = Depends(get_db),
):
    """
    Disconnect/revoke OAuth authorization for a specific MCP server.

    Args:
        server_id: The unique identifier of the server
        preferences_store: User preferences store
        provider_registry: OAuth provider registry
        user_email: Current user's email from session

    Returns:
        Success message

    Raises:
        HTTPException 401: If user is not authenticated
        HTTPException 404: If server is not found or not authorized
    """
    try:
        # Get user preferences to check if authorized
        user_prefs = await preferences_store.get_user_preferences(user_email)
        server_pref = user_prefs.mcp_preferences.get(server_id)

        if not server_pref or not server_pref.is_authorized:
            raise HTTPException(
                status_code=404, detail=f"Server '{server_id}' is not authorized"
            )

        # Try to revoke token with OAuth provider (optional - may fail if provider doesn't support it)
        provider = await provider_registry.get_provider_async(server_id, db)
        if (
            provider
            and server_pref.credentials
            and server_pref.credentials.access_token
        ):
            try:
                await provider.revoke_token(server_pref.credentials.access_token)
                logger.info(f"Successfully revoked OAuth token for {server_id}")
            except Exception as e:
                logger.warning(f"Failed to revoke OAuth token for {server_id}: {e}")
                # Continue anyway - we'll delete local credentials even if revocation fails

        # Remove credentials from user preferences
        await preferences_store.revoke_mcp_authorization(user_email, server_id)

        logger.info(f"Successfully disconnected {server_id} for {user_email}")

        return {
            "success": True,
            "message": f"Successfully disconnected from {server_id}",
        }

    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error disconnecting {server_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to disconnect server")


class AuthURLResponse(BaseModel):
    """Response containing OAuth authorization URL"""

    auth_url: str
    state: str


@router.get("/{server_id}/auth-url", response_model=AuthURLResponse)
async def get_authorization_url(
    server_id: str,
    request: Request,
    provider_registry: OAuthProviderRegistry = Depends(get_oauth_provider_registry),
    user_email: str = Depends(get_user_email),
    db: AsyncSession = Depends(get_db),
):
    """
    Generate OAuth authorization URL for a specific MCP server.

    User clicks "Authorize" -> Frontend calls this endpoint -> Redirects to OAuth provider

    Args:
        server_id: The unique identifier of the server
        request: FastAPI request object
        provider_registry: OAuth provider registry
        user_email: Current user's email from session

    Returns:
        AuthURLResponse with authorization URL and state

    Raises:
        HTTPException 401: If user is not authenticated
        HTTPException 404: If OAuth provider is not configured for this server
    """
    # Check if OAuth provider is configured for this server
    provider = await provider_registry.get_provider_async(server_id, db)
    if not provider:
        raise HTTPException(
            status_code=404,
            detail=f"OAuth provider not configured for server '{server_id}'",
        )

    # Generate random state for CSRF protection
    state = secrets.token_urlsafe(32)

    # Store state with user email for validation in callback
    _oauth_states[state] = {
        "user_email": user_email,
        "server_id": server_id,
        "created_at": datetime.utcnow().isoformat(),
    }

    # Generate authorization URL
    auth_url = provider.get_authorization_url(state)

    logger.info(f"Generated OAuth URL for {user_email} -> {server_id}")

    return AuthURLResponse(auth_url=auth_url, state=state)


@router.get("/{server_id}/auth-callback")
async def oauth_callback(
    server_id: str,
    code: Optional[str] = None,
    state: Optional[str] = None,
    error: Optional[str] = None,
    error_description: Optional[str] = None,
    provider_registry: OAuthProviderRegistry = Depends(get_oauth_provider_registry),
    preferences_store: UserPreferencesStore = Depends(get_preferences_store),
    db: AsyncSession = Depends(get_db),
):
    """
    OAuth callback endpoint - handles redirect from OAuth provider.

    OAuth provider redirects here with code/state -> Exchange code for token -> Store credentials

    Args:
        server_id: The unique identifier of the server
        code: Authorization code from OAuth provider
        state: State parameter for CSRF protection
        error: Error code if authorization failed
        error_description: Human-readable error description
        provider_registry: OAuth provider registry
        preferences_store: User preferences store

    Returns:
        RedirectResponse to frontend dashboard with success/error message

    Raises:
        HTTPException 400: If state is invalid or missing
        HTTPException 404: If OAuth provider is not configured
        HTTPException 500: If token exchange fails
    """
    # Check for OAuth errors
    if error:
        logger.error(f"OAuth error for {server_id}: {error} - {error_description}")
        return RedirectResponse(
            url=f"{settings.FRONTEND_URL}/dashboard?auth_error={error}&description={error_description or ''}"
        )

    # Validate state parameter
    if not state or state not in _oauth_states:
        raise HTTPException(
            status_code=400, detail="Invalid or expired OAuth state parameter"
        )

    # Get state data and remove it (one-time use)
    state_data = _oauth_states.pop(state)
    user_email = state_data["user_email"]
    expected_server_id = state_data["server_id"]

    # Verify server_id matches
    if server_id != expected_server_id:
        raise HTTPException(
            status_code=400, detail="Server ID mismatch in OAuth callback"
        )

    # Validate code parameter
    if not code:
        raise HTTPException(
            status_code=400, detail="Missing authorization code in OAuth callback"
        )

    # Get OAuth provider
    provider = await provider_registry.get_provider_async(server_id, db)
    if not provider:
        raise HTTPException(
            status_code=404,
            detail=f"OAuth provider not configured for server '{server_id}'",
        )

    try:
        # Exchange code for access token
        token_response = await provider.exchange_code_for_token(code)

        # Store credentials in user preferences
        credentials = MCPCredentials(
            access_token=token_response.access_token,
            refresh_token=token_response.refresh_token,
            expires_at=None,  # TODO: Calculate expiry from expires_in
        )

        await preferences_store.authorize_mcp(user_email, server_id, credentials)

        logger.info(f"Successfully authorized {server_id} for {user_email}")

        # Redirect back to dashboard with success message
        return RedirectResponse(
            url=f"{settings.FRONTEND_URL}/dashboard?auth_success=true"
        )

    except HTTPException as e:
        # Re-raise HTTP exceptions
        logger.error(f"OAuth token exchange failed: {e.detail}")
        return RedirectResponse(
            url=f"{settings.FRONTEND_URL}/dashboard?auth_error=token_exchange_failed&description={e.detail}"
        )
    except Exception as e:
        # Catch any other errors
        logger.error(f"Unexpected error in OAuth callback: {str(e)}")
        return RedirectResponse(
            url=f"{settings.FRONTEND_URL}/dashboard?auth_error=unknown_error&description={str(e)}"
        )

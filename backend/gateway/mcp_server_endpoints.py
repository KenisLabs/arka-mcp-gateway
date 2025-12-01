"""API endpoints for MCP server configuration management.

This module provides endpoints for:
1. Listing available MCP servers from catalog
2. Listing configured MCP servers
3. Adding new MCP servers with credentials
4. Updating MCP server configurations
5. Removing MCP servers
"""

import json
import logging
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field

from database import get_db
from auth.rbac import require_admin
from gateway.models import (
    MCPServerConfiguration,
    OAuthProviderCredentials,
    AuditLog,
    UserCredential,
)
from gateway.crypto_utils import encrypt_string, decrypt_string
from gateway.auth_providers.registry import get_oauth_provider_registry
from config import settings

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/admin", tags=["admin-mcp-servers"])


# ============================================================================
# Pydantic Models for Request/Response
# ============================================================================


class MCPServerCatalogItem(BaseModel):
    """Single MCP server from the catalog."""

    id: str
    name: str
    display_name: str
    description: str
    category: str
    icon: str
    version: str
    publisher: str
    requires_auth: bool
    auth_type: str
    auth_fields: List[dict]
    documentation_url: str
    setup_instructions: str
    capabilities: List[str]
    popular: bool


class ConfiguredMCPServer(BaseModel):
    """Configured MCP server response."""

    id: str
    server_id: str
    display_name: str
    description: Optional[str]
    category: Optional[str]
    icon: Optional[str]
    is_enabled: bool
    has_credentials: bool
    added_by: str
    created_at: str
    updated_at: str


class AddMCPServerRequest(BaseModel):
    """Request to add a new MCP server."""

    server_id: str = Field(..., description="Server ID from catalog")
    display_name: Optional[str] = Field(None, description="Custom display name")
    credentials: dict = Field(..., description="OAuth credentials and configuration")


class UpdateMCPServerRequest(BaseModel):
    """Request to update MCP server configuration."""

    display_name: Optional[str] = None
    description: Optional[str] = None
    is_enabled: Optional[bool] = None
    credentials: Optional[dict] = None


# ============================================================================
# Helper Functions
# ============================================================================


def load_catalog():
    """Load MCP server catalog from JSON file."""
    import os

    # Shared directory is now inside backend/shared
    catalog_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),  # Go up from gateway/ to backend/
        "shared",
        "mcp_servers_catalog.json",
    )
    with open(catalog_path, "r") as f:
        return json.load(f)


async def log_admin_action(
    db: AsyncSession,
    actor_email: str,
    action: str,
    resource_type: str,
    resource_id: str,
    details: dict,
):
    """
    Log admin action to audit log.

    **Enterprise Edition Feature**: Audit logging is only available in the
    Enterprise Edition. This function is a no-op in the Community Edition.
    """
    # Audit logging is an Enterprise Edition feature
    # This function is stubbed out in Community Edition
    pass


# ============================================================================
# API Endpoints
# ============================================================================


@router.get("/mcp-servers/catalog", response_model=List[MCPServerCatalogItem])
async def list_catalog_servers(user: dict = Depends(require_admin)):
    """List all available MCP servers from the catalog.

    Returns:
        List of MCP servers that can be added to the organization
    """
    try:
        catalog = load_catalog()
        return catalog["catalog"]
    except Exception as e:
        logger.error(f"Error loading MCP server catalog: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to load MCP server catalog",
        )


@router.get("/mcp-servers/configured", response_model=List[ConfiguredMCPServer])
async def list_configured_servers(
    db: AsyncSession = Depends(get_db), user: dict = Depends(require_admin)
):
    """List all MCP servers that have been configured/added.

    Returns:
        List of configured MCP servers with their status
    """
    try:
        # Get all configured servers
        result = await db.execute(
            select(MCPServerConfiguration).order_by(MCPServerConfiguration.created_at)
        )
        servers = result.scalars().all()

        # Check if each has credentials
        configured_servers = []
        for server in servers:
            # Check if OAuth credentials exist
            cred_result = await db.execute(
                select(OAuthProviderCredentials).where(
                    OAuthProviderCredentials.mcp_server_id == server.server_id
                )
            )
            has_credentials = cred_result.scalar_one_or_none() is not None

            configured_servers.append(
                ConfiguredMCPServer(
                    id=server.id,
                    server_id=server.server_id,
                    display_name=server.display_name,
                    description=server.description,
                    category=server.category,
                    icon=server.icon,
                    is_enabled=server.is_enabled,
                    has_credentials=has_credentials,
                    added_by=server.added_by,
                    created_at=server.created_at.isoformat(),
                    updated_at=server.updated_at.isoformat(),
                )
            )

        return configured_servers

    except Exception as e:
        logger.error(f"Error listing configured MCP servers: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list configured servers",
        )


@router.post("/mcp-servers", status_code=status.HTTP_201_CREATED)
async def add_mcp_server(
    request: AddMCPServerRequest,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(require_admin),
):
    """Add a new MCP server configuration with credentials.

    Args:
        request: Server details and credentials

    Returns:
        Created server configuration
    """
    try:
        # Check if server configuration already exists
        existing_config = await db.execute(
            select(MCPServerConfiguration).where(
                MCPServerConfiguration.server_id == request.server_id
            )
        )
        if existing_config.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"MCP server '{request.server_id}' is already configured. Please check your configured servers list or remove the existing configuration first.",
            )

        # Check if OAuth credentials already exist (from previous partial setup)
        existing_creds = await db.execute(
            select(OAuthProviderCredentials).where(
                OAuthProviderCredentials.mcp_server_id == request.server_id
            )
        )
        if existing_creds.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"OAuth credentials for '{request.server_id}' already exist. This server may have been partially configured. Please contact an administrator to clean up the database or use a different server.",
            )

        # Load catalog to get server details
        catalog = load_catalog()
        catalog_server = next(
            (s for s in catalog["catalog"] if s["id"] == request.server_id), None
        )
        if not catalog_server:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Server '{request.server_id}' not found in catalog",
            )

        # Create server configuration
        server_config = MCPServerConfiguration(
            server_id=request.server_id,
            display_name=request.display_name or catalog_server["display_name"],
            description=catalog_server["description"],
            category=catalog_server["category"],
            icon=catalog_server["icon"],
            is_enabled=True,
            added_by=user.get("sub"),
        )
        db.add(server_config)
        await db.flush()

        # Store OAuth credentials if provided
        if catalog_server["requires_auth"] and request.credentials:
            # Encrypt sensitive fields
            encrypted_credentials = {}
            for key, value in request.credentials.items():
                if (
                    "secret" in key.lower()
                    or "password" in key.lower()
                    or "token" in key.lower()
                ):
                    encrypted_credentials[key] = encrypt_string(value)
                else:
                    encrypted_credentials[key] = value

            # Determine OAuth URLs based on server type
            oauth_config = {
                "github-mcp": {
                    "auth_url": "https://github.com/login/oauth/authorize",
                    "token_url": "https://github.com/login/oauth/access_token",
                    "scopes": ["repo", "user"],
                },
                "gmail-mcp": {
                    "auth_url": "https://accounts.google.com/o/oauth2/v2/auth",
                    "token_url": "https://oauth2.googleapis.com/token",
                    "scopes": [
                        "https://www.googleapis.com/auth/gmail.readonly",
                        "https://www.googleapis.com/auth/gmail.modify",
                        "https://www.googleapis.com/auth/gmail.labels",
                        "https://www.googleapis.com/auth/gmail.send",
                    ],
                },
                "gcal-mcp": {
                    "auth_url": "https://accounts.google.com/o/oauth2/v2/auth",
                    "token_url": "https://oauth2.googleapis.com/token",
                    "scopes": [
                        "https://www.googleapis.com/auth/calendar",
                        "https://www.googleapis.com/auth/calendar.events",
                    ],
                },
                "gtasks-mcp": {
                    "auth_url": "https://accounts.google.com/o/oauth2/v2/auth",
                    "token_url": "https://oauth2.googleapis.com/token",
                    "scopes": [
                        "https://www.googleapis.com/auth/tasks",
                    ],
                },
                "jira-mcp": {
                    "auth_url": "https://auth.atlassian.com/authorize",
                    "token_url": "https://auth.atlassian.com/oauth/token",
                    # Updated scopes as per requirements
                    "scopes": [],
                },
                "slack-mcp": {
                    "auth_url": "https://slack.com/oauth/v2/authorize",
                    "token_url": "https://slack.com/api/oauth.v2.access",
                    "scopes": [
                        # Channel/Conversation permissions (PUBLIC)
                        "channels:read",  # View basic information about public channels
                        "channels:write",  # Manage public channels and create new ones
                        "channels:history",  # View messages in public channels
                        # User permissions
                        "users:read",  # View people in workspace
                        "users:read.email",  # View email addresses
                        "users.profile:read",  # View profile details
                        "users.profile:write",  # Edit profile and status
                        # Group/Private channel permissions
                        "groups:read",  # View basic info about private channels
                        "groups:write",  # Manage private channels
                        "groups:history",  # View messages in private channels
                        # Direct message permissions
                        "im:read",  # View basic info about DMs
                        "im:write",  # Start DMs
                        "im:history",  # View messages in DMs
                        # Multi-party direct message permissions
                        "mpim:read",  # View basic info about group DMs
                        "mpim:write",  # Start group DMs
                        "mpim:history",  # View messages in group DMs
                        # Chat/Message permissions
                        "chat:write",  # Send messages
                        # File permissions
                        "files:read",  # View files
                        "files:write",  # Upload and edit files
                        # Pin permissions
                        "pins:read",  # View pinned content
                        "pins:write",  # Add and remove pins
                        # Reaction permissions
                        "reactions:read",  # View emoji reactions
                        "reactions:write",  # Add and edit reactions
                        # Other permissions
                        "emoji:read",  # View custom emoji
                        "search:read",  # Search workspace content
                        "team:read",  # View workspace info
                        "usergroups:read",  # View user groups
                        "usergroups:write",  # Create and manage user groups
                    ],
                },
                "gitlab-mcp": {
                    "auth_url": f"{encrypted_credentials.get('gitlab_url', 'https://gitlab.com')}/oauth/authorize",
                    "token_url": f"{encrypted_credentials.get('gitlab_url', 'https://gitlab.com')}/oauth/token",
                    "scopes": ["api", "read_user", "read_repository"],
                },
            }

            config = oauth_config.get(
                request.server_id, {"auth_url": "", "token_url": "", "scopes": []}
            )

            # Map server IDs to OAuth provider names (must match factory function provider_name)
            server_to_provider_name = {
                "github-mcp": "github",
                "gmail-mcp": "gmail",
                "gcal-mcp": "google_calendar",
                "gtasks-mcp": "google_tasks",
                "jira-mcp": "jira",
                "slack-mcp": "slack",
                "gitlab-mcp": "gitlab",
                "linear-mcp": "linear",
                "notion-mcp": "notion",
                "google-drive-mcp": "google_drive",
                "confluence-mcp": "confluence",
                "asana-mcp": "asana",
                "zendesk-mcp": "zendesk",
                "salesforce-mcp": "salesforce",
            }

            provider_name = server_to_provider_name.get(
                request.server_id, catalog_server["name"].lower().replace(" ", "_")
            )

            oauth_creds = OAuthProviderCredentials(
                mcp_server_id=request.server_id,
                provider_name=provider_name,
                client_id=encrypted_credentials.get("client_id", ""),
                client_secret=encrypted_credentials.get("client_secret", ""),
                redirect_uri=encrypted_credentials.get(
                    "redirect_uri",
                    f"{settings.backend_url}/servers/{request.server_id}/auth-callback",
                ),
                auth_url=config["auth_url"],
                token_url=config["token_url"],
                scopes=config["scopes"],
                additional_config=encrypted_credentials,
            )
            db.add(oauth_creds)

        # Log action
        await log_admin_action(
            db,
            user.get("sub"),
            "add_mcp_server",
            "mcp_server",
            request.server_id,
            {"display_name": server_config.display_name},
        )

        await db.commit()

        # Clear cached OAuth provider to ensure fresh credentials are loaded on next request
        if catalog_server["requires_auth"] and request.credentials:
            registry = get_oauth_provider_registry()
            registry.clear_provider_cache(request.server_id)
            logger.info(
                f"Cleared OAuth provider cache for newly created server: {request.server_id}"
            )

        logger.info(f"Admin {user.get('sub')} added MCP server: {request.server_id}")

        return {
            "message": "MCP server added successfully",
            "server_id": request.server_id,
            "display_name": server_config.display_name,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error adding MCP server: {e}", exc_info=True)
        await db.rollback()

        # Provide more specific error messages
        error_msg = str(e)
        if "duplicate key" in error_msg.lower():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"This MCP server is already configured. Please check your configured servers list or contact an administrator.",
            )
        elif "foreign key" in error_msg.lower():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid reference in configuration. Please check your input and try again.",
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to add MCP server: {error_msg}",
            )


@router.put("/mcp-servers/{server_id}")
async def update_mcp_server(
    server_id: str,
    request: UpdateMCPServerRequest,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(require_admin),
):
    """Update MCP server configuration.

    Args:
        server_id: Server ID to update
        request: Fields to update

    Returns:
        Success message
    """
    try:
        # Get server configuration
        result = await db.execute(
            select(MCPServerConfiguration).where(
                MCPServerConfiguration.server_id == server_id
            )
        )
        server = result.scalar_one_or_none()
        if not server:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"MCP server '{server_id}' not found",
            )

        # Update fields
        if request.display_name is not None:
            server.display_name = request.display_name
        if request.description is not None:
            server.description = request.description
        if request.is_enabled is not None:
            server.is_enabled = request.is_enabled

        # Track if OAuth credentials are being changed (for user token invalidation)
        credentials_changed = False
        credentials_updated = False

        # Update credentials if provided
        if request.credentials:
            result = await db.execute(
                select(OAuthProviderCredentials).where(
                    OAuthProviderCredentials.mcp_server_id == server_id
                )
            )
            oauth_creds = result.scalar_one_or_none()

            if oauth_creds:
                # Update credentials - single pass through provided fields
                for key, value in request.credentials.items():
                    # Skip if value is empty or None
                    if not value:
                        continue

                    old_value = getattr(oauth_creds, key, None)
                    is_sensitive = any(
                        s in key.lower() for s in ["secret", "password", "token"]
                    )

                    if is_sensitive:
                        # Encrypt and store sensitive fields
                        encrypted_value = encrypt_string(value)
                        if old_value != encrypted_value:
                            setattr(oauth_creds, key, encrypted_value)
                            credentials_changed = True  # Triggers token invalidation
                            oauth_creds.updated_at = (
                                datetime.utcnow()
                            )  # Track when secret was updated
                    else:
                        # Update non-sensitive fields (client_id, redirect_uri, scopes, etc.)
                        if old_value != value:
                            setattr(oauth_creds, key, value)
                            credentials_updated = True  # Triggers cache clear only

        # Log action
        await log_admin_action(
            db,
            user.get("sub"),
            "update_mcp_server",
            "mcp_server",
            server_id,
            {"display_name": request.display_name, "is_enabled": request.is_enabled},
        )

        await db.commit()

        # If OAuth credentials changed (client_id/client_secret), invalidate all user tokens
        invalidated_count = 0
        if credentials_changed:
            # Invalidate all user credentials for this server
            # User tokens were issued by the old OAuth app and won't work with new credentials
            result = await db.execute(
                select(UserCredential).where(
                    UserCredential.server_id == server_id,
                    UserCredential.is_authorized == True,
                )
            )
            user_creds = result.scalars().all()

            invalidated_count = len(user_creds)
            for cred in user_creds:
                cred.is_authorized = False
                cred.access_token = None
                cred.refresh_token = None
                cred.expires_at = None
                cred.authorized_at = None

            await db.commit()

            logger.warning(
                f"Invalidated {invalidated_count} user credentials for {server_id} "
                f"due to OAuth credentials change (client_id/client_secret updated)"
            )

        # Always clear cached OAuth provider when ANY credentials are updated
        # This ensures changes to redirect_uri, scopes, auth_url, client_secret, etc. are reflected
        if credentials_updated or credentials_changed:
            registry = get_oauth_provider_registry()
            registry.clear_provider_cache(server_id)
            logger.info(
                f"Cleared OAuth provider cache for {server_id} due to credential update"
            )

        logger.info(f"Admin {user.get('sub')} updated MCP server: {server_id}")

        return {
            "message": "MCP server updated successfully",
            "invalidated_users": invalidated_count,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating MCP server: {e}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update MCP server: {str(e)}",
        )


@router.delete("/mcp-servers/{server_id}")
async def remove_mcp_server(
    server_id: str,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(require_admin),
):
    """Remove an MCP server configuration.

    Args:
        server_id: Server ID to remove

    Returns:
        Success message
    """
    try:
        # Get server configuration
        result = await db.execute(
            select(MCPServerConfiguration).where(
                MCPServerConfiguration.server_id == server_id
            )
        )
        server = result.scalar_one_or_none()
        if not server:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"MCP server '{server_id}' not found",
            )

        # Delete all user credentials for this server
        user_creds_result = await db.execute(
            select(UserCredential).where(UserCredential.server_id == server_id)
        )
        user_creds = user_creds_result.scalars().all()
        deleted_user_creds_count = len(user_creds)
        for cred in user_creds:
            await db.delete(cred)

        # Delete OAuth credentials
        cred_result = await db.execute(
            select(OAuthProviderCredentials).where(
                OAuthProviderCredentials.mcp_server_id == server_id
            )
        )
        oauth_creds = cred_result.scalar_one_or_none()
        if oauth_creds:
            await db.delete(oauth_creds)

        # Delete server configuration
        await db.delete(server)

        # Log action
        await log_admin_action(
            db,
            user.get("sub"),
            "remove_mcp_server",
            "mcp_server",
            server_id,
            {"display_name": server.display_name},
        )

        await db.commit()

        # Clear cached OAuth provider when server is deleted
        registry = get_oauth_provider_registry()
        registry.clear_provider_cache(server_id)
        logger.info(f"Cleared OAuth provider cache for deleted server: {server_id}")

        if deleted_user_creds_count > 0:
            logger.warning(
                f"Deleted {deleted_user_creds_count} user credential(s) for {server_id} "
                f"during server removal"
            )

        logger.info(f"Admin {user.get('sub')} removed MCP server: {server_id}")

        return {
            "message": "MCP server removed successfully",
            "deleted_user_credentials": deleted_user_creds_count,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error removing MCP server: {e}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to remove MCP server: {str(e)}",
        )


@router.get("/mcp-servers/{server_id}/credentials")
async def get_mcp_server_credentials(
    server_id: str,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(require_admin),
):
    """Get MCP server credentials (decrypted for editing).

    Args:
        server_id: Server ID

    Returns:
        Decrypted credentials (excluding sensitive fields)
    """
    try:
        # Get OAuth credentials
        result = await db.execute(
            select(OAuthProviderCredentials).where(
                OAuthProviderCredentials.mcp_server_id == server_id
            )
        )
        oauth_creds = result.scalar_one_or_none()

        if not oauth_creds:
            # Return empty credentials if none exist yet
            return {
                "client_id": "",
                "client_secret_hint": "",
                "client_secret_configured": False,
                "client_secret_updated_at": None,
                "redirect_uri": f"{settings.backend_url}/servers/{server_id}/auth-callback",
                "scopes": [],
                "additional_config": {},
            }

        # Return credentials with secret hint (not actual secret)
        try:
            client_id = (
                decrypt_string(oauth_creds.client_id) if oauth_creds.client_id else ""
            )
        except:
            client_id = oauth_creds.client_id or ""

        # Create secret hint: first 2 + last 2 characters
        client_secret_hint = "****"
        if oauth_creds.client_secret:
            try:
                decrypted_secret = decrypt_string(oauth_creds.client_secret)
                if len(decrypted_secret) > 4:
                    client_secret_hint = (
                        f"{decrypted_secret[:2]}******{decrypted_secret[-2:]}"
                    )
                elif len(decrypted_secret) > 0:
                    client_secret_hint = "****"
            except:
                client_secret_hint = "****"

        return {
            "client_id": client_id,
            "client_secret_hint": client_secret_hint,
            "client_secret_configured": bool(oauth_creds.client_secret),
            "client_secret_updated_at": (
                oauth_creds.updated_at.isoformat() if oauth_creds.updated_at else None
            ),
            "redirect_uri": oauth_creds.redirect_uri
            or f"{settings.backend_url}/servers/{server_id}/auth-callback",
            "scopes": oauth_creds.scopes or [],
            "additional_config": {
                k: (
                    v
                    if "secret" not in k.lower() and "password" not in k.lower()
                    else "••••"  # Use bullet instead of asterisk for consistency
                )
                for k, v in (oauth_creds.additional_config or {}).items()
            },
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting MCP server credentials: {e}", exc_info=True)
        # Return empty credentials on error for testing
        return {
            "client_id": "",
            "client_secret_hint": "",
            "client_secret_configured": False,
            "client_secret_updated_at": None,
            "redirect_uri": f"{settings.backend_url}/servers/{server_id}/auth-callback",
            "scopes": [],
            "additional_config": {},
        }

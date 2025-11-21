"""
Admin endpoints for managing organization and user tool access.

Provides endpoints for:
- Managing organization-level tool access (enable/disable MCP servers)
- Managing user-level tool access overrides
- Listing users
- Creating users with temporary passwords
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from gateway.models import (
    OrganizationToolAccess,
    UserToolAccess,
    User,
    OAuthProviderCredentials,
    UserCredential,
)
from gateway.crypto_utils import encrypt_string, decrypt_string
from gateway.auth_providers.registry import get_oauth_provider_registry
from auth.rbac import require_admin
from auth.password_utils import generate_temporary_password, hash_password
from pydantic import BaseModel, EmailStr
from typing import Optional
import json
from pathlib import Path
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/admin", tags=["admin"])

# Load MCP servers from JSON (now inside backend/shared)
MCP_SERVERS_FILE = Path(__file__).parent.parent / "shared" / "mcp_servers.json"


def load_mcp_servers():
    """Load MCP servers from shared JSON file."""
    try:
        with open(MCP_SERVERS_FILE, "r") as f:
            data = json.load(f)
            return data.get("servers", [])
    except FileNotFoundError:
        logger.error(f"MCP servers file not found: {MCP_SERVERS_FILE}")
        return []
    except json.JSONDecodeError:
        logger.error(f"Invalid JSON in MCP servers file: {MCP_SERVERS_FILE}")
        return []


@router.get("/organization/tools")
async def list_organization_tools(
    admin: dict = Depends(require_admin), db: AsyncSession = Depends(get_db)
):
    """
    List all MCP servers with organization-level access status.

    Returns list of MCP servers from JSON with their organization-level
    enabled/disabled status.

    Args:
        admin: Current admin user (from JWT)
        db: Database session

    Returns:
        List of tools with organization access status
    """
    # Load MCP servers from JSON
    mcp_servers = load_mcp_servers()

    # Get organization-level access settings from database
    result = await db.execute(select(OrganizationToolAccess))
    org_access_map = {
        access.mcp_server_id: access.enabled for access in result.scalars().all()
    }

    # Combine JSON data with database access settings
    tools = []
    for server in mcp_servers:
        server_id = server.get("id")
        tools.append(
            {
                "id": server_id,
                "name": server.get("name"),
                "description": server.get("description"),
                "enabled": org_access_map.get(server_id, True),  # Default to enabled
                "provider": server.get("provider", {}),
            }
        )

    return {"tools": tools}


@router.put("/organization/tools/{server_id}/toggle")
async def toggle_organization_tool(
    server_id: str,
    enabled: bool,
    admin: dict = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """
    Enable or disable a tool at the organization level.

    When disabled at org level, no users can access the tool regardless of
    user-level settings.

    Args:
        server_id: MCP server ID
        enabled: True to enable, False to disable
        admin: Current admin user (from JWT)
        db: Database session

    Returns:
        Success message
    """
    # Verify server exists in JSON
    mcp_servers = load_mcp_servers()
    server_exists = any(s.get("id") == server_id for s in mcp_servers)
    if not server_exists:
        raise HTTPException(status_code=404, detail=f"Server {server_id} not found")

    # Check if org access record exists
    result = await db.execute(
        select(OrganizationToolAccess).where(
            OrganizationToolAccess.mcp_server_id == server_id
        )
    )
    org_access = result.scalar_one_or_none()

    if org_access:
        # Update existing record
        org_access.enabled = enabled
    else:
        # Create new record
        org_access = OrganizationToolAccess(mcp_server_id=server_id, enabled=enabled)
        db.add(org_access)

    await db.flush()

    logger.info(
        f"Admin {admin.get('sub')} {'enabled' if enabled else 'disabled'} "
        f"tool {server_id} at organization level"
    )

    return {
        "message": f"Tool {server_id} {'enabled' if enabled else 'disabled'} at organization level",
        "server_id": server_id,
        "enabled": enabled,
    }


@router.get("/users")
async def list_users(
    admin: dict = Depends(require_admin), db: AsyncSession = Depends(get_db)
):
    """
    List all users in the system.

    Args:
        admin: Current admin user (from JWT)
        db: Database session

    Returns:
        List of users with their roles
    """
    result = await db.execute(select(User))
    users = result.scalars().all()

    return {
        "users": [
            {
                "email": user.email,
                "name": user.name,
                "role": user.role,
                "created_at": user.created_at.isoformat() if user.created_at else None,
            }
            for user in users
        ]
    }


# Pydantic models for user creation
class CreateUserRequest(BaseModel):
    """Request body for creating a new user."""

    email: str
    name: Optional[str] = None
    role: str = "user"


class CreateUserResponse(BaseModel):
    """Response body for user creation."""

    email: str
    name: Optional[str]
    role: str
    temporary_password: str
    password_expires_at: str
    message: str


@router.post("/users", response_model=CreateUserResponse)
async def create_user(
    request: CreateUserRequest,
    admin: dict = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new user with a temporary password.

    The user will be created with:
    - A randomly generated secure password (16 characters)
    - Password expiry set to 24 hours from creation
    - must_change_password flag set to True
    - Default role of 'user' (can be overridden)

    The generated password is returned in the response and should be
    securely communicated to the new user by the admin.

    Args:
        request: User creation request with email, optional name, and role
        admin: Current admin user (from JWT)
        db: Database session

    Returns:
        User details including the temporary password

    Raises:
        HTTPException: 400 if user already exists
        HTTPException: 500 if user creation fails
    """
    # Check if user already exists
    result = await db.execute(select(User).where(User.email == request.email))
    existing_user = result.scalar_one_or_none()

    if existing_user:
        raise HTTPException(
            status_code=400, detail=f"User with email {request.email} already exists"
        )

    # Generate temporary password
    temp_password, password_expiry = generate_temporary_password()

    # Hash the password
    password_hash_value = hash_password(temp_password)

    # Create new user
    new_user = User(
        email=request.email,
        name=request.name
        or request.email.split("@")[0],  # Use email prefix as default name
        role=request.role,
        password_hash=password_hash_value,
        password_expires_at=password_expiry,
        must_change_password=True,
    )

    try:
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)

        logger.info(
            f"Admin {admin['sub']} created user {request.email} with temporary password"
        )

        return CreateUserResponse(
            email=new_user.email,
            name=new_user.name,
            role=new_user.role,
            temporary_password=temp_password,
            password_expires_at=password_expiry.isoformat(),
            message="User created successfully. Please securely share the temporary password with the user. The password expires in 24 hours.",
        )

    except Exception as e:
        await db.rollback()
        logger.error(f"Failed to create user {request.email}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create user: {str(e)}")


@router.get("/users/{user_email}/tools")
async def list_user_tools(
    user_email: str,
    admin: dict = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """
    List all tools with access status for a specific user.

    Shows organization-level status and user-level overrides.

    **Enterprise Edition Feature**: Per-user tool permissions are only available
    in the Enterprise Edition. Contact support@kenislabs.com or visit kenislabs.com.com for more information.

    Args:
        user_email: User's email address
        admin: Current admin user (from JWT)
        db: Database session

    Returns:
        List of tools with access status for the user
    """
    raise HTTPException(
        status_code=402,
        detail="Per-user tool permissions are an Enterprise Edition feature. Contact support@kenislabs.com or visit kenislabs.com.com for more information.",
    )


# DEPRECATED: This endpoint is replaced by /users/{user_email}/tools/{tool_id}/toggle in tool_management_endpoints.py
# Commenting out to prevent route shadowing. Remove after migration is complete.
# @router.put("/users/{user_email}/tools/{server_id}/toggle")
# async def toggle_user_tool(
#     user_email: str,
#     server_id: str,
#     enabled: bool,
#     admin: dict = Depends(require_admin),
#     db: AsyncSession = Depends(get_db)
# ):
#     """
#     Set user-level override for tool access.
#
#     This creates an override at the user level. The tool must also be
#     enabled at the organization level for the user to access it.
#
#     Args:
#         user_email: User's email address
#         server_id: MCP server ID
#         enabled: True to enable, False to disable
#         admin: Current admin user (from JWT)
#         db: Database session
#
#     Returns:
#         Success message
#     """
#     # Verify user exists
#     result = await db.execute(select(User).where(User.email == user_email))
#     user = result.scalar_one_or_none()
#     if not user:
#         raise HTTPException(status_code=404, detail=f"User {user_email} not found")
#
#     # Verify server exists in JSON
#     mcp_servers = load_mcp_servers()
#     server_exists = any(s.get("id") == server_id for s in mcp_servers)
#     if not server_exists:
#         raise HTTPException(status_code=404, detail=f"Server {server_id} not found")
#
#     # Check if user access record exists
#     result = await db.execute(
#         select(UserToolAccess).where(
#             UserToolAccess.user_email == user_email,
#             UserToolAccess.mcp_server_id == server_id
#         )
#     )
#     user_access = result.scalar_one_or_none()
#
#     if user_access:
#         # Update existing record
#         user_access.enabled = enabled
#     else:
#         # Create new record
#         user_access = UserToolAccess(
#             user_email=user_email,
#             mcp_server_id=server_id,
#             enabled=enabled
#         )
#         db.add(user_access)
#
#     await db.flush()
#
#     logger.info(
#         f"Admin {admin.get('sub')} set {server_id} to "
#         f"{'enabled' if enabled else 'disabled'} for user {user_email}"
#     )
#
#     return {
#         "message": f"Tool {server_id} {'enabled' if enabled else 'disabled'} for user {user_email}",
#         "user_email": user_email,
#         "server_id": server_id,
#         "enabled": enabled
#     }


@router.delete("/users/{user_email}/tools/{server_id}/override")
async def remove_user_tool_override(
    user_email: str,
    server_id: str,
    admin: dict = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """
    Remove user-level override for tool access.

    Removes the user-level override, reverting to organization-level default.

    **Enterprise Edition Feature**: Per-user tool permissions are only available
    in the Enterprise Edition. Contact support@kenislabs.com or visit kenislabs.com.com for more information.

    Args:
        user_email: User's email address
        server_id: MCP server ID
        admin: Current admin user (from JWT)
        db: Database session

    Returns:
        Success message
    """
    raise HTTPException(
        status_code=402,
        detail="Per-user tool permissions are an Enterprise Edition feature. Contact support@kenislabs.com or visit kenislabs.com.com for more information.",
    )


# ============================================================================
# OAuth Provider Management Endpoints
# ============================================================================


@router.get("/oauth-providers")
async def list_oauth_providers(
    admin: dict = Depends(require_admin), db: AsyncSession = Depends(get_db)
):
    """
    List all OAuth provider credentials.

    Returns all configured OAuth providers for MCP servers.

    Args:
        admin: Current admin user (from JWT)
        db: Database session

    Returns:
        List of OAuth provider configurations (client_secret is masked)
    """
    result = await db.execute(select(OAuthProviderCredentials))
    providers = result.scalars().all()

    return {
        "providers": [
            {
                "id": p.id,
                "mcp_server_id": p.mcp_server_id,
                "provider_name": p.provider_name,
                "client_id": p.client_id,
                "client_secret": "***" if p.client_secret else None,  # Mask secret
                "redirect_uri": p.redirect_uri,
                "auth_url": p.auth_url,
                "token_url": p.token_url,
                "scopes": p.scopes,
                "additional_config": p.additional_config,
                "created_at": p.created_at.isoformat() if p.created_at else None,
                "updated_at": p.updated_at.isoformat() if p.updated_at else None,
            }
            for p in providers
        ]
    }


@router.get("/oauth-providers/{server_id}")
async def get_oauth_provider(
    server_id: str,
    admin: dict = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """
    Get OAuth provider configuration for a specific MCP server.

    Args:
        server_id: MCP server ID
        admin: Current admin user (from JWT)
        db: Database session

    Returns:
        OAuth provider configuration (client_secret is masked)
    """
    result = await db.execute(
        select(OAuthProviderCredentials).where(
            OAuthProviderCredentials.mcp_server_id == server_id
        )
    )
    provider = result.scalar_one_or_none()

    if not provider:
        raise HTTPException(
            status_code=404,
            detail=f"No OAuth provider configured for server {server_id}",
        )

    return {
        "id": provider.id,
        "mcp_server_id": provider.mcp_server_id,
        "provider_name": provider.provider_name,
        "client_id": provider.client_id,
        "client_secret": "***" if provider.client_secret else None,  # Mask secret
        "redirect_uri": provider.redirect_uri,
        "auth_url": provider.auth_url,
        "token_url": provider.token_url,
        "scopes": provider.scopes,
        "additional_config": provider.additional_config,
        "created_at": provider.created_at.isoformat() if provider.created_at else None,
        "updated_at": provider.updated_at.isoformat() if provider.updated_at else None,
    }


@router.post("/oauth-providers")
async def create_oauth_provider(
    mcp_server_id: str,
    provider_name: str,
    client_id: str,
    client_secret: str,
    redirect_uri: str,
    auth_url: str,
    token_url: str,
    scopes: list = None,
    additional_config: dict = None,
    admin: dict = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new OAuth provider configuration.

    Args:
        mcp_server_id: MCP server ID
        provider_name: OAuth provider name (e.g., 'github', 'google')
        client_id: OAuth client ID
        client_secret: OAuth client secret
        redirect_uri: OAuth redirect URI
        auth_url: OAuth authorization endpoint URL
        token_url: OAuth token endpoint URL
        scopes: Required OAuth scopes (optional)
        additional_config: Additional provider-specific settings (optional)
        admin: Current admin user (from JWT)
        db: Database session

    Returns:
        Created OAuth provider configuration
    """
    # Verify server exists in JSON
    mcp_servers = load_mcp_servers()
    server_exists = any(s.get("id") == mcp_server_id for s in mcp_servers)
    if not server_exists:
        raise HTTPException(status_code=404, detail=f"Server {mcp_server_id} not found")

    # Check if provider already exists for this server
    result = await db.execute(
        select(OAuthProviderCredentials).where(
            OAuthProviderCredentials.mcp_server_id == mcp_server_id
        )
    )
    existing = result.scalar_one_or_none()
    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"OAuth provider already configured for server {mcp_server_id}",
        )

    # Encrypt the client_secret before storing
    encrypted_secret = encrypt_string(client_secret)

    # Create new provider
    provider = OAuthProviderCredentials(
        mcp_server_id=mcp_server_id,
        provider_name=provider_name,
        client_id=client_id,
        client_secret=encrypted_secret,  # Stored encrypted
        redirect_uri=redirect_uri,
        auth_url=auth_url,
        token_url=token_url,
        scopes=scopes or [],
        additional_config=additional_config or {},
    )
    db.add(provider)
    await db.flush()

    # Clear any cached provider to ensure fresh credentials are loaded
    registry = get_oauth_provider_registry()
    registry.clear_provider_cache(mcp_server_id)

    logger.info(
        f"Admin {admin.get('sub')} created OAuth provider for server {mcp_server_id}"
    )

    return {
        "message": f"OAuth provider created for server {mcp_server_id}",
        "id": provider.id,
        "mcp_server_id": provider.mcp_server_id,
        "provider_name": provider.provider_name,
    }


@router.put("/oauth-providers/{server_id}")
async def update_oauth_provider(
    server_id: str,
    provider_name: str = None,
    client_id: str = None,
    client_secret: str = None,
    redirect_uri: str = None,
    auth_url: str = None,
    token_url: str = None,
    scopes: list = None,
    additional_config: dict = None,
    admin: dict = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """
    Update OAuth provider configuration for a specific MCP server.

    Only provided fields will be updated. Pass None to keep existing values.

    Args:
        server_id: MCP server ID
        provider_name: OAuth provider name (optional)
        client_id: OAuth client ID (optional)
        client_secret: OAuth client secret (optional)
        redirect_uri: OAuth redirect URI (optional)
        auth_url: OAuth authorization endpoint URL (optional)
        token_url: OAuth token endpoint URL (optional)
        scopes: Required OAuth scopes (optional)
        additional_config: Additional provider-specific settings (optional)
        admin: Current admin user (from JWT)
        db: Database session

    Returns:
        Success message
    """
    result = await db.execute(
        select(OAuthProviderCredentials).where(
            OAuthProviderCredentials.mcp_server_id == server_id
        )
    )
    provider = result.scalar_one_or_none()

    if not provider:
        raise HTTPException(
            status_code=404,
            detail=f"No OAuth provider configured for server {server_id}",
        )

    # Track if OAuth credentials are being changed
    # If client_id or client_secret change, all user tokens need to be invalidated
    credentials_changed = False
    if client_id is not None and client_id != provider.client_id:
        credentials_changed = True
    if client_secret is not None and client_secret != "***":
        credentials_changed = True

    # Update only provided fields
    if provider_name is not None:
        provider.provider_name = provider_name
    if client_id is not None:
        provider.client_id = client_id
    if client_secret is not None:
        # Only update if client_secret is not the masked placeholder
        # Frontend sends "***" when the secret hasn't been changed
        if client_secret != "***":
            # Encrypt the new client_secret before storing
            provider.client_secret = encrypt_string(client_secret)
    if redirect_uri is not None:
        provider.redirect_uri = redirect_uri
    if auth_url is not None:
        provider.auth_url = auth_url
    if token_url is not None:
        provider.token_url = token_url
    if scopes is not None:
        provider.scopes = scopes
    if additional_config is not None:
        provider.additional_config = additional_config

    await db.flush()

    invalidated_count = 0
    if credentials_changed:
        # Invalidate all user credentials for this server
        # User tokens were issued by the old OAuth app, so they won't work with the new one
        result = await db.execute(
            select(UserCredential).where(
                UserCredential.server_id == server_id,
                UserCredential.is_authorized == True
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

        await db.flush()

        logger.warning(
            f"Invalidated {invalidated_count} user credentials for {server_id} "
            f"due to OAuth provider credential change (client_id/client_secret updated)"
        )

    # Clear cached provider to ensure next request uses updated credentials
    registry = get_oauth_provider_registry()
    registry.clear_provider_cache(server_id)

    logger.info(
        f"Admin {admin.get('sub')} updated OAuth provider for server {server_id}"
    )

    return {
        "message": f"OAuth provider updated for server {server_id}",
        "mcp_server_id": server_id,
        "invalidated_users": invalidated_count
    }


@router.delete("/oauth-providers/{server_id}")
async def delete_oauth_provider(
    server_id: str,
    admin: dict = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """
    Delete OAuth provider configuration for a specific MCP server.

    Args:
        server_id: MCP server ID
        admin: Current admin user (from JWT)
        db: Database session

    Returns:
        Success message
    """
    result = await db.execute(
        select(OAuthProviderCredentials).where(
            OAuthProviderCredentials.mcp_server_id == server_id
        )
    )
    provider = result.scalar_one_or_none()

    if not provider:
        raise HTTPException(
            status_code=404,
            detail=f"No OAuth provider configured for server {server_id}",
        )

    await db.delete(provider)
    await db.flush()

    # Clear cached provider after deletion
    registry = get_oauth_provider_registry()
    registry.clear_provider_cache(server_id)

    logger.info(
        f"Admin {admin.get('sub')} deleted OAuth provider for server {server_id}"
    )

    return {
        "message": f"OAuth provider deleted for server {server_id}",
        "mcp_server_id": server_id,
    }

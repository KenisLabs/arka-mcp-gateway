"""Data models for MCP server management

This module contains:
1. Pydantic models for API request/response validation
2. SQLAlchemy models for database persistence
"""
from typing import Optional
from pydantic import BaseModel
from sqlalchemy import Column, String, Boolean, DateTime, Index, JSON
from sqlalchemy.sql import func
from database import Base
import uuid


class MCPServerMetadata(BaseModel):
    """Static metadata about available MCP servers"""
    id: str
    name: str
    description: str
    status: str  # From JSON: "available", "unavailable"
    type: str
    icon: str
    requires_auth: bool = False  # Whether this MCP requires authentication
    auth_type: Optional[str] = None  # e.g., "oauth2", "api_key"
    default_enabled: bool = True  # Whether enabled by default for new users


# ============================================================================
# SQLAlchemy Database Models
# ============================================================================


class UserCredential(Base):
    """SQLAlchemy model for user MCP credentials.

    Stores per-user, per-MCP authorization status and OAuth credentials.
    Composite primary key on (user_id, server_id) ensures one record per user per MCP.

    Attributes:
        user_id (str): User's unique identifier (email)
        server_id (str): MCP server ID (e.g., 'github-mcp', 'jira-mcp')
        is_authorized (bool): Whether user has completed OAuth for this MCP
        is_enabled (bool): Whether user has enabled this MCP in their dashboard
        authorized_at (datetime): Timestamp when OAuth was completed
        access_token (str): OAuth access token (nullable)
        refresh_token (str): OAuth refresh token (nullable)
        expires_at (datetime): Token expiration timestamp (nullable)
        created_at (datetime): Record creation timestamp
        updated_at (datetime): Record last update timestamp

    Example:
        Create a new credential record::

            credential = UserCredential(
                user_id="user@example.com",
                server_id="github-mcp",
                is_authorized=True,
                access_token="ghp_xxx",
                authorized_at=datetime.utcnow()
            )
            session.add(credential)
            await session.commit()
    """

    __tablename__ = "user_credentials"

    # Composite primary key
    user_id = Column(String, primary_key=True, nullable=False, index=True)
    server_id = Column(String, primary_key=True, nullable=False, index=True)

    # Authorization status
    is_authorized = Column(Boolean, default=False, nullable=False)
    is_enabled = Column(Boolean, default=True, nullable=False)
    authorized_at = Column(DateTime(timezone=True), nullable=True)

    # OAuth credentials
    access_token = Column(String, nullable=True)
    refresh_token = Column(String, nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=True)

    # Metadata
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )

    # Indexes for common queries
    __table_args__ = (
        Index('idx_user_authorized', 'user_id', 'is_authorized'),
        Index('idx_user_enabled', 'user_id', 'is_enabled'),
    )

    def __repr__(self):
        """String representation of UserCredential."""
        return (
            f"<UserCredential(user_id='{self.user_id}', "
            f"server_id='{self.server_id}', "
            f"is_authorized={self.is_authorized}, "
            f"is_enabled={self.is_enabled})>"
        )


class RefreshToken(Base):
    """SQLAlchemy model for JWT refresh tokens.

    Stores refresh tokens for JWT-based authentication. Only refresh tokens
    are persisted in the database; access tokens are stateless JWTs.

    Attributes:
        token (str): Unique refresh token string (cryptographically random)
        user_id (str): User's unique identifier from OAuth provider
        user_email (str): User's email address
        created_at (datetime): Token creation timestamp
        last_used (datetime): Last time token was used for refresh
        expires_at (datetime): Token expiration timestamp

    Example:
        Create a new refresh token record::

            refresh_token = RefreshToken(
                token="random_secure_token",
                user_id="user-123",
                user_email="user@example.com",
                expires_at=datetime.now(timezone.utc) + timedelta(days=7)
            )
            session.add(refresh_token)
            await session.commit()
    """

    __tablename__ = "refresh_tokens"

    # Primary key
    token = Column(String, primary_key=True, nullable=False)

    # User information
    user_id = Column(String, nullable=False, index=True)
    user_email = Column(String, nullable=False, index=True)

    # Timestamps
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    last_used = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    expires_at = Column(DateTime(timezone=True), nullable=False, index=True)

    # Indexes for common queries
    __table_args__ = (
        Index('idx_refresh_token_email', 'user_email'),
        Index('idx_refresh_token_user_id', 'user_id'),
        Index('idx_refresh_token_expires', 'expires_at'),
    )

    def __repr__(self):
        """String representation of RefreshToken."""
        return (
            f"<RefreshToken(user_email='{self.user_email}', "
            f"expires_at={self.expires_at})>"
        )


class User(Base):
    """SQLAlchemy model for users with role-based access control.

    Tracks all users (both OAuth and admin) with their roles.
    Admin users have password_hash set, OAuth users have it as NULL.

    Attributes:
        id (str): Unique user identifier (UUID)
        email (str): User's email address (unique)
        name (str): User's display name
        role (str): User's role ('admin' or 'user')
        password_hash (str): Bcrypt password hash (only for admin users)
        password_expires_at (datetime): When password expires (for temporary passwords)
        must_change_password (bool): Whether user must change password on next login
        reset_token (str): Token for password reset (nullable)
        reset_token_expires_at (datetime): When reset token expires (nullable)
        created_at (datetime): Record creation timestamp
        updated_at (datetime): Record last update timestamp

    Example:
        Create an admin user::

            from passlib.hash import bcrypt
            admin = User(
                email="admin@example.com",
                name="Admin",
                role="admin",
                password_hash=bcrypt.hash("admin123")
            )
            session.add(admin)
            await session.commit()

        Create an OAuth user::

            user = User(
                email="user@example.com",
                name="John Doe",
                role="user"
            )
            session.add(user)
            await session.commit()

        Create a user with temporary password::

            from auth.password_utils import hash_password, calculate_password_expiry
            user = User(
                email="newuser@example.com",
                name="New User",
                role="user",
                password_hash=hash_password("TempPass123!"),
                password_expires_at=calculate_password_expiry(24),
                must_change_password=True
            )
            session.add(user)
            await session.commit()
    """

    __tablename__ = "users"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, unique=True, nullable=False, index=True)
    name = Column(String, nullable=True)
    role = Column(String, default="user", nullable=False)
    password_hash = Column(String, nullable=True)

    # Password management fields
    password_expires_at = Column(DateTime(timezone=True), nullable=True)
    must_change_password = Column(Boolean, default=False, nullable=False)
    reset_token = Column(String, nullable=True)
    reset_token_expires_at = Column(DateTime(timezone=True), nullable=True)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )

    # Indexes
    __table_args__ = (
        Index('idx_users_email', 'email'),
        Index('idx_users_role', 'role'),
        Index('idx_users_reset_token', 'reset_token'),
    )

    def __repr__(self):
        """String representation of User."""
        return (
            f"<User(email='{self.email}', "
            f"role='{self.role}')>"
        )


class OrganizationToolAccess(Base):
    """SQLAlchemy model for organization-level tool access control.

    Controls which MCP servers are enabled at the organization level.
    If a server is disabled here, no users can access it.

    Attributes:
        id (str): Unique identifier (UUID)
        mcp_server_id (str): MCP server ID (references mcp_servers.json)
        enabled (bool): Whether this tool is enabled org-wide
        created_at (datetime): Record creation timestamp
        updated_at (datetime): Record last update timestamp

    Example:
        Disable a tool at org level::

            org_access = OrganizationToolAccess(
                mcp_server_id="github-mcp",
                enabled=False
            )
            session.add(org_access)
            await session.commit()
    """

    __tablename__ = "organization_tool_access"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    mcp_server_id = Column(String, unique=True, nullable=False, index=True)
    enabled = Column(Boolean, default=True, nullable=False)
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )

    def __repr__(self):
        """String representation of OrganizationToolAccess."""
        return (
            f"<OrganizationToolAccess(mcp_server_id='{self.mcp_server_id}', "
            f"enabled={self.enabled})>"
        )


class UserToolAccess(Base):
    """SQLAlchemy model for user-level tool access control.

    Allows admin to override tool access for specific users.
    User can only access a tool if both org and user levels are enabled.

    Attributes:
        id (str): Unique identifier (UUID)
        user_email (str): User's email address
        mcp_server_id (str): MCP server ID (references mcp_servers.json)
        enabled (bool): Whether this tool is enabled for the user
        created_at (datetime): Record creation timestamp
        updated_at (datetime): Record last update timestamp

    Example:
        Disable a tool for a specific user::

            user_access = UserToolAccess(
                user_email="user@example.com",
                mcp_server_id="github-mcp",
                enabled=False
            )
            session.add(user_access)
            await session.commit()
    """

    __tablename__ = "user_tool_access"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_email = Column(String, nullable=False, index=True)
    mcp_server_id = Column(String, nullable=False, index=True)
    enabled = Column(Boolean, default=True, nullable=False)
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )

    # Indexes
    __table_args__ = (
        Index('idx_user_tool_access_composite', 'user_email', 'mcp_server_id', unique=True),
        Index('idx_user_tool_access_user', 'user_email'),
        Index('idx_user_tool_access_server', 'mcp_server_id'),
    )

    def __repr__(self):
        """String representation of UserToolAccess."""
        return (
            f"<UserToolAccess(user_email='{self.user_email}', "
            f"mcp_server_id='{self.mcp_server_id}', "
            f"enabled={self.enabled})>"
        )


class OAuthProviderCredentials(Base):
    """SQLAlchemy model for OAuth provider credentials.

    Stores OAuth configuration for MCP servers that require OAuth authentication.
    Allows admins to configure OAuth client IDs and secrets per server.

    Attributes:
        id (str): Unique identifier (UUID)
        mcp_server_id (str): MCP server ID (references mcp_servers.json)
        provider_name (str): OAuth provider name (e.g., 'github', 'google')
        client_id (str): OAuth client ID
        client_secret (str): OAuth client secret (encrypted/hashed)
        redirect_uri (str): OAuth redirect URI
        auth_url (str): OAuth authorization endpoint URL
        token_url (str): OAuth token endpoint URL
        scopes (list): Required OAuth scopes as JSON array
        additional_config (dict): Additional provider-specific settings as JSON
        created_at (datetime): Record creation timestamp
        updated_at (datetime): Record last update timestamp

    Example:
        Create OAuth config for GitHub::

            oauth_config = OAuthProviderCredentials(
                mcp_server_id="github-mcp",
                provider_name="github",
                client_id="Iv1.xxx",
                client_secret="encrypted_secret",
                redirect_uri="http://localhost:8000/auth/callback/github",
                auth_url="https://github.com/login/oauth/authorize",
                token_url="https://github.com/login/oauth/access_token",
                scopes=["repo", "user"],
                additional_config={"allow_signup": False}
            )
            session.add(oauth_config)
            await session.commit()
    """

    __tablename__ = "oauth_provider_credentials"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    mcp_server_id = Column(String, unique=True, nullable=False, index=True)
    provider_name = Column(String, nullable=False)
    client_id = Column(String, nullable=False)
    client_secret = Column(String, nullable=False)  # Should be encrypted at rest
    redirect_uri = Column(String, nullable=False)
    auth_url = Column(String, nullable=False)
    token_url = Column(String, nullable=False)
    scopes = Column(JSON, nullable=True)  # List of OAuth scopes
    additional_config = Column(JSON, nullable=True)  # Provider-specific settings
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )

    # Indexes
    __table_args__ = (
        Index('idx_oauth_credentials_server', 'mcp_server_id', unique=True),
        Index('idx_oauth_credentials_provider', 'provider_name'),
    )

    def __repr__(self):
        """String representation of OAuthProviderCredentials."""
        return (
            f"<OAuthProviderCredentials(mcp_server_id='{self.mcp_server_id}', "
            f"provider_name='{self.provider_name}')>"
        )


class MCPServerTool(Base):
    """SQLAlchemy model for individual tools within MCP servers.

    Defines the specific tools/capabilities available within each MCP server.
    For example, GitHub MCP might have tools like 'create_issue', 'list_repositories', etc.

    Attributes:
        id (str): Unique identifier (UUID)
        mcp_server_id (str): MCP server ID (references mcp_servers.json)
        tool_name (str): Internal tool name (e.g., 'create_issue')
        display_name (str): Human-readable display name (e.g., 'Create Issue')
        description (str): Tool description
        category (str): Tool category for grouping (e.g., 'issues', 'repositories')
        is_dangerous (bool): Whether this tool performs destructive operations
        created_at (datetime): Record creation timestamp
        updated_at (datetime): Record last update timestamp

    Example:
        Add a tool to GitHub MCP::

            tool = MCPServerTool(
                mcp_server_id="github-mcp",
                tool_name="create_issue",
                display_name="Create Issue",
                description="Create a new GitHub issue",
                category="issues",
                is_dangerous=False
            )
            session.add(tool)
            await session.commit()
    """

    __tablename__ = "mcp_server_tools"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    mcp_server_id = Column(String, nullable=False, index=True)
    tool_name = Column(String, nullable=False)
    display_name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    category = Column(String, nullable=True, index=True)
    is_dangerous = Column(Boolean, default=False, nullable=False)
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )

    # Indexes
    __table_args__ = (
        Index('idx_mcp_server_tools_server', 'mcp_server_id'),
        Index('idx_mcp_server_tools_unique', 'mcp_server_id', 'tool_name', unique=True),
        Index('idx_mcp_server_tools_category', 'category'),
    )

    def __repr__(self):
        """String representation of MCPServerTool."""
        return (
            f"<MCPServerTool(mcp_server_id='{self.mcp_server_id}', "
            f"tool_name='{self.tool_name}', "
            f"display_name='{self.display_name}')>"
        )


class OrganizationToolPermission(Base):
    """SQLAlchemy model for organization-level tool permissions.

    Controls which specific tools within MCP servers are enabled at the organization level.
    If a tool is disabled here, no users can access it.

    Attributes:
        id (str): Unique identifier (UUID)
        tool_id (str): Foreign key to mcp_server_tools.id
        enabled (bool): Whether this tool is enabled org-wide
        created_at (datetime): Record creation timestamp
        updated_at (datetime): Record last update timestamp

    Example:
        Disable a dangerous tool at org level::

            permission = OrganizationToolPermission(
                tool_id="tool-uuid-123",
                enabled=False
            )
            session.add(permission)
            await session.commit()
    """

    __tablename__ = "organization_tool_permissions"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    tool_id = Column(String, nullable=False, unique=True, index=True)
    enabled = Column(Boolean, default=True, nullable=False)
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )

    # Indexes
    __table_args__ = (
        Index('idx_org_tool_permissions_tool', 'tool_id', unique=True),
    )

    def __repr__(self):
        """String representation of OrganizationToolPermission."""
        return (
            f"<OrganizationToolPermission(tool_id='{self.tool_id}', "
            f"enabled={self.enabled})>"
        )


class UserToolPermission(Base):
    """SQLAlchemy model for user-level tool permissions.

    Allows admins to override tool access for specific users.
    User can only access a tool if both org and user levels are enabled.

    Attributes:
        id (str): Unique identifier (UUID)
        user_email (str): User's email address
        tool_id (str): Foreign key to mcp_server_tools.id
        enabled (bool): Whether this tool is enabled for the user
        created_at (datetime): Record creation timestamp
        updated_at (datetime): Record last update timestamp

    Example:
        Give a user access to a dangerous tool::

            permission = UserToolPermission(
                user_email="trusted@example.com",
                tool_id="tool-uuid-123",
                enabled=True
            )
            session.add(permission)
            await session.commit()
    """

    __tablename__ = "user_tool_permissions"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_email = Column(String, nullable=False, index=True)
    tool_id = Column(String, nullable=False, index=True)
    enabled = Column(Boolean, default=True, nullable=False)
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )

    # Indexes
    __table_args__ = (
        Index('idx_user_tool_permissions_composite', 'user_email', 'tool_id', unique=True),
        Index('idx_user_tool_permissions_user', 'user_email'),
        Index('idx_user_tool_permissions_tool', 'tool_id'),
    )

    def __repr__(self):
        """String representation of UserToolPermission."""
        return (
            f"<UserToolPermission(user_email='{self.user_email}', "
            f"tool_id='{self.tool_id}', "
            f"enabled={self.enabled})>"
        )


class MCPServerConfiguration(Base):
    """SQLAlchemy model for configured MCP servers.

    Stores MCP servers that have been added/configured by admins.
    This differentiates between available servers (in catalog) and
    actually configured servers that users can access.

    Attributes:
        id (str): Unique identifier (UUID)
        server_id (str): Server ID from catalog (e.g., 'github-mcp')
        display_name (str): Custom display name set by admin
        description (str): Server description
        category (str): Server category (e.g., 'Development', 'Project Management')
        icon (str): Icon identifier
        is_enabled (bool): Whether this server is currently enabled
        configuration (dict): Additional server configuration as JSON
        added_by (str): Email of admin who added this server
        created_at (datetime): When server was added
        updated_at (datetime): Last configuration update

    Example:
        Add a new MCP server configuration::

            config = MCPServerConfiguration(
                server_id="github-mcp",
                display_name="GitHub MCP",
                description="Access GitHub repositories",
                category="Development",
                icon="github",
                is_enabled=True,
                added_by="admin@example.com"
            )
            session.add(config)
            await session.commit()
    """

    __tablename__ = "mcp_server_configurations"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    server_id = Column(String, unique=True, nullable=False, index=True)
    display_name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    category = Column(String, nullable=True, index=True)
    icon = Column(String, nullable=True)
    is_enabled = Column(Boolean, default=True, nullable=False)
    configuration = Column(JSON, nullable=True)  # Additional server-specific config
    added_by = Column(String, nullable=False, index=True)
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )

    # Indexes
    __table_args__ = (
        Index('idx_mcp_server_config_server_id', 'server_id', unique=True),
        Index('idx_mcp_server_config_enabled', 'is_enabled'),
        Index('idx_mcp_server_config_category', 'category'),
    )

    def __repr__(self):
        """String representation of MCPServerConfiguration."""
        return (
            f"<MCPServerConfiguration(server_id='{self.server_id}', "
            f"display_name='{self.display_name}', "
            f"is_enabled={self.is_enabled})>"
        )


class AuditLog(Base):
    """SQLAlchemy model for audit logging.

    Tracks all admin actions for security and compliance.

    Attributes:
        id (str): Unique identifier (UUID)
        actor_email (str): Email of user who performed the action
        actor_role (str): Role of user who performed the action
        action (str): Action performed (e.g., 'toggle_org_tool')
        resource_type (str): Type of resource affected (e.g., 'mcp_server')
        resource_id (str): ID of affected resource
        details (dict): Additional context as JSON
        created_at (datetime): When action was performed

    Example:
        Log an admin action::

            audit = AuditLog(
                actor_email="admin@example.com",
                actor_role="admin",
                action="toggle_org_tool",
                resource_type="mcp_server",
                resource_id="github-mcp",
                details={"enabled": False}
            )
            session.add(audit)
            await session.commit()
    """

    __tablename__ = "audit_log"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    actor_email = Column(String, nullable=False, index=True)
    actor_role = Column(String, nullable=False)
    action = Column(String, nullable=False, index=True)
    resource_type = Column(String, nullable=True)
    resource_id = Column(String, nullable=True)
    details = Column(JSON, nullable=True)
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True
    )

    # Indexes
    __table_args__ = (
        Index('idx_audit_log_actor', 'actor_email'),
        Index('idx_audit_log_action', 'action'),
        Index('idx_audit_log_created', 'created_at'),
    )

    def __repr__(self):
        """String representation of AuditLog."""
        return (
            f"<AuditLog(actor_email='{self.actor_email}', "
            f"action='{self.action}', "
            f"resource_type='{self.resource_type}')>"
        )


class MCPAccessToken(Base):
    """SQLAlchemy model for MCP API access tokens.

    Stores JWT tokens for MCP client authentication (VS Code, Claude Desktop, etc.).
    Tokens are long-lived and can be revoked by users.

    Attributes:
        id (UUID): Primary key
        user_id (int): Foreign key to users table
        token_name (str): Human-readable name for the token (e.g., "VS Code", "Claude Desktop")
        jti (str): JWT ID for token revocation
        token_prefix (str): First 12 characters of token for display
        last_used_at (datetime): Last time the token was used
        expires_at (datetime): Token expiration time (nullable for long-lived tokens)
        revoked (bool): Whether the token has been revoked
        revoked_at (datetime): When the token was revoked
        created_at (datetime): Token creation timestamp
        updated_at (datetime): Token last update timestamp
    """
    __tablename__ = "mcp_access_tokens"

    id = Column(
        String,
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        nullable=False
    )
    user_id = Column(
        String,
        nullable=False,
        index=True
    )
    token_name = Column(
        String(255),
        nullable=False
    )
    jti = Column(
        String(255),
        unique=True,
        nullable=False,
        index=True
    )
    token_prefix = Column(
        String(20),
        nullable=False
    )
    last_used_at = Column(
        DateTime,
        nullable=True
    )
    expires_at = Column(
        DateTime,
        nullable=True
    )
    revoked = Column(
        Boolean,
        default=False,
        nullable=False,
        index=True
    )
    revoked_at = Column(
        DateTime,
        nullable=True
    )
    created_at = Column(
        DateTime,
        server_default=func.now(),
        nullable=False
    )
    updated_at = Column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )

    # Indexes
    __table_args__ = (
        Index('idx_mcp_tokens_user_id', 'user_id'),
        Index('idx_mcp_tokens_jti', 'jti'),
        Index('idx_mcp_tokens_revoked', 'revoked'),
    )

    def __repr__(self):
        """String representation of MCPAccessToken."""
        return (
            f"<MCPAccessToken(user_id='{self.user_id}', "
            f"token_name='{self.token_name}', "
            f"revoked={self.revoked})>"
        )

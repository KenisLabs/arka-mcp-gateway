"""
User MCP Preferences - Tracks per-user MCP authorization and enablement.

For each user, tracks:
- Which MCPs they have authorized (OAuth completed)
- Which MCPs are enabled/disabled in their dashboard
- Stored credentials (persisted in PostgreSQL)
"""
from typing import Dict, List, Optional
from datetime import datetime, timezone
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db_session
from .registry import get_registry
from .models import UserCredential
from .crypto_utils import encrypt_string, decrypt_string
import logging

logger = logging.getLogger(__name__)


class MCPCredentials(BaseModel):
    """Credentials for an authorized MCP"""
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    expires_at: Optional[datetime] = None
    # Additional provider-specific data can be stored here


class UserMCPPreference(BaseModel):
    """User's preference for a specific MCP"""
    server_id: str
    is_authorized: bool = False
    is_enabled: bool = True
    authorized_at: Optional[datetime] = None
    credentials: Optional[MCPCredentials] = None


class UserPreferences(BaseModel):
    """All MCP preferences for a user"""
    user_id: str
    mcp_preferences: Dict[str, UserMCPPreference] = {}


class UserPreferencesStore:
    """
    PostgreSQL-backed store for user MCP preferences.

    Stores user preferences and OAuth credentials persistently in PostgreSQL.
    All methods are async to support database operations.
    """

    def __init__(self):
        """Initialize the preferences store"""
        self._registry = get_registry()

    async def _ensure_user_credentials_exist(
        self,
        session: AsyncSession,
        user_id: str
    ) -> None:
        """
        Ensure database records exist for all available MCPs for this user.

        Args:
            session: Database session
            user_id: User's unique identifier (email)
        """
        # Get all available MCPs from registry
        available_servers = self._registry.get_available_servers()

        for server in available_servers:
            # Check if credential already exists
            stmt = select(UserCredential).where(
                UserCredential.user_id == user_id,
                UserCredential.server_id == server.id
            )
            result = await session.execute(stmt)
            existing = result.scalar_one_or_none()

            if not existing:
                # Create new credential record with defaults
                credential = UserCredential(
                    user_id=user_id,
                    server_id=server.id,
                    is_authorized=False,
                    is_enabled=server.default_enabled,
                    authorized_at=None,
                    access_token=None,
                    refresh_token=None,
                    expires_at=None
                )
                session.add(credential)

        await session.commit()

    def _db_credential_to_pydantic(
        self,
        db_credential: UserCredential
    ) -> UserMCPPreference:
        """
        Convert SQLAlchemy UserCredential to Pydantic UserMCPPreference.

        Automatically decrypts access_token and refresh_token.

        Args:
            db_credential: Database model instance

        Returns:
            Pydantic model instance
        """
        credentials = None
        if db_credential.access_token:
            try:
                # Decrypt tokens when reading from database
                decrypted_access_token = decrypt_string(db_credential.access_token)
                decrypted_refresh_token = (
                    decrypt_string(db_credential.refresh_token)
                    if db_credential.refresh_token
                    else None
                )

                credentials = MCPCredentials(
                    access_token=decrypted_access_token,
                    refresh_token=decrypted_refresh_token,
                    expires_at=db_credential.expires_at
                )
            except Exception as e:
                logger.error(
                    f"Failed to decrypt credentials for user {db_credential.user_id}, "
                    f"server {db_credential.server_id}: {e}"
                )
                # Return None credentials if decryption fails
                credentials = None

        return UserMCPPreference(
            server_id=db_credential.server_id,
            is_authorized=db_credential.is_authorized,
            is_enabled=db_credential.is_enabled,
            authorized_at=db_credential.authorized_at,
            credentials=credentials
        )

    async def get_user_preferences(self, user_id: str) -> UserPreferences:
        """
        Get all MCP preferences for a user from database.

        Args:
            user_id: User's unique identifier

        Returns:
            UserPreferences (creates if doesn't exist)
        """
        async with get_db_session() as session:
            # Ensure user has credential records for all MCPs
            await self._ensure_user_credentials_exist(session, user_id)

            # Fetch all credentials for this user
            stmt = select(UserCredential).where(UserCredential.user_id == user_id)
            result = await session.execute(stmt)
            db_credentials = result.scalars().all()

            # Convert to Pydantic models
            mcp_preferences = {}
            for db_cred in db_credentials:
                mcp_preferences[db_cred.server_id] = self._db_credential_to_pydantic(db_cred)

            return UserPreferences(user_id=user_id, mcp_preferences=mcp_preferences)

    async def get_mcp_preference(
        self,
        user_id: str,
        server_id: str
    ) -> Optional[UserMCPPreference]:
        """
        Get user's preference for a specific MCP from database.

        Args:
            user_id: User's unique identifier
            server_id: MCP server ID

        Returns:
            UserMCPPreference if found, None otherwise
        """
        async with get_db_session() as session:
            stmt = select(UserCredential).where(
                UserCredential.user_id == user_id,
                UserCredential.server_id == server_id
            )
            result = await session.execute(stmt)
            db_credential = result.scalar_one_or_none()

            if not db_credential:
                # Create default preference if doesn't exist
                server = self._registry.get_server_by_id(server_id)
                if not server:
                    return None

                db_credential = UserCredential(
                    user_id=user_id,
                    server_id=server_id,
                    is_authorized=False,
                    is_enabled=server.default_enabled
                )
                session.add(db_credential)
                await session.commit()

            return self._db_credential_to_pydantic(db_credential)

    async def toggle_mcp_enabled(
        self,
        user_id: str,
        server_id: str,
        enabled: bool
    ) -> UserMCPPreference:
        """
        Toggle MCP enabled/disabled for a user in database.

        Args:
            user_id: User's unique identifier
            server_id: MCP server ID
            enabled: Whether to enable or disable

        Returns:
            Updated UserMCPPreference

        Raises:
            ValueError: If server_id is invalid
        """
        async with get_db_session() as session:
            stmt = select(UserCredential).where(
                UserCredential.user_id == user_id,
                UserCredential.server_id == server_id
            )
            result = await session.execute(stmt)
            db_credential = result.scalar_one_or_none()

            if not db_credential:
                raise ValueError(f"Invalid server_id: {server_id}")

            db_credential.is_enabled = enabled
            await session.commit()

            return self._db_credential_to_pydantic(db_credential)

    async def authorize_mcp(
        self,
        user_id: str,
        server_id: str,
        credentials: MCPCredentials
    ) -> UserMCPPreference:
        """
        Mark an MCP as authorized for a user and store credentials in database.

        Args:
            user_id: User's unique identifier
            server_id: MCP server ID
            credentials: OAuth/API credentials

        Returns:
            Updated UserMCPPreference

        Raises:
            ValueError: If server_id is invalid
        """
        async with get_db_session() as session:
            stmt = select(UserCredential).where(
                UserCredential.user_id == user_id,
                UserCredential.server_id == server_id
            )
            result = await session.execute(stmt)
            db_credential = result.scalar_one_or_none()

            if not db_credential:
                # Create new credential if doesn't exist
                db_credential = UserCredential(
                    user_id=user_id,
                    server_id=server_id,
                    is_enabled=True
                )
                session.add(db_credential)

            # Update authorization and credentials (encrypt tokens before storing)
            db_credential.is_authorized = True
            db_credential.authorized_at = datetime.now(timezone.utc)
            db_credential.access_token = (
                encrypt_string(credentials.access_token)
                if credentials.access_token
                else None
            )
            db_credential.refresh_token = (
                encrypt_string(credentials.refresh_token)
                if credentials.refresh_token
                else None
            )
            db_credential.expires_at = credentials.expires_at

            await session.commit()
            logger.info(f"Authorized {server_id} for user {user_id}, encrypted token saved to database")

            return self._db_credential_to_pydantic(db_credential)

    async def revoke_mcp_authorization(
        self,
        user_id: str,
        server_id: str
    ) -> UserMCPPreference:
        """
        Revoke MCP authorization for a user in database.

        Args:
            user_id: User's unique identifier
            server_id: MCP server ID

        Returns:
            Updated UserMCPPreference

        Raises:
            ValueError: If server_id is invalid
        """
        async with get_db_session() as session:
            stmt = select(UserCredential).where(
                UserCredential.user_id == user_id,
                UserCredential.server_id == server_id
            )
            result = await session.execute(stmt)
            db_credential = result.scalar_one_or_none()

            if not db_credential:
                raise ValueError(f"Invalid server_id: {server_id}")

            # Clear authorization and credentials
            db_credential.is_authorized = False
            db_credential.authorized_at = None
            db_credential.access_token = None
            db_credential.refresh_token = None
            db_credential.expires_at = None

            await session.commit()
            logger.info(f"Revoked {server_id} for user {user_id}, credentials removed from database")

            return self._db_credential_to_pydantic(db_credential)

    async def get_authorized_mcps(self, user_id: str) -> List[UserMCPPreference]:
        """
        Get list of all authorized MCPs for a user from database.

        Args:
            user_id: User's unique identifier

        Returns:
            List of UserMCPPreference for authorized MCPs
        """
        async with get_db_session() as session:
            stmt = select(UserCredential).where(
                UserCredential.user_id == user_id,
                UserCredential.is_authorized == True  # noqa: E712
            )
            result = await session.execute(stmt)
            db_credentials = result.scalars().all()

            return [self._db_credential_to_pydantic(db_cred) for db_cred in db_credentials]

    async def get_enabled_mcps(self, user_id: str) -> List[UserMCPPreference]:
        """
        Get list of all enabled MCPs for a user from database.

        Args:
            user_id: User's unique identifier

        Returns:
            List of UserMCPPreference for enabled MCPs
        """
        async with get_db_session() as session:
            stmt = select(UserCredential).where(
                UserCredential.user_id == user_id,
                UserCredential.is_enabled == True  # noqa: E712
            )
            result = await session.execute(stmt)
            db_credentials = result.scalars().all()

            return [self._db_credential_to_pydantic(db_cred) for db_cred in db_credentials]


# Global preferences store instance
_preferences_store: Optional[UserPreferencesStore] = None


def get_preferences_store() -> UserPreferencesStore:
    """
    Get the global preferences store instance.
    Creates it if it doesn't exist (singleton pattern).

    Returns:
        The global UserPreferencesStore instance
    """
    global _preferences_store
    if _preferences_store is None:
        _preferences_store = UserPreferencesStore()
    return _preferences_store

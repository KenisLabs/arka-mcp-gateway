"""JWT Token Management Utilities.

This module provides utilities for creating, verifying, and managing JWT tokens
for authentication. It supports both access tokens (short-lived JWTs) and
refresh tokens (long-lived, stored in database).

Example:
    Generate tokens after successful OAuth::

        from auth.jwt_utils import create_access_token, create_refresh_token

        user_data = {"sub": "user@example.com", "name": "John Doe"}
        access_token = create_access_token(user_data)
        refresh_token = await create_refresh_token("user@example.com")

    Verify and decode access token::

        from auth.jwt_utils import verify_access_token

        payload = verify_access_token(token)
        if payload:
            user_email = payload["sub"]
"""
import jwt
import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict
from sqlalchemy import select, delete
from config import settings
from database import get_db_session
import logging

logger = logging.getLogger(__name__)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token.

    Generates a signed JWT token containing user data with an expiration time.
    The token is signed using the configured algorithm and secret key.

    Args:
        data (dict): User data to encode in the token. Should include:
            - sub (str): Subject (user identifier, typically email)
            - name (str): User's display name
            - provider (str): OAuth provider name
        expires_delta (Optional[timedelta]): Custom expiration time.
            If None, uses JWT_ACCESS_TOKEN_EXPIRE_MINUTES from config.

    Returns:
        str: Encoded JWT access token

    Example:
        >>> user_data = {
        ...     "sub": "user@example.com",
        ...     "name": "John Doe",
        ...     "provider": "azure"
        ... }
        >>> token = create_access_token(user_data)
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.jwt_access_token_expire_minutes
        )

    to_encode.update({
        "exp": expire,
        "iat": datetime.now(timezone.utc),
        "type": "access"
    })

    encoded_jwt = jwt.encode(
        to_encode,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm
    )

    return encoded_jwt


def verify_access_token(token: str) -> Optional[Dict]:
    """Verify and decode a JWT access token.

    Validates the token signature, expiration, and type.
    Returns the decoded payload if valid, None otherwise.

    Args:
        token (str): JWT access token to verify

    Returns:
        Optional[Dict]: Decoded token payload if valid, None otherwise.
            Payload contains:
            - sub (str): User identifier (email)
            - name (str): User's display name
            - provider (str): OAuth provider
            - exp (int): Expiration timestamp
            - iat (int): Issued at timestamp
            - type (str): Token type ("access")

    Example:
        >>> payload = verify_access_token(token)
        >>> if payload:
        ...     print(f"User: {payload['sub']}")
        ... else:
        ...     print("Invalid token")
    """
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm]
        )

        # Verify token type
        if payload.get("type") != "access":
            logger.warning("Token is not an access token")
            return None

        return payload
    except jwt.ExpiredSignatureError:
        logger.warning("Access token has expired")
        return None
    except jwt.InvalidTokenError as e:
        logger.warning(f"Invalid access token: {e}")
        return None
    except Exception as e:
        logger.error(f"Error verifying access token: {e}")
        return None


async def create_refresh_token(user_id: str, user_email: str) -> str:
    """Create a refresh token and store it in the database.

    Generates a cryptographically secure random token and stores it
    in the database with the user information and expiration time.

    Args:
        user_id (str): User's unique identifier from OAuth provider
        user_email (str): User's email address

    Returns:
        str: Random refresh token string

    Example:
        >>> token = await create_refresh_token("user-123", "user@example.com")
    """
    # Import here to avoid circular dependency
    from gateway.models import RefreshToken

    # Generate cryptographically secure random token
    refresh_token = secrets.token_urlsafe(32)

    # Calculate expiration
    expires_at = datetime.now(timezone.utc) + timedelta(
        days=settings.jwt_refresh_token_expire_days
    )

    # Store in database
    async with get_db_session() as session:
        db_token = RefreshToken(
            token=refresh_token,
            user_id=user_id,
            user_email=user_email,
            expires_at=expires_at
        )
        session.add(db_token)
        await session.commit()

    logger.info(f"Created refresh token for user {user_email}")
    return refresh_token


async def verify_refresh_token(token: str) -> Optional[Dict]:
    """Verify a refresh token and return user data.

    Checks if the token exists in the database and is not expired.
    Updates the last_used timestamp if valid.

    Args:
        token (str): Refresh token to verify

    Returns:
        Optional[Dict]: User data if token is valid, None otherwise.
            Contains:
            - user_id (str): User's unique identifier
            - user_email (str): User's email address

    Example:
        >>> user_data = await verify_refresh_token(refresh_token)
        >>> if user_data:
        ...     print(f"Valid token for: {user_data['user_email']}")
    """
    # Import here to avoid circular dependency
    from gateway.models import RefreshToken

    try:
        async with get_db_session() as session:
            stmt = select(RefreshToken).where(RefreshToken.token == token)
            result = await session.execute(stmt)
            db_token = result.scalar_one_or_none()

            if not db_token:
                logger.warning("Refresh token not found in database")
                return None

            # Check if token is expired
            if datetime.now(timezone.utc) > db_token.expires_at:
                logger.info(f"Refresh token expired for {db_token.user_email}")
                # Delete expired token
                await session.delete(db_token)
                await session.commit()
                return None

            # Update last used timestamp
            db_token.last_used = datetime.now(timezone.utc)
            await session.commit()

            return {
                "user_id": db_token.user_id,
                "user_email": db_token.user_email
            }
    except Exception as e:
        logger.error(f"Error verifying refresh token: {e}")
        return None


async def revoke_refresh_token(token: str) -> bool:
    """Revoke a refresh token by deleting it from the database.

    Args:
        token (str): Refresh token to revoke

    Returns:
        bool: True if token was revoked, False otherwise

    Example:
        >>> success = await revoke_refresh_token(refresh_token)
        >>> if success:
        ...     print("Token revoked successfully")
    """
    # Import here to avoid circular dependency
    from gateway.models import RefreshToken

    try:
        async with get_db_session() as session:
            stmt = delete(RefreshToken).where(RefreshToken.token == token)
            result = await session.execute(stmt)
            await session.commit()

            if result.rowcount > 0:
                logger.info("Refresh token revoked successfully")
                return True
            else:
                logger.warning("Refresh token not found for revocation")
                return False
    except Exception as e:
        logger.error(f"Error revoking refresh token: {e}")
        return False


async def revoke_all_user_tokens(user_email: str) -> int:
    """Revoke all refresh tokens for a specific user.

    Useful for logout from all devices or security incident response.

    Args:
        user_email (str): User's email address

    Returns:
        int: Number of tokens revoked

    Example:
        >>> count = await revoke_all_user_tokens("user@example.com")
        >>> print(f"Revoked {count} tokens")
    """
    # Import here to avoid circular dependency
    from gateway.models import RefreshToken

    try:
        async with get_db_session() as session:
            stmt = delete(RefreshToken).where(RefreshToken.user_email == user_email)
            result = await session.execute(stmt)
            await session.commit()

            logger.info(f"Revoked {result.rowcount} refresh tokens for {user_email}")
            return result.rowcount
    except Exception as e:
        logger.error(f"Error revoking user tokens: {e}")
        return 0


async def cleanup_expired_tokens():
    """Remove all expired refresh tokens from the database.

    Should be called periodically (e.g., daily) to prevent database bloat.
    Can be implemented as a background task or cron job.

    Returns:
        int: Number of expired tokens deleted

    Example:
        >>> # Call periodically in a background task
        >>> count = await cleanup_expired_tokens()
        >>> print(f"Cleaned up {count} expired tokens")
    """
    # Import here to avoid circular dependency
    from gateway.models import RefreshToken

    try:
        async with get_db_session() as session:
            now = datetime.now(timezone.utc)
            stmt = delete(RefreshToken).where(RefreshToken.expires_at < now)
            result = await session.execute(stmt)
            await session.commit()

            logger.info(f"Cleaned up {result.rowcount} expired refresh tokens")
            return result.rowcount
    except Exception as e:
        logger.error(f"Error cleaning up expired tokens: {e}")
        return 0

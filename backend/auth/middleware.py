"""JWT Authentication Middleware and Dependencies.

This module provides FastAPI middleware and dependency injection for JWT authentication.
It verifies JWT tokens from HTTP-only cookies and attaches user information to requests.

Example:
    Protect an endpoint with JWT authentication::

        from fastapi import Depends
        from auth.middleware import get_current_user

        @app.get("/protected")
        async def protected_route(user: dict = Depends(get_current_user)):
            return {"message": f"Hello {user['email']}"}

    Optional authentication (for endpoints that work with/without auth)::

        from auth.middleware import get_optional_user

        @app.get("/public-or-private")
        async def flexible_route(user: Optional[dict] = Depends(get_optional_user)):
            if user:
                return {"message": f"Welcome back {user['email']}"}
            else:
                return {"message": "Welcome guest"}
"""
from fastapi import HTTPException, status, Cookie, Depends
from typing import Optional, Dict
from auth.jwt_utils import verify_access_token
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from gateway.models import User
from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)


async def get_current_user(
    access_token: Optional[str] = Cookie(None),
    db: AsyncSession = Depends(get_db)
) -> Dict:
    """Dependency to get the current authenticated user from JWT token.

    Extracts the JWT access token from HTTP-only cookie, verifies it,
    checks password expiry for admin users, and returns the user data.
    Raises 401 error if token is missing or invalid.
    Raises 403 error if password has expired or must be changed.

    Args:
        access_token (Optional[str]): JWT access token from cookie
        db (AsyncSession): Database session

    Returns:
        Dict: User data from token payload containing:
            - sub (str): User email
            - name (str): User's display name
            - provider (str): OAuth provider

    Raises:
        HTTPException: 401 if not authenticated or token is invalid
        HTTPException: 403 if password expired or must be changed

    Example:
        >>> @app.get("/me")
        >>> async def get_me(user: dict = Depends(get_current_user)):
        >>>     return {"email": user["sub"], "name": user["name"]}
    """
    if not access_token:
        logger.warning("No access token provided in cookie")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated. Please log in.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    payload = verify_access_token(access_token)
    if not payload:
        logger.warning("Invalid or expired access token")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token. Please log in again.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Check password expiry for admin provider users only
    if payload.get("provider") == "admin":
        user_email = payload.get("sub")
        result = await db.execute(
            select(User).where(User.email == user_email)
        )
        db_user = result.scalar_one_or_none()

        if db_user:
            # Check if user must change password
            if db_user.must_change_password:
                logger.warning(f"User {user_email} must change password")
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="PASSWORD_CHANGE_REQUIRED",
                )

            # Check if password has expired
            if db_user.password_expires_at:
                now = datetime.now(timezone.utc)
                if db_user.password_expires_at <= now:
                    logger.warning(f"User {user_email} password has expired")
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="PASSWORD_EXPIRED",
                    )

    return payload


async def get_optional_user(access_token: Optional[str] = Cookie(None)) -> Optional[Dict]:
    """Dependency to optionally get the current user from JWT token.

    Similar to get_current_user but returns None instead of raising an error
    if no token is provided or if the token is invalid. Useful for endpoints
    that work differently for authenticated vs. anonymous users.

    Args:
        access_token (Optional[str]): JWT access token from cookie

    Returns:
        Optional[Dict]: User data if authenticated, None otherwise

    Example:
        >>> @app.get("/content")
        >>> async def get_content(user: Optional[dict] = Depends(get_optional_user)):
        >>>     if user:
        >>>         return {"content": "Premium content", "user": user["sub"]}
        >>>     else:
        >>>         return {"content": "Free content"}
    """
    if not access_token:
        return None

    payload = verify_access_token(access_token)
    return payload if payload else None


async def get_current_user_skip_password_check(
    access_token: Optional[str] = Cookie(None)
) -> Dict:
    """Dependency to get current user WITHOUT checking password expiry.

    Used for endpoints that need authentication but should work even if
    the password has expired (e.g., change-password endpoint).

    Args:
        access_token (Optional[str]): JWT access token from cookie

    Returns:
        Dict: User data from token payload

    Raises:
        HTTPException: 401 if not authenticated or token is invalid

    Example:
        >>> @app.post("/change-password")
        >>> async def change_password(user: dict = Depends(get_current_user_skip_password_check)):
        >>>     # User can change password even if expired
        >>>     pass
    """
    if not access_token:
        logger.warning("No access token provided in cookie")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated. Please log in.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    payload = verify_access_token(access_token)
    if not payload:
        logger.warning("Invalid or expired access token")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token. Please log in again.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return payload


async def get_user_email(user: Dict = Depends(get_current_user)) -> str:
    """Convenience dependency to extract just the user email.

    Args:
        user (Dict): User data from get_current_user dependency

    Returns:
        str: User's email address

    Example:
        >>> @app.get("/profile")
        >>> async def get_profile(email: str = Depends(get_user_email)):
        >>>     return {"email": email}
    """
    return user["sub"]

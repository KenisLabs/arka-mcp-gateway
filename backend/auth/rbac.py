"""
Role-Based Access Control (RBAC) middleware.

Provides decorators and dependencies for role-based authorization.
"""
from fastapi import Depends, HTTPException
from .middleware import get_current_user
import logging

logger = logging.getLogger(__name__)


def requires_role(required_role: str):
    """
    Dependency factory for role-based authorization.

    Creates a FastAPI dependency that checks if the current user
    has the required role.

    Args:
        required_role: The role required to access the endpoint (e.g., 'admin', 'user')

    Returns:
        A FastAPI dependency function

    Example:
        @router.get("/admin/users", dependencies=[Depends(requires_role("admin"))])
        async def list_users():
            return {"users": [...]}

    Raises:
        HTTPException 403: If user doesn't have the required role
    """
    async def check_role(user: dict = Depends(get_current_user)) -> dict:
        user_role = user.get("role", "user")

        if user_role != required_role:
            logger.warning(
                f"Access denied for {user.get('sub')}: "
                f"required role '{required_role}', has role '{user_role}'"
            )
            raise HTTPException(
                status_code=403,
                detail=f"Insufficient permissions. Required role: {required_role}"
            )

        return user

    return check_role


async def require_admin(user: dict = Depends(get_current_user)) -> dict:
    """
    FastAPI dependency that requires admin role.

    Convenience dependency for endpoints that require admin access.

    Args:
        user: Current user from JWT token

    Returns:
        User dict if user is admin

    Example:
        @router.get("/admin/dashboard")
        async def admin_dashboard(admin: dict = Depends(require_admin)):
            return {"message": f"Welcome {admin['sub']}"}

    Raises:
        HTTPException 403: If user is not an admin
    """
    user_role = user.get("role", "user")

    if user_role != "admin":
        logger.warning(
            f"Admin access denied for {user.get('sub')}: has role '{user_role}'"
        )
        raise HTTPException(
            status_code=403,
            detail="Admin access required"
        )

    return user


async def require_user(user: dict = Depends(get_current_user)) -> dict:
    """
    FastAPI dependency that requires any authenticated user.

    This is essentially the same as get_current_user, but makes
    the intent clearer in the code.

    Args:
        user: Current user from JWT token

    Returns:
        User dict

    Example:
        @router.get("/dashboard")
        async def dashboard(user: dict = Depends(require_user)):
            return {"message": f"Welcome {user['sub']}"}

    Raises:
        HTTPException 401: If user is not authenticated
    """
    return user

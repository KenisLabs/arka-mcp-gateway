"""
Admin authentication endpoints.

Provides email/password authentication for admin users.
"""
from fastapi import APIRouter, HTTPException, Response, Depends, Request, Cookie
from pydantic import BaseModel, EmailStr
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from gateway.models import User
from .jwt_utils import create_access_token, create_refresh_token
from .middleware import get_current_user, get_current_user_skip_password_check
from .password_utils import (
    hash_password,
    verify_password,
    validate_password_strength,
    generate_reset_token,
    calculate_reset_token_expiry,
    is_reset_token_valid,
)
from .rate_limiter import login_rate_limiter
from datetime import datetime, timezone
from config import settings
from typing import Optional
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/auth", tags=["auth"])


class AdminLoginRequest(BaseModel):
    """Request body for admin login"""
    email: EmailStr
    password: str


class AdminLoginResponse(BaseModel):
    """Response body for admin login"""
    message: str
    user: dict


@router.post("/admin/login", response_model=AdminLoginResponse)
async def admin_login(
    credentials: AdminLoginRequest,
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db)
):
    """
    Email/password login for all users (admin and regular).

    Issues JWT tokens (access + refresh) on success.
    Tokens are set as HTTP-only cookies.

    Rate limited to 5 attempts per minute per IP address.

    Args:
        credentials: Email and password
        request: FastAPI request object (for rate limiting)
        response: FastAPI response object
        db: Database session

    Returns:
        AdminLoginResponse with user info

    Raises:
        HTTPException 401: If credentials are invalid
        HTTPException 429: If rate limit exceeded
    """
    # Check rate limit
    login_rate_limiter.check_rate_limit(request)

    # Find user by email
    result = await db.execute(
        select(User).where(User.email == credentials.email)
    )
    user = result.scalar_one_or_none()

    # Check if user exists
    if not user:
        logger.warning(f"Failed login attempt for {credentials.email}: User not found")
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # Verify password
    if not user.password_hash:
        logger.warning(f"Failed login attempt for {credentials.email}: No password set")
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # Verify password using utility function
    if not verify_password(credentials.password, user.password_hash):
        logger.warning(f"Failed login attempt for {credentials.email}: Invalid password")
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # Create JWT tokens
    user_data = {
        "sub": user.email,
        "name": user.name or user.email,
        "role": user.role,  # Use actual user role
        "provider": "admin"
    }

    access_token = create_access_token(user_data)
    refresh_token = await create_refresh_token(user.id, user.email)

    # Set tokens as HTTP-only cookies
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=getattr(settings, 'cookie_secure', False),
        samesite="lax",
        max_age=settings.jwt_access_token_expire_minutes * 60
    )

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=getattr(settings, 'cookie_secure', False),
        samesite="lax",
        max_age=settings.jwt_refresh_token_expire_days * 24 * 60 * 60
    )

    logger.info(f"Login successful: {user.email} (role: {user.role})")

    return AdminLoginResponse(
        message="Login successful",
        user={
            "email": user.email,
            "name": user.name or user.email,
            "role": user.role
        }
    )


@router.get("/me")
async def get_current_user_info(
    user: dict = Depends(get_current_user)
):
    """
    Get current authenticated user information.

    Requires authentication (access token in cookie).

    Args:
        user: Current authenticated user from JWT

    Returns:
        User information dict

    Raises:
        HTTPException 401: If not authenticated
        HTTPException 403: If password expired or must be changed
    """
    return {
        "email": user["sub"],
        "name": user.get("name", user["sub"]),
        "role": user.get("role", "user"),
        "provider": user.get("provider", "admin")
    }


@router.post("/admin/bootstrap")
async def bootstrap_admin(db: AsyncSession = Depends(get_db)):
    """
    Bootstrap initial admin user.

    Creates admin user with credentials:
    - Email: admin@example.com
    - Password: admin

    Only works if no admin users exist.

    Args:
        db: Database session

    Returns:
        Success message with credentials

    Raises:
        HTTPException 400: If admin user already exists
    """
    # Check if any admin exists
    result = await db.execute(
        select(User).where(User.role == "admin")
    )
    existing_admin = result.scalar_one_or_none()

    if existing_admin:
        raise HTTPException(
            status_code=400,
            detail="Admin user already exists"
        )

    # Create admin user
    password_hash = hash_password("admin")
    admin = User(
        email="admin@example.com",
        name="Admin",
        role="admin",
        password_hash=password_hash
    )

    db.add(admin)
    await db.flush()  # Flush to get the ID, commit happens automatically with get_db

    logger.info("Admin user bootstrapped: admin@example.com")

    return {
        "message": "Admin user created successfully",
        "email": "admin@example.com",
        "password": "admin",
        "warning": "Please change the password after first login"
    }


class ChangePasswordRequest(BaseModel):
    """Request body for changing password"""
    old_password: str
    new_password: str


class ChangePasswordResponse(BaseModel):
    """Response body for password change"""
    message: str


@router.post("/change-password", response_model=ChangePasswordResponse)
async def change_password(
    request: ChangePasswordRequest,
    user: dict = Depends(get_current_user_skip_password_check),
    db: AsyncSession = Depends(get_db)
):
    """
    Change user's password.

    Requires authentication. User must provide their current password
    and a new password that meets strength requirements.

    Args:
        request: Old and new passwords
        user: Current authenticated user
        db: Database session

    Returns:
        ChangePasswordResponse with success message

    Raises:
        HTTPException 401: If old password is incorrect
        HTTPException 400: If new password doesn't meet requirements
        HTTPException 404: If user not found
    """
    # Get user from database
    result = await db.execute(
        select(User).where(User.email == user["sub"])
    )
    db_user = result.scalar_one_or_none()

    if not db_user:
        logger.error(f"User {user['sub']} not found in database")
        raise HTTPException(status_code=404, detail="User not found")

    # Verify old password
    if not db_user.password_hash:
        logger.error(f"User {user['sub']} has no password set")
        raise HTTPException(status_code=400, detail="Cannot change password for OAuth-only users")

    if not verify_password(request.old_password, db_user.password_hash):
        logger.warning(f"Failed password change attempt for {user['sub']}: Incorrect old password")
        raise HTTPException(status_code=401, detail="Current password is incorrect")

    # Validate new password strength
    is_valid, error_message = validate_password_strength(request.new_password)
    if not is_valid:
        logger.warning(f"Password change failed for {user['sub']}: {error_message}")
        raise HTTPException(status_code=400, detail=error_message)

    # Hash new password
    new_password_hash = hash_password(request.new_password)

    # Update user password and clear expiry/force-change flags
    db_user.password_hash = new_password_hash
    db_user.password_expires_at = None
    db_user.must_change_password = False

    await db.commit()

    logger.info(f"Password changed successfully for user {user['sub']}")

    return ChangePasswordResponse(message="Password changed successfully")


class ForgotPasswordRequest(BaseModel):
    """Request body for forgot password"""
    email: str


class ForgotPasswordResponse(BaseModel):
    """Response body for forgot password"""
    message: str


@router.post("/forgot-password", response_model=ForgotPasswordResponse)
async def forgot_password(
    request: ForgotPasswordRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Generate password reset token for user.

    Public endpoint (no authentication required).
    Always returns success message to prevent email enumeration.

    Args:
        request: User email
        db: Database session

    Returns:
        ForgotPasswordResponse with success message

    Note:
        In production, this should send an email with the reset link.
        For MVP, the token is logged (should be removed in production).
    """
    # Find user by email
    result = await db.execute(
        select(User).where(User.email == request.email)
    )
    user = result.scalar_one_or_none()

    # Always return success to prevent email enumeration
    if not user:
        logger.info(f"Password reset requested for non-existent email: {request.email}")
        return ForgotPasswordResponse(
            message="If an account exists with this email, you will receive password reset instructions."
        )

    if not user.password_hash:
        logger.info(f"Password reset requested for OAuth-only user: {request.email}")
        return ForgotPasswordResponse(
            message="If an account exists with this email, you will receive password reset instructions."
        )

    # Generate reset token
    reset_token = generate_reset_token()
    reset_token_expiry = calculate_reset_token_expiry()

    # Store token and expiry
    user.reset_token = reset_token
    user.reset_token_expires_at = reset_token_expiry

    await db.commit()

    logger.info(f"Password reset token generated for user {user.email}")

    # TODO: In production, send email with reset link

    return ForgotPasswordResponse(
        message="If an account exists with this email, you will receive password reset instructions."
    )


class ResetPasswordRequest(BaseModel):
    """Request body for reset password"""
    token: str
    new_password: str


class ResetPasswordResponse(BaseModel):
    """Response body for reset password"""
    message: str


@router.post("/reset-password", response_model=ResetPasswordResponse)
async def reset_password(
    request: ResetPasswordRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Reset user password using reset token.

    Public endpoint (no authentication required).
    Uses the token from forgot-password to reset the password.

    Args:
        request: Reset token and new password
        db: Database session

    Returns:
        ResetPasswordResponse with success message

    Raises:
        HTTPException 400: If token is invalid, expired, or password is weak
        HTTPException 404: If user not found
    """
    # Find user by reset token
    result = await db.execute(
        select(User).where(User.reset_token == request.token)
    )
    user = result.scalar_one_or_none()

    if not user:
        logger.warning("Password reset attempted with invalid token")
        raise HTTPException(status_code=400, detail="Invalid or expired reset token")

    # Validate reset token
    is_valid, error_message = is_reset_token_valid(
        request.token,
        user.reset_token,
        user.reset_token_expires_at
    )

    if not is_valid:
        logger.warning(f"Password reset failed for {user.email}: {error_message}")
        raise HTTPException(status_code=400, detail=error_message)

    # Validate new password strength
    is_valid, error_message = validate_password_strength(request.new_password)
    if not is_valid:
        logger.warning(f"Password reset failed for {user.email}: {error_message}")
        raise HTTPException(status_code=400, detail=error_message)

    # Hash new password
    new_password_hash = hash_password(request.new_password)

    # Update user password and clear all password-related flags
    user.password_hash = new_password_hash
    user.password_expires_at = None
    user.must_change_password = False
    user.reset_token = None
    user.reset_token_expires_at = None

    await db.commit()

    logger.info(f"Password reset successfully for user {user.email}")

    return ResetPasswordResponse(message="Password reset successfully. You can now log in with your new password.")


@router.post("/refresh")
async def refresh_tokens(
    response: Response,
    refresh_token: Optional[str] = Cookie(None),
    db: AsyncSession = Depends(get_db)
):
    """
    Refresh access token using refresh token.

    Validates the refresh token and issues a new access token.
    The refresh token remains valid and is not rotated.

    Args:
        response: FastAPI response object
        refresh_token: Refresh token from cookie
        db: Database session

    Returns:
        Success message

    Raises:
        HTTPException 401: If refresh token is missing or invalid
    """
    from .jwt_utils import verify_refresh_token

    if not refresh_token:
        raise HTTPException(
            status_code=401,
            detail="Refresh token not provided"
        )

    # Verify refresh token
    user_data = await verify_refresh_token(refresh_token)
    if not user_data:
        # Delete invalid refresh token cookie
        response.delete_cookie(key="refresh_token")
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired refresh token. Please log in again."
        )

    # Get user from database to include latest role/name
    result = await db.execute(
        select(User).where(User.email == user_data["user_email"])
    )
    user = result.scalar_one_or_none()

    if not user:
        response.delete_cookie(key="refresh_token")
        raise HTTPException(
            status_code=401,
            detail="User not found. Please log in again."
        )

    # Create new access token with current user data
    access_token_data = {
        "sub": user.email,
        "name": user.name or user.email,
        "role": user.role,
        "provider": user_data.get("provider", "admin")
    }
    new_access_token = create_access_token(access_token_data)

    # Set new access token cookie
    response.set_cookie(
        key="access_token",
        value=new_access_token,
        httponly=True,
        secure=getattr(settings, 'cookie_secure', False),
        samesite="lax",
        max_age=settings.jwt_access_token_expire_minutes * 60
    )

    logger.info(f"Token refreshed successfully for user {user.email}")

    return {"message": "Token refreshed successfully"}


@router.post("/logout")
async def logout(
    response: Response,
    refresh_token: Optional[str] = Cookie(None)
):
    """
    Logout user and revoke their refresh token.

    Removes the refresh token from the database and deletes both cookies.
    Safe to call even if the user is not authenticated.

    Args:
        response: FastAPI response object
        refresh_token: Refresh token from cookie

    Returns:
        Success message
    """
    from .jwt_utils import revoke_refresh_token

    if refresh_token:
        await revoke_refresh_token(refresh_token)
        logger.info("User logged out, refresh token revoked")

    # Delete both cookies
    response.delete_cookie(
        key="access_token",
        httponly=True,
        secure=getattr(settings, 'cookie_secure', False),
        samesite="lax"
    )
    response.delete_cookie(
        key="refresh_token",
        httponly=True,
        secure=getattr(settings, 'cookie_secure', False),
        samesite="lax"
    )

    return {"message": "Logged out successfully"}

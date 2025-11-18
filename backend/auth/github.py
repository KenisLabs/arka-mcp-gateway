"""GitHub OAuth 2.0 authentication endpoints for end-user login.

This module implements the OAuth 2.0 authorization code flow for GitHub.
It provides endpoints for end-user authentication to the Arka MCP Gateway dashboard.

NOTE: This is DIFFERENT from the GitHub MCP server OAuth provider in gateway/auth_providers/github.py.
      - This module: End-user authentication to dashboard
      - gateway/auth_providers/github.py: MCP server authorization

The OAuth flow works as follows:
    1. User navigates to `/auth/login/github`
    2. User is redirected to GitHub OAuth authorization page
    3. User authorizes the application
    4. GitHub redirects back to `/auth/callback/github` with authorization code
    5. Backend exchanges code for access token
    6. User information is fetched from GitHub API
    7. Session is created and user is redirected to frontend dashboard

Security Features:
    - CSRF protection via state parameter
    - HTTPOnly cookies for tokens
    - Automatic user provisioning
    - Role-based access control

Example:
    To initiate GitHub login from your frontend::

        window.location.href = 'http://localhost:8000/auth/login/github';

    To check if user is authenticated::

        const response = await fetch('http://localhost:8000/auth/me', {
            credentials: 'include'
        });
        const user = await response.json();

Setup:
    Before using this module, you must configure a GitHub OAuth App:
        1. Go to GitHub Settings → Developer settings → OAuth Apps → New OAuth App
        2. Application name: "Arka MCP Gateway - User Auth"
        3. Homepage URL: http://localhost:5173 (or your frontend URL)
        4. Authorization callback URL: http://localhost:8000/auth/callback/github
        5. Copy Client ID and generate Client Secret
        6. Set environment variables:
           - ARKA_GITHUB_USER_OAUTH_CLIENT_ID
           - ARKA_GITHUB_USER_OAUTH_CLIENT_SECRET

Environment Variables:
    ARKA_GITHUB_USER_OAUTH_CLIENT_ID: GitHub OAuth App Client ID
    ARKA_GITHUB_USER_OAUTH_CLIENT_SECRET: GitHub OAuth App Client Secret
"""
from fastapi import APIRouter, HTTPException, Response, Cookie, Depends, status
from fastapi.responses import RedirectResponse
from authlib.integrations.httpx_client import OAuth2Client
from typing import Optional
import httpx
import secrets
import time
from sqlalchemy import select
from config import settings
from database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from gateway.models import User
from auth.jwt_utils import create_access_token, create_refresh_token

# Initialize router
router = APIRouter(prefix="/auth", tags=["authentication"])

# In-memory state store for CSRF protection
# TODO: Migrate to Redis for production (horizontal scaling)
_oauth_states = {}


def get_github_user_oauth_client() -> OAuth2Client:
    """Create and configure a GitHub OAuth2 client for user authentication.

    Returns:
        OAuth2Client: Configured OAuth client for GitHub

    Raises:
        ValueError: If GitHub OAuth credentials are not configured

    Example:
        >>> client = get_github_user_oauth_client()
        >>> url, state = client.create_authorization_url(...)
    """
    client_id = settings.get("github_user_oauth_client_id")
    client_secret = settings.get("github_user_oauth_client_secret")

    if not client_id or not client_secret:
        raise ValueError(
            "GitHub User OAuth not configured. "
            "Set ARKA_GITHUB_USER_OAUTH_CLIENT_ID and ARKA_GITHUB_USER_OAUTH_CLIENT_SECRET"
        )

    return OAuth2Client(
        client_id=client_id,
        client_secret=client_secret,
        token_endpoint="https://github.com/login/oauth/access_token",
    )


@router.get("/login/github")
async def login_github():
    """Initiate GitHub OAuth 2.0 login flow for end-user authentication.

    Redirects the user to the GitHub authorization endpoint where they can
    authorize the application. After successful authorization, GitHub will
    redirect back to the callback endpoint.

    Security:
        - Generates cryptographically secure state parameter for CSRF protection
        - State is stored in-memory (migrate to Redis for production)
        - Requests user:email scope for profile information

    Returns:
        RedirectResponse: Redirect to GitHub authorization page

    Raises:
        HTTPException: 500 error if GitHub OAuth is not configured

    Example:
        >>> # From frontend JavaScript
        >>> window.location.href = '/auth/login/github';

    Note:
        Requires ARKA_GITHUB_USER_OAUTH_CLIENT_ID and 
        ARKA_GITHUB_USER_OAUTH_CLIENT_SECRET to be set in environment.
    """
    try:
        client = get_github_user_oauth_client()
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))

    # GitHub OAuth authorization endpoint
    authorization_endpoint = "https://github.com/login/oauth/authorize"

    # Build authorization URL with CSRF protection
    redirect_uri = f"{settings.backend_url}/auth/callback/github"
    scope = "read:user user:email"  # Request user profile and email

    # Generate cryptographically secure state parameter for CSRF protection
    state = secrets.token_urlsafe(32)

    authorization_url, _ = client.create_authorization_url(
        authorization_endpoint,
        redirect_uri=redirect_uri,
        scope=scope,
        state=state
    )

    # Store state for validation in callback (in-memory for now)
    # TODO: Store in Redis with TTL for production
    _oauth_states[state] = {
        "created_at": time.time()
    }

    return RedirectResponse(authorization_url)


@router.get("/callback/github")
async def callback_github(
    code: Optional[str] = None,
    state: Optional[str] = None,
    error: Optional[str] = None,
    error_description: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """Handle GitHub OAuth callback and create user session.

    This endpoint receives the authorization code from GitHub, exchanges it
    for an access token, fetches user information from GitHub API, creates
    or updates the user record, and establishes an authenticated session.

    Security Features:
        - CSRF protection via state parameter validation
        - Automatic user provisioning with 'user' role
        - HTTPOnly cookies for tokens (XSS protection)
        - SameSite=Lax cookie policy (CSRF protection)
        - Secure cookie flag in production (HTTPS only)

    Args:
        code (Optional[str]): Authorization code from GitHub
        state (Optional[str]): State parameter for CSRF protection
        error (Optional[str]): Error code if authorization failed
        error_description (Optional[str]): Human-readable error description
        db (AsyncSession): Database session (injected)

    Returns:
        RedirectResponse: Redirect to frontend dashboard with session cookies

    Raises:
        HTTPException: 
            - 400 if authorization error or missing code
            - 403 if state validation fails (CSRF attack)
            - 500 if token exchange or API calls fail

    Example:
        This endpoint is called automatically by GitHub after login.
        You don't need to call it manually.

    Flow:
        1. Validate state parameter (CSRF protection)
        2. Exchange authorization code for access token
        3. Fetch user profile from GitHub API
        4. Create or update user in database
        5. Generate JWT access and refresh tokens
        6. Set HTTPOnly cookies
        7. Redirect to dashboard
    """
    # Check for errors from GitHub
    if error:
        error_msg = f"GitHub OAuth error: {error}"
        if error_description:
            error_msg += f" - {error_description}"
        raise HTTPException(status_code=400, detail=error_msg)

    if not code:
        raise HTTPException(status_code=400, detail="No authorization code provided")

    # Validate state parameter (CSRF protection)
    if not state or state not in _oauth_states:
        raise HTTPException(
            status_code=403,
            detail="Invalid or expired state parameter. Possible CSRF attack."
        )

    # Remove used state (one-time use)
    _oauth_states.pop(state, None)

    try:
        # Exchange code for access token
        client = get_github_user_oauth_client()
        redirect_uri = f"{settings.backend_url}/auth/callback/github"

        token = client.fetch_token(
            url="https://github.com/login/oauth/access_token",
            code=code,
            grant_type="authorization_code",
            redirect_uri=redirect_uri
        )

        # Get user info from GitHub API
        async with httpx.AsyncClient() as http_client:
            # Fetch user profile
            headers = {
                "Authorization": f"Bearer {token['access_token']}",
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28"
            }

            # Get basic user info
            user_response = await http_client.get(
                "https://api.github.com/user",
                headers=headers
            )
            user_response.raise_for_status()
            user_info = user_response.json()

            # Get user emails (primary email)
            emails_response = await http_client.get(
                "https://api.github.com/user/emails",
                headers=headers
            )
            emails_response.raise_for_status()
            emails = emails_response.json()

            # Find primary verified email
            primary_email = None
            for email_obj in emails:
                if email_obj.get("primary") and email_obj.get("verified"):
                    primary_email = email_obj.get("email")
                    break

            # Fallback to any verified email
            if not primary_email:
                for email_obj in emails:
                    if email_obj.get("verified"):
                        primary_email = email_obj.get("email")
                        break

            if not primary_email:
                raise HTTPException(
                    status_code=400,
                    detail="No verified email found for GitHub account. Please verify your email on GitHub."
                )

        # Extract user information
        github_id = user_info.get("id")
        github_login = user_info.get("login")
        user_name = user_info.get("name") or github_login
        user_email = primary_email

        # Create or update User record in database
        result = await db.execute(
            select(User).where(User.email == user_email)
        )
        existing_user = result.scalar_one_or_none()

        if not existing_user:
            # Create new user with 'user' role (OAuth users are regular users, not admins)
            new_user = User(
                email=user_email,
                name=user_name,
                role="user",
                password_hash=None  # OAuth users don't have passwords
            )
            db.add(new_user)
            await db.flush()
            user_id = new_user.id
            user_role = "user"
        else:
            # Update user name if it changed
            if existing_user.name != user_name:
                existing_user.name = user_name
                await db.flush()

            user_id = existing_user.id
            user_role = existing_user.role

        # Create JWT access token with user information
        access_token_data = {
            "sub": user_email,  # Subject (user identifier)
            "name": user_name,
            "role": user_role,
            "provider": "github",
            "github_login": github_login
        }
        access_token = create_access_token(access_token_data)

        # Create refresh token and store in database
        refresh_token = await create_refresh_token(user_id, user_email)

        # Redirect to frontend with tokens in HTTPOnly cookies
        response = RedirectResponse(url=f"{settings.frontend_url}/dashboard")

        # Set access token cookie (HTTPOnly, short-lived)
        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,  # XSS protection
            secure=getattr(settings, 'cookie_secure', False),
            samesite="lax",  # CSRF protection
            max_age=settings.jwt_access_token_expire_minutes * 60
        )

        # Set refresh token cookie (HTTPOnly, long-lived)
        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,  # XSS protection
            secure=getattr(settings, 'cookie_secure', False),
            samesite="lax",  # CSRF protection
            max_age=settings.jwt_refresh_token_expire_days * 24 * 60 * 60
        )

        return response

    except httpx.HTTPStatusError as e:
        print(f"GitHub API error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch user information from GitHub: {e.response.status_code}"
        )
    except Exception as e:
        print(f"Error during GitHub OAuth callback: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Authentication failed: {str(e)}"
        )

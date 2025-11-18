"""
JWT token utilities for MCP access tokens.

Provides functions to create and verify long-lived JWT tokens for MCP client authentication.
"""
from datetime import datetime, timedelta
from typing import Optional
import jwt
import secrets
from config import settings


def create_mcp_access_token(
    user_id: str,
    email: str,
    name: str,
    token_name: str,
    expires_delta: Optional[timedelta] = None
) -> tuple[str, str]:
    """
    Create a long-lived JWT token for MCP access.

    Args:
        user_id: User's unique identifier
        email: User's email address
        name: User's display name
        token_name: Human-readable token name (e.g., "VS Code", "Claude Desktop")
        expires_delta: Optional expiration time delta (default: 10 years)

    Returns:
        tuple: (jwt_token, jti)
            - jwt_token: The encoded JWT token string
            - jti: Unique JWT ID for revocation tracking

    Example:
        >>> token, jti = create_mcp_access_token(
        ...     user_id="123",
        ...     email="user@example.com",
        ...     name="John Doe",
        ...     token_name="VS Code"
        ... )
        >>> print(f"Token: {token[:20]}...")
        >>> print(f"JTI: {jti}")
    """
    # Generate unique JWT ID for revocation tracking
    jti = secrets.token_urlsafe(32)

    # Build JWT payload
    payload = {
        "sub": str(user_id),  # Subject (user ID)
        "email": email,
        "name": name,
        "jti": jti,  # JWT ID for revocation
        "token_name": token_name,
        "type": "mcp_access",  # Token type identifier
        "iat": datetime.utcnow(),  # Issued at
    }

    # Set expiration
    if expires_delta:
        payload["exp"] = datetime.utcnow() + expires_delta
    else:
        # Default: 10 years for long-lived tokens
        payload["exp"] = datetime.utcnow() + timedelta(days=3650)

    # Encode JWT
    token = jwt.encode(
        payload,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm
    )

    return token, jti


def verify_mcp_access_token(token: str) -> dict:
    """
    Verify and decode a JWT MCP access token.

    Args:
        token: The JWT token string to verify

    Returns:
        dict: Decoded token payload containing:
            - sub: User ID
            - email: User email
            - name: User name
            - jti: JWT ID
            - token_name: Token name
            - type: Token type ("mcp_access")
            - iat: Issued at timestamp
            - exp: Expiration timestamp

    Raises:
        jwt.ExpiredSignatureError: If the token has expired
        jwt.InvalidTokenError: If the token is invalid or has wrong type

    Example:
        >>> try:
        ...     payload = verify_mcp_access_token(token)
        ...     print(f"User ID: {payload['sub']}")
        ...     print(f"Email: {payload['email']}")
        ... except jwt.ExpiredSignatureError:
        ...     print("Token expired")
        ... except jwt.InvalidTokenError as e:
        ...     print(f"Invalid token: {e}")
    """
    try:
        # Decode and verify JWT
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm]
        )

        # Verify token type
        if payload.get("type") != "mcp_access":
            raise jwt.InvalidTokenError("Invalid token type")

        return payload

    except jwt.ExpiredSignatureError:
        raise jwt.ExpiredSignatureError("Token has expired")
    except jwt.InvalidTokenError as e:
        raise jwt.InvalidTokenError(f"Invalid token: {str(e)}")

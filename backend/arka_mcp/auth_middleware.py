"""
MCP Authentication Middleware.

Provides JWT authentication for incoming MCP requests from clients like VS Code and Claude Desktop.
"""
from typing import Optional
from fastapi import Request
from auth.mcp_jwt import verify_mcp_access_token
from database import get_db_session
from gateway.models import MCPAccessToken, User
from sqlalchemy import select
import jwt
import logging

logger = logging.getLogger(__name__)


async def authenticate_mcp_request(request: Request) -> Optional[dict]:
    """
    Authenticate MCP request using JWT Bearer token.

    Extracts JWT from Authorization header, verifies it, checks if it's revoked,
    and returns user information.

    Args:
        request: FastAPI request object

    Returns:
        dict: User information if authenticated, None otherwise
            Contains:
            - user_id (str): User's database ID
            - email (str): User's email
            - name (str): User's display name
            - token_name (str): Name of the MCP token being used

    Example:
        >>> user_info = await authenticate_mcp_request(request)
        >>> if user_info:
        ...     print(f"Authenticated as: {user_info['email']}")
    """
    # Extract Authorization header
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        logger.warning(f"MCP request missing Authorization header. Path: {request.url.path}")
        return None

    # Parse Bearer token
    parts = auth_header.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        logger.warning(f"Invalid Authorization header format. Got: {auth_header[:20]}...")
        return None

    token = parts[1]
    logger.debug(f"Authenticating MCP token: {token[:20]}...")

    try:
        # Verify JWT token
        payload = verify_mcp_access_token(token)
        logger.debug(f"Token verified successfully. Payload keys: {payload.keys()}")

        # Extract token info
        jti = payload.get("jti")
        user_id = payload.get("sub")
        email = payload.get("email")
        name = payload.get("name")
        token_name = payload.get("token_name")

        if not all([jti, user_id, email]):
            logger.warning(f"JWT payload missing required fields. jti={jti}, user_id={user_id}, email={email}")
            return None

        logger.debug(f"Looking up token in database: jti={jti[:8]}...")

        # Check if token is revoked in database
        async with get_db_session() as session:
            result = await session.execute(
                select(MCPAccessToken)
                .where(MCPAccessToken.jti == jti)
                .where(MCPAccessToken.revoked == False)
            )
            token_record = result.scalar_one_or_none()

            if not token_record:
                logger.warning(f"MCP token {jti[:8]}... is revoked or not found in database")
                return None

            logger.debug(f"Token found in database: {token_record.id}")

            # Update last_used_at timestamp
            from datetime import datetime
            token_record.last_used_at = datetime.utcnow()
            await session.commit()

        logger.info(f"MCP request authenticated: {email} using token '{token_name}'")

        return {
            "user_id": user_id,
            "email": email,
            "name": name,
            "token_name": token_name,
            "jti": jti
        }

    except jwt.ExpiredSignatureError:
        logger.warning("MCP token has expired")
        return None
    except jwt.InvalidTokenError as e:
        logger.warning(f"Invalid MCP token: {e}")
        return None
    except Exception as e:
        logger.error(f"Error authenticating MCP request: {e}", exc_info=True)
        return None

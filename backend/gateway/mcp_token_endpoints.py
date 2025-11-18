"""
MCP Access Token Management API Endpoints.

Provides endpoints for users to generate, list, and revoke MCP access tokens
for authenticating MCP clients (VS Code, Claude Desktop, etc.).
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from datetime import datetime
from auth.mcp_jwt import create_mcp_access_token
from auth.middleware import get_current_user
from database import get_db
from gateway.models import MCPAccessToken, User
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/mcp-tokens", tags=["mcp-tokens"])


# ============================================================================
# Request/Response Models
# ============================================================================

class CreateTokenRequest(BaseModel):
    """Request body for creating a new MCP access token"""
    # No fields needed - token is created automatically for the user
    pass


class TokenResponse(BaseModel):
    """Response model for token information (without the actual JWT)"""
    id: str
    token_name: str
    token_prefix: str
    last_used_at: str | None
    created_at: str
    expires_at: str | None = None


class CreateTokenResponse(BaseModel):
    """Response model when creating a new token (includes full JWT)"""
    token: str  # Full JWT token - only shown once!
    token_id: str
    token_name: str
    token_prefix: str
    created_at: str
    message: str


# ============================================================================
# Endpoints
# ============================================================================

@router.post("/", response_model=CreateTokenResponse)
async def create_token(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Generate a new MCP access token for the current user.

    **Important**: Each user can only have ONE active token at a time.
    If a token already exists, it will be automatically revoked and a new one created.

    The JWT token is returned **only once** and cannot be retrieved again.
    Users should save it securely.

    Args:
        current_user: Authenticated user (from JWT payload)
        db: Database session

    Returns:
        CreateTokenResponse with the full JWT token

    Example:
        POST /api/mcp-tokens/

        Response:
        {
            "token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
            "token_id": "550e8400-e29b-41d4-a716-446655440000",
            "token_name": "MCP Access Token",
            "token_prefix": "eyJ0eXAiOiJK...",
            "created_at": "2025-01-15T10:30:00Z",
            "message": "Save this token securely. It will not be shown again."
        }
    """
    try:
        # Extract user info from JWT payload
        user_email = current_user["sub"]
        user_name = current_user.get("name", user_email)

        # Get user_id from database
        result = await db.execute(
            select(User).where(User.email == user_email)
        )
        user = result.scalar_one_or_none()
        if not user:
            raise HTTPException(404, "User not found")

        # Revoke any existing active tokens for this user
        existing_tokens_result = await db.execute(
            select(MCPAccessToken)
            .where(MCPAccessToken.user_id == str(user.id))
            .where(MCPAccessToken.revoked == False)
        )
        existing_tokens = existing_tokens_result.scalars().all()

        if existing_tokens:
            from datetime import datetime
            for token in existing_tokens:
                token.revoked = True
                token.revoked_at = datetime.utcnow()
            logger.info(f"Revoked {len(existing_tokens)} existing token(s) for user {user_email}")

        # Create JWT token with default name
        token_name = "MCP Access Token"
        jwt_token, jti = create_mcp_access_token(
            user_id=str(user.id),
            email=user_email,
            name=user_name,
            token_name=token_name
        )

        # Store token metadata in database
        token_record = MCPAccessToken(
            user_id=str(user.id),
            token_name=token_name,
            jti=jti,
            token_prefix=jwt_token[:12] + "...",  # First 12 chars for display
            expires_at=None  # Long-lived token (10 years)
        )

        db.add(token_record)
        await db.commit()
        await db.refresh(token_record)

        logger.info(f"Created new MCP access token for user {user_email}: {token_record.id}")

        return CreateTokenResponse(
            token=jwt_token,  # ONLY RETURNED ONCE!
            token_id=token_record.id,
            token_name=token_record.token_name,
            token_prefix=token_record.token_prefix,
            created_at=token_record.created_at.isoformat(),
            message="Save this token securely. It will not be shown again."
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create MCP token for user {current_user.get('sub', 'unknown')}: {e}")
        raise HTTPException(500, f"Failed to create token: {str(e)}")


@router.get("/", response_model=list[TokenResponse])
async def list_tokens(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    List all active MCP tokens for the current user.

    Only shows non-revoked tokens. The full JWT token is never returned
    after creation - only the prefix is shown for identification.

    Args:
        current_user: Authenticated user (from JWT payload)
        db: Database session

    Returns:
        List of TokenResponse objects

    Example:
        GET /api/mcp/tokens

        Response:
        [
            {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "token_name": "VS Code",
                "token_prefix": "eyJ0eXAiOiJK...",
                "last_used_at": "2025-01-15T12:45:00Z",
                "created_at": "2025-01-15T10:30:00Z"
            },
            {
                "id": "660f9511-f3ac-52e5-b827-557766551111",
                "token_name": "Claude Desktop",
                "token_prefix": "eyJ0eXBhOiJK...",
                "last_used_at": null,
                "created_at": "2025-01-14T09:00:00Z"
            }
        ]
    """
    try:
        # Extract user info from JWT payload
        user_email = current_user["sub"]

        # Get user_id from database
        result = await db.execute(
            select(User).where(User.email == user_email)
        )
        user = result.scalar_one_or_none()
        if not user:
            raise HTTPException(404, "User not found")

        # Query non-revoked tokens for this user
        result = await db.execute(
            select(MCPAccessToken)
            .where(MCPAccessToken.user_id == str(user.id))
            .where(MCPAccessToken.revoked == False)
            .order_by(MCPAccessToken.created_at.desc())
        )
        tokens = result.scalars().all()

        return [
            TokenResponse(
                id=token.id,
                token_name=token.token_name,
                token_prefix=token.token_prefix,
                last_used_at=token.last_used_at.isoformat() if token.last_used_at else None,
                created_at=token.created_at.isoformat(),
                expires_at=token.expires_at.isoformat() if token.expires_at else None
            )
            for token in tokens
        ]

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to list MCP tokens for user {user_email}: {e}")
        raise HTTPException(500, f"Failed to list tokens: {str(e)}")


@router.delete("/{token_id}")
async def revoke_token(
    token_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Revoke an MCP access token.

    Once revoked, the token can no longer be used to authenticate MCP clients.
    This action cannot be undone.

    Args:
        token_id: UUID of the token to revoke
        current_user: Authenticated user (from JWT payload)
        db: Database session

    Returns:
        Success message

    Raises:
        HTTPException 404: If token not found or doesn't belong to user

    Example:
        DELETE /api/mcp/tokens/550e8400-e29b-41d4-a716-446655440000

        Response:
        {
            "message": "Token revoked successfully"
        }
    """
    try:
        # Extract user info from JWT payload
        user_email = current_user["sub"]

        # Get user_id from database
        result = await db.execute(
            select(User).where(User.email == user_email)
        )
        user = result.scalar_one_or_none()
        if not user:
            raise HTTPException(404, "User not found")

        # Find the token
        result = await db.execute(
            select(MCPAccessToken)
            .where(MCPAccessToken.id == token_id)
            .where(MCPAccessToken.user_id == str(user.id))
        )
        token = result.scalar_one_or_none()

        if not token:
            raise HTTPException(404, "Token not found")

        # Mark as revoked
        token.revoked = True
        token.revoked_at = datetime.utcnow()
        await db.commit()

        logger.info(f"Revoked MCP token {token_id} for user {user_email}")

        return {"message": "Token revoked successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to revoke MCP token {token_id} for user {current_user.get('sub', 'unknown')}: {e}")
        raise HTTPException(500, f"Failed to revoke token: {str(e)}")

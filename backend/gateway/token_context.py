"""
Token Context Module for Worker Process Communication.

This module provides secure token bundling for passing OAuth credentials
to worker processes. The entire context is encrypted as a JSON object,
making it easy to add additional fields in the future.

Architecture:
1. Main process fetches user's OAuth tokens from database
2. Checks if tokens are expired and refreshes if needed
3. Creates JSON payload with all user credentials
4. Encrypts entire JSON using Fernet (AES-128)
5. Passes encrypted bundle to worker via HTTP
6. Worker decrypts and extracts tokens for tool execution

Security Features:
- Fernet encryption (AES-128-CBC with HMAC)
- TTL validation (5 minutes max age) to prevent replay attacks
- User ID binding to prevent token substitution
- All tokens encrypted in single payload
- Automatic token refresh for expired OAuth tokens
- No sensitive data logged (tokens, refresh tokens masked in logs)

Future Extensibility:
The JSON structure can easily be extended to include:
- Additional OAuth scopes
- User preferences
- Session metadata
- API rate limit info
"""
import json
import logging
import httpx
from typing import Dict, Optional, List
from datetime import datetime, timezone, timedelta
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from gateway.models import UserCredential
from gateway.crypto_utils import encrypt_string, decrypt_string

logger = logging.getLogger(__name__)


async def refresh_google_token(
    cred: UserCredential,
    db: AsyncSession
) -> bool:
    """
    Refresh an expired Google OAuth token (Gmail, Google Calendar, etc.) using the refresh token.

    This function works for all Google services that use OAuth 2.0.

    Security Notes:
    - This function makes external API calls to OAuth provider
    - TODO: Add rate limiting to prevent abuse (e.g., max 10 refresh attempts/hour/user)
    - TODO: Add retry logic with exponential backoff for transient failures
    - OAuth endpoint URLs are hardcoded for security (prevent SSRF)

    Args:
        cred: UserCredential object with refresh_token
        db: Database session

    Returns:
        True if refresh succeeded, False otherwise
    """
    if not cred.refresh_token:
        logger.warning(f"No refresh token available for {cred.server_id}")
        return False

    try:
        # Decrypt refresh token
        refresh_token = decrypt_string(cred.refresh_token)

        # Get Gmail OAuth config from environment or database
        from gateway.auth_providers.registry import get_oauth_provider
        provider = await get_oauth_provider(cred.server_id, db)

        if not provider:
            logger.error(f"No OAuth provider found for {cred.server_id}")
            return False

        # Make refresh request to Google
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://oauth2.googleapis.com/token",
                data={
                    "client_id": provider.client_id,
                    "client_secret": provider.client_secret,
                    "refresh_token": refresh_token,
                    "grant_type": "refresh_token"
                },
                timeout=10.0
            )

            if response.status_code != 200:
                logger.error(
                    f"Token refresh failed for {cred.server_id}: "
                    f"{response.status_code} - {response.text}"
                )
                return False

            token_data = response.json()

            # Update credential with new access token
            new_access_token = token_data.get("access_token")
            expires_in = token_data.get("expires_in", 3600)  # Default 1 hour

            if not new_access_token:
                logger.error(f"No access_token in refresh response for {cred.server_id}")
                return False

            # Encrypt and save new access token
            cred.access_token = encrypt_string(new_access_token)

            # Update expiry time (with 5 minute buffer for safety)
            cred.expires_at = datetime.now(timezone.utc) + timedelta(
                seconds=expires_in - 300
            )

            # If new refresh token provided, update it
            if "refresh_token" in token_data:
                cred.refresh_token = encrypt_string(token_data["refresh_token"])

            await db.commit()

            logger.info(
                f"Successfully refreshed token for {cred.server_id}, "
                f"expires at {cred.expires_at}"
            )
            return True

    except Exception as e:
        logger.error(f"Failed to refresh token for {cred.server_id}: {e}")
        await db.rollback()
        return False


# Backwards compatibility alias
refresh_gmail_token = refresh_google_token


async def create_token_context(
    user_id: str,
    user_email: str,
    db: AsyncSession
) -> str:
    """
    Create encrypted token context for worker process.

    Fetches all OAuth tokens for the user from database and encrypts
    them into a single JSON payload.

    Args:
        user_id: User's database ID
        user_email: User's email address
        db: Database session

    Returns:
        Encrypted token context string (base64-encoded)

    Example encrypted payload structure:
        {
            "user_id": "user@example.com",
            "user_email": "user@example.com",
            "created_at": "2024-11-14T12:00:00Z",
            "tokens": {
                "gmail-mcp": {
                    "access_token": "ya29.xxx",
                    "refresh_token": "1//xxx",
                    "expires_at": "2024-11-14T13:00:00Z"
                },
                "github-mcp": {
                    "access_token": "ghp_xxx",
                    "refresh_token": null,
                    "expires_at": null
                }
            }
        }
    """
    logger.info(f"Creating token context for user: {user_email}")

    # Fetch all user credentials from database
    result = await db.execute(
        select(UserCredential).where(
            UserCredential.user_id == user_email,
            UserCredential.is_authorized == True
        )
    )
    credentials = result.scalars().all()

    # Build tokens dictionary
    tokens = {}
    for cred in credentials:
        # Check if token is expired and refresh if needed
        if cred.expires_at:
            now = datetime.now(timezone.utc)
            # Refresh if token expires within next 5 minutes
            if cred.expires_at <= now + timedelta(minutes=5):
                logger.info(
                    f"Token for {cred.server_id} is expired or expires soon "
                    f"(expires_at: {cred.expires_at}), attempting refresh..."
                )

                # Google services (Gmail, Google Calendar, etc.) support token refresh
                if cred.server_id in ["gmail-mcp", "gcal-mcp"]:
                    refresh_success = await refresh_google_token(cred, db)
                    if not refresh_success:
                        logger.warning(
                            f"Failed to refresh token for {cred.server_id}, "
                            f"using existing token anyway"
                        )
                else:
                    logger.warning(
                        f"Token refresh not implemented for {cred.server_id}"
                    )

        token_data = {}

        # Decrypt access token if present
        if cred.access_token:
            try:
                token_data["access_token"] = decrypt_string(cred.access_token)
            except Exception as e:
                logger.error(
                    f"Failed to decrypt access token for {cred.server_id}: {e}"
                )
                continue

        # Decrypt refresh token if present
        if cred.refresh_token:
            try:
                token_data["refresh_token"] = decrypt_string(cred.refresh_token)
            except Exception as e:
                logger.error(
                    f"Failed to decrypt refresh token for {cred.server_id}: {e}"
                )
                token_data["refresh_token"] = None
        else:
            token_data["refresh_token"] = None

        # Add expiry timestamp
        if cred.expires_at:
            token_data["expires_at"] = cred.expires_at.isoformat()
        else:
            token_data["expires_at"] = None

        tokens[cred.server_id] = token_data

    # Create context payload
    context = {
        "user_id": user_id,
        "user_email": user_email,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "tokens": tokens
    }

    # Serialize to JSON
    context_json = json.dumps(context)

    # Encrypt entire JSON payload
    encrypted_context = encrypt_string(context_json)

    logger.info(
        f"Created token context for {user_email} with {len(tokens)} services"
    )
    logger.debug(f"Services included: {list(tokens.keys())}")

    return encrypted_context


def decrypt_token_context(encrypted_context: str, max_age_seconds: int = 300) -> Dict:
    """
    Decrypt token context from worker process.

    Args:
        encrypted_context: Encrypted token context string
        max_age_seconds: Maximum age of token context in seconds (default: 300 = 5 minutes)

    Returns:
        Decrypted context dictionary with structure:
        {
            "user_id": "...",
            "user_email": "...",
            "created_at": "...",
            "tokens": {
                "server-id": {
                    "access_token": "...",
                    "refresh_token": "...",
                    "expires_at": "..."
                }
            }
        }

    Raises:
        ValueError: If decryption fails, context is invalid, or context is too old
    """
    try:
        # Decrypt the payload
        context_json = decrypt_string(encrypted_context)

        # Parse JSON
        context = json.loads(context_json)

        # Validate required fields
        required_fields = ["user_id", "user_email", "created_at", "tokens"]
        for field in required_fields:
            if field not in context:
                raise ValueError(f"Missing required field: {field}")

        # Validate token context age (prevent replay attacks)
        created_at_str = context.get("created_at")
        try:
            created_at = datetime.fromisoformat(created_at_str.replace("Z", "+00:00"))
            age_seconds = (datetime.now(timezone.utc) - created_at).total_seconds()

            if age_seconds > max_age_seconds:
                logger.warning(
                    f"Token context too old: {age_seconds:.1f}s (max: {max_age_seconds}s)"
                )
                raise ValueError(
                    f"Token context expired: created {age_seconds:.1f}s ago "
                    f"(max age: {max_age_seconds}s)"
                )

            if age_seconds < -60:  # Allow 60s clock skew
                logger.warning(f"Token context has future timestamp: {created_at_str}")
                raise ValueError("Token context has invalid future timestamp")

        except (ValueError, AttributeError) as e:
            if "Token context expired" in str(e) or "invalid future timestamp" in str(e):
                raise
            logger.error(f"Invalid created_at timestamp: {created_at_str}")
            raise ValueError(f"Invalid created_at timestamp format: {e}")

        # Log successful decryption (without sensitive data)
        logger.debug(
            f"Decrypted token context for user "
            f"with {len(context['tokens'])} services (age: {age_seconds:.1f}s)"
        )

        return context

    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse token context JSON: {e}")
        raise ValueError("Invalid token context: JSON parsing failed")
    except ValueError:
        # Re-raise ValueError with original message
        raise
    except Exception as e:
        logger.error(f"Failed to decrypt token context: {e}")
        raise ValueError(f"Token context decryption failed: {str(e)}")


def get_token_for_server(context: Dict, server_id: str) -> Optional[Dict]:
    """
    Extract token for a specific MCP server from context.

    Args:
        context: Decrypted token context dictionary
        server_id: MCP server ID (e.g., "gmail-mcp")

    Returns:
        Token dictionary with access_token, refresh_token, expires_at
        or None if server not found

    Example:
        context = decrypt_token_context(encrypted)
        gmail_token = get_token_for_server(context, "gmail-mcp")
        if gmail_token:
            access_token = gmail_token["access_token"]
    """
    tokens = context.get("tokens", {})
    return tokens.get(server_id)


def list_authorized_servers(context: Dict) -> List[str]:
    """
    Get list of all authorized MCP servers in context.

    Args:
        context: Decrypted token context dictionary

    Returns:
        List of server IDs that have tokens

    Example:
        context = decrypt_token_context(encrypted)
        servers = list_authorized_servers(context)
        # ["gmail-mcp", "github-mcp", "notion-mcp"]
    """
    tokens = context.get("tokens", {})
    return list(tokens.keys())

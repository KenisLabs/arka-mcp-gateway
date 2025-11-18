"""Password utility functions for secure password management.

This module provides cryptographically secure password generation, hashing,
validation, and reset token management following industry best practices.

Security Features:
- Uses secrets module for cryptographically secure random generation
- Enforces character diversity (uppercase, lowercase, digits, special chars)
- Uses bcrypt with appropriate work factor for password hashing
- Generates secure reset tokens with expiration
- Comprehensive validation with clear error messages
- No sensitive data in logs or exceptions

Author: MCP Gateway Team
"""

import secrets
import string
import bcrypt
from datetime import datetime, timedelta, timezone
from typing import Optional, Tuple
import logging

# Configure logger (never log passwords or sensitive data)
logger = logging.getLogger(__name__)

# Password policy constants
MIN_PASSWORD_LENGTH = 12
MAX_PASSWORD_LENGTH = 128
PASSWORD_EXPIRY_HOURS = 24  # For temporary passwords
RESET_TOKEN_EXPIRY_HOURS = 1  # For password reset tokens
BCRYPT_ROUNDS = 12  # Work factor for bcrypt (2^12 iterations)

# Character sets for password generation
UPPERCASE = string.ascii_uppercase
LOWERCASE = string.ascii_lowercase
DIGITS = string.digits
SPECIAL_CHARS = "!@#$%^&*()-_=+[]{}|;:,.<>?"


class PasswordError(Exception):
    """Base exception for password-related errors."""
    pass


class PasswordValidationError(PasswordError):
    """Exception raised when password validation fails."""
    pass


class PasswordHashError(PasswordError):
    """Exception raised when password hashing fails."""
    pass


def generate_secure_password(length: int = 16) -> str:
    """Generate a cryptographically secure random password.

    Generates a password with guaranteed character diversity:
    - At least 2 uppercase letters
    - At least 2 lowercase letters
    - At least 2 digits
    - At least 2 special characters
    - Remaining characters randomly selected from all sets

    Args:
        length: Length of password to generate (must be >= 12)

    Returns:
        str: Generated password

    Raises:
        PasswordError: If length is too short

    Example:
        >>> password = generate_secure_password(16)
        >>> len(password)
        16
        >>> validate_password_strength(password)
        True
    """
    if length < MIN_PASSWORD_LENGTH:
        raise PasswordError(
            f"Password length must be at least {MIN_PASSWORD_LENGTH} characters"
        )

    if length > MAX_PASSWORD_LENGTH:
        raise PasswordError(
            f"Password length must not exceed {MAX_PASSWORD_LENGTH} characters"
        )

    # Ensure minimum character diversity (2 of each type)
    password_chars = [
        secrets.choice(UPPERCASE),
        secrets.choice(UPPERCASE),
        secrets.choice(LOWERCASE),
        secrets.choice(LOWERCASE),
        secrets.choice(DIGITS),
        secrets.choice(DIGITS),
        secrets.choice(SPECIAL_CHARS),
        secrets.choice(SPECIAL_CHARS),
    ]

    # Fill remaining length with random characters from all sets
    all_chars = UPPERCASE + LOWERCASE + DIGITS + SPECIAL_CHARS
    remaining_length = length - len(password_chars)
    password_chars.extend(secrets.choice(all_chars) for _ in range(remaining_length))

    # Shuffle to avoid predictable patterns (using secrets for crypto-safe shuffle)
    # Fisher-Yates shuffle with cryptographic randomness
    for i in range(len(password_chars) - 1, 0, -1):
        j = secrets.randbelow(i + 1)
        password_chars[i], password_chars[j] = password_chars[j], password_chars[i]

    password = ''.join(password_chars)

    logger.info("Generated secure password with length %d", length)
    return password


def hash_password(password: str) -> str:
    """Hash a password using bcrypt.

    Uses bcrypt with appropriate work factor (2^12 iterations) for secure
    password hashing. The salt is automatically generated and included in
    the hash output.

    Args:
        password: Plain text password to hash

    Returns:
        str: Bcrypt hash (includes salt)

    Raises:
        PasswordHashError: If hashing fails
        PasswordValidationError: If password is empty or too long

    Example:
        >>> hash_val = hash_password("SecurePass123!")
        >>> hash_val.startswith('$2b$')
        True
        >>> verify_password("SecurePass123!", hash_val)
        True
    """
    if not password:
        raise PasswordValidationError("Password cannot be empty")

    if len(password) > MAX_PASSWORD_LENGTH:
        raise PasswordValidationError(
            f"Password cannot exceed {MAX_PASSWORD_LENGTH} characters"
        )

    try:
        # Generate salt and hash password
        salt = bcrypt.gensalt(rounds=BCRYPT_ROUNDS)
        password_bytes = password.encode('utf-8')
        hashed = bcrypt.hashpw(password_bytes, salt)

        logger.info("Successfully hashed password")
        return hashed.decode('utf-8')

    except Exception as e:
        logger.error("Password hashing failed: %s", str(e))
        raise PasswordHashError("Failed to hash password") from e


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a bcrypt hash.

    Constant-time comparison to prevent timing attacks.

    Args:
        plain_password: Plain text password to verify
        hashed_password: Bcrypt hash to compare against

    Returns:
        bool: True if password matches, False otherwise

    Example:
        >>> hash_val = hash_password("MyPassword123!")
        >>> verify_password("MyPassword123!", hash_val)
        True
        >>> verify_password("WrongPassword", hash_val)
        False
    """
    if not plain_password or not hashed_password:
        logger.warning("Password verification attempted with empty values")
        return False

    try:
        password_bytes = plain_password.encode('utf-8')
        hash_bytes = hashed_password.encode('utf-8')

        result = bcrypt.checkpw(password_bytes, hash_bytes)

        if result:
            logger.info("Password verification successful")
        else:
            logger.warning("Password verification failed - incorrect password")

        return result

    except Exception as e:
        logger.error("Password verification error: %s", str(e))
        return False


def validate_password_strength(password: str) -> Tuple[bool, Optional[str]]:
    """Validate password meets strength requirements.

    Requirements:
    - Minimum 12 characters
    - Maximum 128 characters
    - At least 1 uppercase letter
    - At least 1 lowercase letter
    - At least 1 digit
    - At least 1 special character

    Args:
        password: Password to validate

    Returns:
        Tuple[bool, Optional[str]]: (is_valid, error_message)

    Example:
        >>> validate_password_strength("Short1!")
        (False, 'Password must be at least 12 characters long')
        >>> validate_password_strength("SecurePassword123!")
        (True, None)
    """
    if not password:
        return False, "Password cannot be empty"

    if len(password) < MIN_PASSWORD_LENGTH:
        return False, f"Password must be at least {MIN_PASSWORD_LENGTH} characters long"

    if len(password) > MAX_PASSWORD_LENGTH:
        return False, f"Password must not exceed {MAX_PASSWORD_LENGTH} characters"

    # Check character diversity
    has_upper = any(c in UPPERCASE for c in password)
    has_lower = any(c in LOWERCASE for c in password)
    has_digit = any(c in DIGITS for c in password)
    has_special = any(c in SPECIAL_CHARS for c in password)

    if not has_upper:
        return False, "Password must contain at least one uppercase letter"

    if not has_lower:
        return False, "Password must contain at least one lowercase letter"

    if not has_digit:
        return False, "Password must contain at least one digit"

    if not has_special:
        return False, "Password must contain at least one special character (!@#$%^&*()-_=+[]{}|;:,.<>?)"

    return True, None


def generate_reset_token() -> str:
    """Generate a cryptographically secure password reset token.

    Generates a URL-safe token using 32 bytes of random data (256 bits),
    which provides sufficient entropy to prevent brute force attacks.

    Returns:
        str: URL-safe reset token (43 characters)

    Example:
        >>> token = generate_reset_token()
        >>> len(token)
        43
        >>> isinstance(token, str)
        True
    """
    # 32 bytes = 256 bits of entropy
    # URL-safe base64 encoding produces 43 characters
    token = secrets.token_urlsafe(32)
    logger.info("Generated password reset token")
    return token


def calculate_password_expiry(hours: int = PASSWORD_EXPIRY_HOURS) -> datetime:
    """Calculate password expiration datetime.

    Args:
        hours: Number of hours until expiration (default 24)

    Returns:
        datetime: UTC datetime when password will expire

    Example:
        >>> expiry = calculate_password_expiry(24)
        >>> expiry > datetime.now(timezone.utc)
        True
    """
    expiry = datetime.now(timezone.utc) + timedelta(hours=hours)
    logger.info("Calculated password expiry: %s", expiry.isoformat())
    return expiry


def calculate_reset_token_expiry() -> datetime:
    """Calculate reset token expiration datetime.

    Reset tokens are short-lived (1 hour) for security.

    Returns:
        datetime: UTC datetime when reset token will expire

    Example:
        >>> expiry = calculate_reset_token_expiry()
        >>> expiry > datetime.now(timezone.utc)
        True
    """
    expiry = datetime.now(timezone.utc) + timedelta(hours=RESET_TOKEN_EXPIRY_HOURS)
    logger.info("Calculated reset token expiry: %s", expiry.isoformat())
    return expiry


def is_password_expired(expires_at: Optional[datetime]) -> bool:
    """Check if a password has expired.

    Args:
        expires_at: Password expiration datetime (None = never expires)

    Returns:
        bool: True if password has expired, False otherwise

    Example:
        >>> past = datetime.now(timezone.utc) - timedelta(hours=1)
        >>> is_password_expired(past)
        True
        >>> future = datetime.now(timezone.utc) + timedelta(hours=1)
        >>> is_password_expired(future)
        False
    """
    if expires_at is None:
        return False

    # Ensure expires_at is timezone-aware
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)

    now = datetime.now(timezone.utc)
    expired = now >= expires_at

    if expired:
        logger.warning("Password has expired (expired at: %s)", expires_at.isoformat())

    return expired


def is_reset_token_valid(
    token: str,
    stored_token: Optional[str],
    expires_at: Optional[datetime]
) -> Tuple[bool, Optional[str]]:
    """Validate a password reset token.

    Checks:
    1. Token is not empty
    2. Stored token exists
    3. Token matches (constant-time comparison)
    4. Token has not expired

    Args:
        token: Token provided by user
        stored_token: Token stored in database
        expires_at: Token expiration datetime

    Returns:
        Tuple[bool, Optional[str]]: (is_valid, error_message)

    Example:
        >>> token = generate_reset_token()
        >>> expiry = calculate_reset_token_expiry()
        >>> is_reset_token_valid(token, token, expiry)
        (True, None)
        >>> is_reset_token_valid("wrong", token, expiry)
        (False, 'Invalid reset token')
    """
    if not token:
        return False, "Reset token cannot be empty"

    if not stored_token:
        return False, "No reset token found for this user"

    # Constant-time comparison to prevent timing attacks
    if not secrets.compare_digest(token, stored_token):
        logger.warning("Reset token mismatch")
        return False, "Invalid reset token"

    if expires_at is None:
        logger.error("Reset token has no expiration date")
        return False, "Invalid reset token configuration"

    # Ensure expires_at is timezone-aware
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)

    now = datetime.now(timezone.utc)
    if now >= expires_at:
        logger.warning("Reset token has expired (expired at: %s)", expires_at.isoformat())
        return False, "Reset token has expired. Please request a new one."

    logger.info("Reset token validation successful")
    return True, None


# Convenience function for generating temporary passwords
def generate_temporary_password() -> Tuple[str, datetime]:
    """Generate a temporary password with expiration.

    Creates a secure 16-character password that expires in 24 hours.

    Returns:
        Tuple[str, datetime]: (password, expiration_datetime)

    Example:
        >>> password, expiry = generate_temporary_password()
        >>> len(password)
        16
        >>> expiry > datetime.now(timezone.utc)
        True
    """
    password = generate_secure_password(16)
    expiry = calculate_password_expiry(PASSWORD_EXPIRY_HOURS)

    logger.info("Generated temporary password expiring at %s", expiry.isoformat())
    return password, expiry

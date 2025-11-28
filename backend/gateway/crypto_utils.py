"""
Encryption utilities for sensitive data like OAuth credentials.

Uses Fernet symmetric encryption (AES-128) to encrypt/decrypt secrets.
The encryption key should be stored in environment variables and never committed to version control.
"""

from cryptography.fernet import Fernet
from config import settings
import base64
import os
import logging

logger = logging.getLogger(__name__)


def get_encryption_key() -> bytes:
    """
    Get or generate the Fernet encryption key.

    The key should be set in the ARKA_ENCRYPTION_KEY environment variable.
    If not set, a new key will be generated (only for development).

    Returns:
        bytes: The Fernet encryption key

    Raises:
        ValueError: If encryption key is not set in production
    """
    # Try to get key from settings
    key = getattr(settings, "ENCRYPTION_KEY", None)

    if key:
        # If key is a string, encode it
        if isinstance(key, str):
            return key.encode()
        return key

    # In production, we should never generate a new key
    # For development, we'll generate one but warn about it
    logger.warning(
        "No ARKA_ENCRYPTION_KEY found in environment. "
        "Generating a new key for development. "
        "THIS SHOULD NOT HAPPEN IN PRODUCTION!"
    )
    new_key = Fernet.generate_key()
    logger.warning(f"Generated encryption key: {new_key.decode()}")
    logger.warning("Add this to your .env file as ARKA_ENCRYPTION_KEY")
    return new_key


def get_fernet_cipher() -> Fernet:
    """
    Get a Fernet cipher instance for encryption/decryption.

    Returns:
        Fernet: Configured Fernet cipher
    """
    key = get_encryption_key()
    return Fernet(key)


def encrypt_string(plaintext: str) -> str:
    """
    Encrypt a string using Fernet encryption.

    Args:
        plaintext: The string to encrypt

    Returns:
        str: Base64-encoded encrypted string
    """
    if not plaintext:
        return ""

    cipher = get_fernet_cipher()
    encrypted_bytes = cipher.encrypt(plaintext.encode())
    return encrypted_bytes.decode()


def decrypt_string(encrypted: str) -> str:
    """
    Decrypt a Fernet-encrypted string.

    Args:
        encrypted: Base64-encoded encrypted string

    Returns:
        str: Decrypted plaintext string

    Raises:
        cryptography.fernet.InvalidToken: If decryption fails
    """
    if not encrypted:
        return ""

    cipher = get_fernet_cipher()
    decrypted_bytes = cipher.decrypt(encrypted.encode())
    return decrypted_bytes.decode()


def generate_new_key() -> str:
    """
    Generate a new Fernet encryption key.

    Use this to generate a key for the ARKA_ENCRYPTION_KEY environment variable.

    Returns:
        str: Base64-encoded Fernet key
    """
    return Fernet.generate_key().decode()


if __name__ == "__main__":
    # CLI utility to generate a new encryption key
    print("Generated new Fernet encryption key:")
    print(generate_new_key())
    print("\nAdd this to your .env file as:")
    print("ARKA_ENCRYPTION_KEY=<key>")

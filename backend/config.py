"""Application configuration using Dynaconf.

This module provides centralized configuration management using Dynaconf.
Settings are loaded from environment variables, .env files, and settings files.

Example:
    Access settings in your code::

        from config import settings

        print(settings.JWT_SECRET_KEY)
        print(settings.JWT_ALGORITHM)
        print(settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)

Environment Variables:
    JWT_SECRET_KEY: Secret key for signing JWT tokens
    JWT_ALGORITHM: Algorithm for JWT signing (default: HS256)
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: Access token expiration in minutes (default: 30)
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: Refresh token expiration in days (default: 7)
"""

import logging
from pathlib import Path
import importlib
from dynaconf import Dynaconf


logger = logging.getLogger(__name__)

settings = Dynaconf(
    envvar_prefix="ARKA",  # Export variables as ARKA_VAR_NAME
    settings_files=["settings.toml", ".secrets.toml"],
    environments=True,  # Enable layered environments (dev, staging, prod)
    env_switcher="ENV_FOR_DYNACONF",  # Switch environment with this var
    load_dotenv=True,  # Load from .env file
    merge_enabled=True,  # Merge settings from multiple sources
)


# Enterprise Edition Detection with Submodule Support
# ---------------------------------------------------
def _check_enterprise_submodule():
    """
    Check if enterprise submodule exists in backend directory.

    The enterprise submodule is located at backend/enterprise/ and contains
    enterprise-only features as a Python package.
    This enables all enterprise features including:
    - Azure AD SSO authentication
    - Per-user tool permissions
    - And any future enterprise features

    Returns:
        bool: True if enterprise submodule exists, False otherwise
    """
    # Path to enterprise submodule: backend/enterprise/
    backend_dir = Path(__file__).parent  # /path/to/arka-mcp-gateway/backend
    enterprise_submodule = backend_dir / "enterprise"

    # Check if submodule exists and has __init__.py
    enterprise_init = enterprise_submodule / "__init__.py"

    if enterprise_init.exists():
        logger.info(f"Enterprise submodule detected at: {enterprise_submodule}")
        return True

    return False


# Check for enterprise submodule before any enterprise imports
_enterprise_submodule_available = _check_enterprise_submodule()


def is_enterprise_edition() -> bool:
    """
    Check if this is the enterprise edition.

    Detection:
    1. Check if enterprise submodule exists at backend/enterprise/
    2. Try to import enterprise.__enterprise__ marker
    3. Return True only if marker is True

    Returns:
        bool: True if running enterprise edition, False for community edition
    """
    # First check if submodule exists
    if not _enterprise_submodule_available:
        return False

    # Try to import and check marker
    try:
        from enterprise import __enterprise__

        return __enterprise__ is True
    except (ImportError, AttributeError):
        return False


def get_enterprise_module(module_name: str):
    """
    Dynamically import enterprise module if available.

    Args:
        module_name: Module path relative to enterprise package (e.g., "auth.azure")

    Returns:
        Module object if successful, None otherwise
    """
    if not is_enterprise_edition():
        return None

    try:
        return importlib.import_module(f"enterprise.{module_name}")
    except ImportError as e:
        logger.error(f"Failed to import enterprise.{module_name}: {e}")
        return None

"""Enterprise Edition Detection Module.

This module provides utilities to detect whether the application is running
in Enterprise or Community edition, and to dynamically load enterprise modules.

The enterprise edition is detected by checking for a git submodule at
backend/enterprise/ that contains enterprise-only features.
"""

import logging
import importlib
from pathlib import Path


logger = logging.getLogger(__name__)


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

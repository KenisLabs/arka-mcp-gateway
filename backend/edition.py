"""Enterprise Edition Detection Module.

This module provides utilities to detect whether the application is running
in Enterprise or Community edition, and to dynamically load enterprise modules.

The enterprise edition is detected by attempting to import the enterprise package.
"""

import logging
import importlib


logger = logging.getLogger(__name__)


def is_enterprise_edition() -> bool:
    """
    Check if this is the enterprise edition.

    Attempts to import the enterprise module and check for the __enterprise__ marker.
    Returns True only if the marker exists and is True.

    Returns:
        bool: True if running enterprise edition, False for community edition
    """
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

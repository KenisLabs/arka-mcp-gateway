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

from dynaconf import Dynaconf

settings = Dynaconf(
    envvar_prefix="ARKA",  # Export variables as ARKA_VAR_NAME
    settings_files=["settings.toml", ".secrets.toml"],
    environments=True,  # Enable layered environments (dev, staging, prod)
    env_switcher="ENV_FOR_DYNACONF",  # Switch environment with this var
    load_dotenv=True,  # Load from .env file
    merge_enabled=True,  # Merge settings from multiple sources
)

"""Database configuration and session management.

This module provides SQLAlchemy database engine and session management
for the Arka MCP Gateway backend.

Example:
    Use the database session in your code::

        from database import get_db_session

        async with get_db_session() as session:
            result = await session.execute(select(User))
            users = result.scalars().all()
"""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy import text
from contextlib import asynccontextmanager
from config import settings
import logging

logger = logging.getLogger(__name__)

# Create SQLAlchemy Base for model definitions
Base = declarative_base()

# Create async engine
engine = create_async_engine(
    settings.database_url,
    echo=False,  # Set to True for SQL query logging during development
    pool_pre_ping=True,  # Verify connections before using them
    pool_size=5,  # Number of connections to maintain in the pool
    max_overflow=10  # Max overflow connections beyond pool_size
)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)


async def ensure_database_exists():
    """Ensure the database exists, create it if it doesn't.

    For PostgreSQL, connects to the default 'postgres' database to create
    the target database if it doesn't exist.

    This is safe to call multiple times - it won't recreate existing databases.
    """
    # Parse database URL to get database name and connection details
    import re
    from urllib.parse import urlparse

    db_url = settings.database_url

    # Only handle PostgreSQL databases
    if not db_url.startswith("postgresql"):
        logger.debug("Not a PostgreSQL database, skipping database creation check")
        return

    # Parse the URL to extract database name
    parsed = urlparse(db_url.replace("postgresql+asyncpg://", "postgresql://"))
    db_name = parsed.path.lstrip("/")

    if not db_name:
        logger.warning("Could not extract database name from URL")
        return

    # Create connection to postgres database (default system database)
    # Replace the database name with 'postgres' in the URL
    postgres_url = db_url.replace(f"/{db_name}", "/postgres")

    try:
        # Create a temporary engine to connect to postgres database
        temp_engine = create_async_engine(postgres_url, isolation_level="AUTOCOMMIT")

        async with temp_engine.connect() as conn:
            # Check if database exists
            result = await conn.execute(
                text(f"SELECT 1 FROM pg_database WHERE datname = '{db_name}'")
            )
            exists = result.scalar() is not None

            if not exists:
                logger.info(f"Database '{db_name}' does not exist, creating...")
                await conn.execute(text(f"CREATE DATABASE {db_name}"))
                logger.info(f"✓ Database '{db_name}' created successfully")
            else:
                logger.debug(f"Database '{db_name}' already exists")

        await temp_engine.dispose()

    except Exception as e:
        logger.warning(f"Could not create database automatically: {e}")
        logger.warning(f"Please create database '{db_name}' manually if it doesn't exist")


async def init_db():
    """Initialize the database by creating all tables.

    This should be called once on application startup.

    Steps:
    1. Ensure database exists (creates if needed)
    2. Create all tables from SQLAlchemy models
    """
    logger.info("Initializing database...")

    # First, ensure the database itself exists
    await ensure_database_exists()

    # Then create tables
    async with engine.begin() as conn:
        # Import all models here to ensure they're registered with Base
        from gateway.models import (  # noqa: F401
            UserCredential,
            RefreshToken,
            User,
            OrganizationToolAccess,
            UserToolAccess,
            AuditLog
        )

        # Create all tables
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database initialized successfully")


async def close_db():
    """Close all database connections.

    This should be called on application shutdown.
    """
    logger.info("Closing database connections...")
    await engine.dispose()
    logger.info("Database connections closed")


@asynccontextmanager
async def get_db_session():
    """Get a database session.

    Use this as an async context manager to get a database session.
    The session will be automatically closed when the context exits.

    Yields:
        AsyncSession: Database session

    Example::

        async with get_db_session() as session:
            result = await session.execute(select(User))
            users = result.scalars().all()
    """
    session = AsyncSessionLocal()
    try:
        yield session
        await session.commit()
    except Exception:
        await session.rollback()
        raise
    finally:
        await session.close()


async def get_db():
    """FastAPI dependency for getting a database session.

    Use this as a FastAPI dependency to inject a database session
    into your route handlers.

    Yields:
        AsyncSession: Database session

    Example::

        @app.get("/users")
        async def get_users(db: AsyncSession = Depends(get_db)):
            result = await db.execute(select(User))
            return result.scalars().all()
    """
    async with get_db_session() as session:
        yield session

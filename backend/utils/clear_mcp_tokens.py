"""
Clear all MCP access tokens from the database.

This script deletes all records from the mcp_access_tokens table
to avoid confusion during testing.
"""
import asyncio
from sqlalchemy import text
from database import get_db_session
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def clear_tokens():
    """Delete all MCP access tokens from the database."""
    async with get_db_session() as db:
        try:
            # Delete all records from mcp_access_tokens table
            result = await db.execute(text("DELETE FROM mcp_access_tokens"))
            deleted_count = result.rowcount

            logger.info(f"✓ Deleted {deleted_count} MCP access token(s)")

            if deleted_count > 0:
                logger.info("Database cleared successfully!")
            else:
                logger.info("No MCP access tokens found in database")

        except Exception as e:
            logger.error(f"Error clearing tokens: {e}")
            raise


if __name__ == "__main__":
    asyncio.run(clear_tokens())

"""
Reset tool database: Delete all tools and repopulate from filesystem.

This script:
1. Deletes all MCPServerTool records from the database
2. Deletes associated OrganizationToolPermission and UserToolPermission records
3. Discovers tools from filesystem
4. Populates database with fresh data

Run this script to clean up stale/incorrect tool data.
"""
import asyncio
from sqlalchemy import delete
from database import get_db_session
from gateway.models import MCPServerTool, OrganizationToolPermission, UserToolPermission
from utils.populate_tools import discover_tools, populate_database
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def delete_all_tools():
    """Delete all tools and associated permissions from the database."""
    async with get_db_session() as db:
        # Delete user tool permissions first (foreign key constraint)
        result = await db.execute(delete(UserToolPermission))
        user_perms_deleted = result.rowcount
        logger.info(f"Deleted {user_perms_deleted} user tool permissions")

        # Delete organization tool permissions
        result = await db.execute(delete(OrganizationToolPermission))
        org_perms_deleted = result.rowcount
        logger.info(f"Deleted {org_perms_deleted} organization tool permissions")

        # Delete all tools
        result = await db.execute(delete(MCPServerTool))
        tools_deleted = result.rowcount
        logger.info(f"Deleted {tools_deleted} tools")

        await db.commit()

        logger.info(f"\n✓ Database cleaned: {tools_deleted} tools removed\n")


async def main():
    """Main function to reset and repopulate tools."""
    logger.info("="*60)
    logger.info("RESETTING TOOL DATABASE")
    logger.info("="*60)

    # Step 1: Delete all existing tools
    logger.info("\n[1/3] Deleting all existing tools from database...")
    await delete_all_tools()

    # Step 2: Discover tools from filesystem
    logger.info("[2/3] Discovering tools from filesystem...")
    tools_by_server = await discover_tools()

    if not tools_by_server:
        logger.warning("No tools found! Check that arka_mcp/servers/*_tools/ directories exist.")
        return

    # Show summary
    total_tools = sum(len(tools) for tools in tools_by_server.values())
    logger.info(f"\nDiscovered {total_tools} tools across {len(tools_by_server)} servers:")
    for server_id, tools in tools_by_server.items():
        logger.info(f"  {server_id}: {len(tools)} tools")

    # Step 3: Populate database
    logger.info("\n[3/3] Populating database with fresh tools...")
    await populate_database(tools_by_server, dry_run=False)

    logger.info("\n" + "="*60)
    logger.info("✓ Tool database reset complete!")
    logger.info("="*60)


if __name__ == "__main__":
    asyncio.run(main())

"""
Common utilities for tool synchronization.

Shared logic used by both gateway/tool_sync.py (automatic sync on startup)
and utils/populate_tools.py (manual sync script).
"""
import logging
from typing import List, Dict
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession
from gateway.models import MCPServerTool, OrganizationToolPermission, UserToolPermission

logger = logging.getLogger(__name__)


async def delete_orphaned_tools(
    db: AsyncSession,
    all_db_tools: List[MCPServerTool],
    discovered_tools: Dict[str, set],
    dry_run: bool = False
) -> int:
    """
    Delete tools from database that no longer exist in filesystem.

    Args:
        db: Database session
        all_db_tools: List of all tools currently in database
        discovered_tools: Dict mapping server_id -> set of tool_names found in filesystem
        dry_run: If True, only count deletions without actually deleting

    Returns:
        int: Number of tools deleted (or would be deleted if dry_run=True)
    """
    deleted_count = 0

    for db_tool in all_db_tools:
        server_id = db_tool.mcp_server_id
        tool_name = db_tool.tool_name

        # Check if tool exists in discovered tools (Pythonic approach)
        if server_id not in discovered_tools:
            # Server directory no longer exists - all its tools are orphaned
            logger.info(f"🗑️  Deleting tool from removed server: {server_id}:{tool_name}")

            if not dry_run:
                # Delete associated permissions first (foreign key constraints)
                await db.execute(
                    delete(OrganizationToolPermission).where(
                        OrganizationToolPermission.tool_id == db_tool.id
                    )
                )
                await db.execute(
                    delete(UserToolPermission).where(
                        UserToolPermission.tool_id == db_tool.id
                    )
                )

                # Delete the tool itself
                await db.delete(db_tool)

            deleted_count += 1

        elif tool_name not in discovered_tools[server_id]:
            # Server directory exists but tool file was removed
            logger.info(f"🗑️  Deleting orphaned tool: {server_id}:{tool_name} (file removed)")

            if not dry_run:
                # Delete associated permissions first (foreign key constraints)
                await db.execute(
                    delete(OrganizationToolPermission).where(
                        OrganizationToolPermission.tool_id == db_tool.id
                    )
                )
                await db.execute(
                    delete(UserToolPermission).where(
                        UserToolPermission.tool_id == db_tool.id
                    )
                )

                # Delete the tool itself
                await db.delete(db_tool)

            deleted_count += 1

    return deleted_count

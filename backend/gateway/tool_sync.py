"""
Automatic Tool Synchronization Module.

Automatically discovers and registers tools from filesystem to database on startup.
This ensures the database always reflects the current codebase state.

Key features:
- Creates new tools found in filesystem
- Updates metadata for existing tools
- Deletes orphaned tools (tools in DB but not in filesystem)
- Cleans up associated permissions for deleted tools
"""
import os
import logging
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from gateway.models import MCPServerTool, OrganizationToolPermission
from gateway.tool_sync_common import delete_orphaned_tools
from arka_mcp.utils import parse_tool_file

logger = logging.getLogger(__name__)

# Base directories
BASE_DIR = "arka_mcp/servers"
BASE_MODULE = "arka_mcp.servers"


async def sync_tools_to_database(db: AsyncSession) -> dict:
    """
    Synchronize tools from filesystem to database.

    Scans all *_tools directories and ensures database has up-to-date tool metadata.
    Also deletes orphaned tools (tools in DB but not in filesystem).

    Args:
        db: Database session

    Returns:
        dict: Statistics about sync operation
            {
                "created": int,
                "updated": int,
                "deleted": int,
                "failed": int,
                "total": int,
                "servers": list[str]
            }
    """
    stats = {
        "created": 0,
        "updated": 0,
        "deleted": 0,
        "failed": 0,
        "total": 0,
        "servers": []
    }

    # Track all discovered tools per server for orphan detection
    discovered_tools = {}  # server_id -> set of tool_names

    # Check if base directory exists
    if not os.path.exists(BASE_DIR):
        logger.warning(f"Tool base directory '{BASE_DIR}' not found, skipping tool sync")
        return stats

    try:
        # Scan all *_tools directories
        for entry in os.listdir(BASE_DIR):
            dir_path = os.path.join(BASE_DIR, entry)

            # Skip if not a directory or doesn't end with _tools
            if not os.path.isdir(dir_path) or not entry.endswith("_tools"):
                continue

            # Extract service name (e.g., "notion_tools" -> "notion-mcp")
            service_name = entry.replace("_tools", "") + "-mcp"
            stats["servers"].append(service_name)

            # Initialize tracking set for this server
            discovered_tools[service_name] = set()

            # Scan all .py files in the directory
            for filename in os.listdir(dir_path):
                if not filename.endswith(".py") or filename.startswith("__"):
                    continue

                tool_name = filename[:-3]  # Remove .py extension
                module_path = f"{BASE_MODULE}.{entry}.{tool_name}"

                # Parse tool metadata
                try:
                    tool_info = parse_tool_file(module_path, service_name, tool_name)
                except Exception as e:
                    logger.debug(f"Failed to parse {service_name}:{tool_name}: {e}")
                    stats["failed"] += 1
                    continue

                if not tool_info:
                    stats["failed"] += 1
                    continue

                # Track this tool as discovered
                discovered_tools[service_name].add(tool_name)

                # Extract display name from tool_name (convert snake_case to Title Case)
                display_name = tool_name.replace("_", " ").title()

                # Extract description from docstring (first line)
                description = None
                if tool_info.get("docstring"):
                    lines = [line.strip() for line in tool_info["docstring"].split("\n") if line.strip()]
                    if lines:
                        description = lines[0]

                # Determine if tool is dangerous (based on name patterns)
                is_dangerous = any(keyword in tool_name.lower() for keyword in [
                    "delete", "remove", "destroy", "drop", "truncate", "purge"
                ])

                # Check if tool already exists
                result = await db.execute(
                    select(MCPServerTool).where(
                        MCPServerTool.mcp_server_id == service_name,
                        MCPServerTool.tool_name == tool_name
                    )
                )
                existing_tool = result.scalar_one_or_none()

                if existing_tool:
                    # Update existing tool metadata
                    existing_tool.display_name = display_name
                    existing_tool.description = description or f"{display_name} tool for {service_name}"
                    existing_tool.category = service_name.replace("-mcp", "").title()
                    existing_tool.is_dangerous = is_dangerous
                    stats["updated"] += 1
                else:
                    # Create new tool
                    new_tool = MCPServerTool(
                        mcp_server_id=service_name,
                        tool_name=tool_name,
                        display_name=display_name,
                        description=description or f"{display_name} tool for {service_name}",
                        category=service_name.replace("-mcp", "").title(),
                        is_dangerous=is_dangerous
                    )
                    db.add(new_tool)
                    await db.flush()

                    # Create default organization permission (enabled unless dangerous)
                    org_perm = OrganizationToolPermission(
                        tool_id=new_tool.id,
                        enabled=not is_dangerous
                    )
                    db.add(org_perm)
                    stats["created"] += 1

        # Delete orphaned tools (tools in DB but not in filesystem)
        logger.debug("Checking for orphaned tools in database...")

        # Get all tools from database
        all_db_tools_result = await db.execute(select(MCPServerTool))
        all_db_tools = all_db_tools_result.scalars().all()

        # Use shared function to delete orphaned tools
        stats["deleted"] = await delete_orphaned_tools(db, all_db_tools, discovered_tools)

        # Commit all changes
        await db.commit()

        stats["total"] = stats["created"] + stats["updated"]
        return stats

    except Exception as e:
        # Rollback on any error to prevent partial commits
        await db.rollback()
        logger.error(f"Tool sync failed, rolling back all changes: {e}")
        raise  # Re-raise to be caught by outer handler in sync_tools_on_startup()


async def sync_tools_on_startup(db: AsyncSession):
    """
    Wrapper function for tool sync during server startup.

    Logs results and handles errors gracefully without crashing the server.

    Args:
        db: Database session
    """
    try:
        logger.info("🔄 Synchronizing tools from filesystem to database...")
        stats = await sync_tools_to_database(db)

        if stats["total"] == 0 and stats["deleted"] == 0 and stats["failed"] == 0:
            logger.info("✓ No tool changes detected")
        else:
            # Build summary message
            changes = []
            if stats["created"] > 0:
                changes.append(f"{stats['created']} created")
            if stats["updated"] > 0:
                changes.append(f"{stats['updated']} updated")
            if stats["deleted"] > 0:
                changes.append(f"{stats['deleted']} deleted")
            if stats["failed"] > 0:
                changes.append(f"{stats['failed']} failed")

            logger.info(
                f"✓ Tool sync complete: {', '.join(changes)} "
                f"across {len(stats['servers'])} servers"
            )
            if stats["servers"]:
                logger.debug(f"  Servers synced: {', '.join(stats['servers'])}")

    except Exception as e:
        logger.error(f"Failed to sync tools on startup: {e}", exc_info=True)
        logger.warning("Server will continue without tool sync - tools may be outdated")

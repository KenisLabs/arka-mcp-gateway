"""
Populate MCPServerTool table by scanning filesystem for available tools.

This script:
1. Scans arka_mcp/servers/*_tools/ directories for Python tool files
2. Extracts metadata from each tool (name, description, parameters)
3. Creates MCPServerTool records in the database
4. Creates default OrganizationToolPermission records
5. Deletes orphaned tools (tools in DB but not in filesystem)
6. Cleans up associated permissions for deleted tools

Run this script whenever:
- New MCP servers are added
- New tools are added to existing servers
- Tools are renamed or removed
- Database needs to be synced with codebase

Usage:
    python populate_tools.py              # Apply changes to database
    python populate_tools.py --dry-run    # Preview changes without applying
"""
import os
import asyncio
from sqlalchemy import select
from database import get_db_session
from gateway.models import MCPServerTool, OrganizationToolPermission
from gateway.tool_sync_common import delete_orphaned_tools
from arka_mcp.utils import parse_tool_file
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Base directories
BASE_DIR = "arka_mcp/servers"
BASE_MODULE = "arka_mcp.servers"


async def discover_tools():
    """
    Discover all tools by scanning the filesystem.

    Returns:
        dict: Mapping of server_id -> list of tool info
        Example:
        {
            "notion": [
                {
                    "tool_name": "create_page",
                    "display_name": "Create Page",
                    "description": "Creates a new page in Notion",
                    "category": "Pages",
                    ...
                }
            ]
        }
    """
    tools_by_server = {}

    # Check if base directory exists
    if not os.path.exists(BASE_DIR):
        logger.error(f"Base directory '{BASE_DIR}' not found")
        return tools_by_server

    # Scan all *_tools directories
    for entry in os.listdir(BASE_DIR):
        dir_path = os.path.join(BASE_DIR, entry)

        # Skip if not a directory or doesn't end with _tools
        if not os.path.isdir(dir_path) or not entry.endswith("_tools"):
            continue

        # Extract service name (e.g., "notion_tools" -> "notion-mcp")
        # Add "-mcp" suffix to match registered MCP server IDs
        service_name = entry.replace("_tools", "") + "-mcp"

        logger.info(f"Scanning {service_name} tools in {dir_path}")

        tools = []

        # Scan all .py files in the directory
        for filename in os.listdir(dir_path):
            if not filename.endswith(".py") or filename.startswith("__"):
                continue

            tool_name = filename[:-3]  # Remove .py extension
            module_path = f"{BASE_MODULE}.{entry}.{tool_name}"

            logger.debug(f"  Parsing tool: {service_name}:{tool_name}")

            # Parse tool metadata
            tool_info = parse_tool_file(module_path, service_name, tool_name)

            if not tool_info:
                logger.warning(f"  Failed to parse {service_name}:{tool_name}")
                continue

            # Extract display name from tool_name (convert snake_case to Title Case)
            display_name = tool_name.replace("_", " ").title()

            # Extract description from docstring (first line)
            description = None
            if tool_info.get("docstring"):
                # Get first non-empty line
                lines = [line.strip() for line in tool_info["docstring"].split("\n") if line.strip()]
                if lines:
                    description = lines[0]

            # Determine if tool is dangerous (based on name patterns)
            is_dangerous = any(keyword in tool_name.lower() for keyword in [
                "delete", "remove", "destroy", "drop", "truncate", "purge"
            ])

            tools.append({
                "tool_name": tool_name,
                "display_name": display_name,
                "description": description or f"{display_name} tool for {service_name}",
                "category": service_name.title(),
                "is_dangerous": is_dangerous,
                "signature": tool_info.get("signature"),
                "return_type": tool_info.get("return_type")
            })

        if tools:
            tools_by_server[service_name] = tools
            logger.info(f"  Found {len(tools)} tools for {service_name}")

    return tools_by_server


async def populate_database(tools_by_server: dict, dry_run: bool = False):
    """
    Populate database with discovered tools.

    Args:
        tools_by_server: Dict mapping server_id -> list of tool info
        dry_run: If True, only show what would be done without making changes
    """
    async with get_db_session() as db:
        total_created = 0
        total_updated = 0
        total_deleted = 0

        # Track all discovered tool names per server for cleanup
        discovered_tools = {}  # server_id -> set of tool_names

        for server_id, tools in tools_by_server.items():
            logger.info(f"\nProcessing {server_id} ({len(tools)} tools):")

            # Track discovered tools for this server
            discovered_tools[server_id] = set()

            for tool_data in tools:
                tool_name = tool_data["tool_name"]
                discovered_tools[server_id].add(tool_name)

                # Check if tool already exists
                result = await db.execute(
                    select(MCPServerTool).where(
                        MCPServerTool.mcp_server_id == server_id,
                        MCPServerTool.tool_name == tool_name
                    )
                )
                existing_tool = result.scalar_one_or_none()

                if existing_tool:
                    # Update existing tool metadata
                    logger.info(f"  ↻ Updating {server_id}:{tool_name}")

                    if not dry_run:
                        existing_tool.display_name = tool_data["display_name"]
                        existing_tool.description = tool_data["description"]
                        existing_tool.category = tool_data["category"]
                        existing_tool.is_dangerous = tool_data["is_dangerous"]

                    total_updated += 1
                else:
                    # Create new tool
                    logger.info(f"  ✓ Creating {server_id}:{tool_name}")

                    if not dry_run:
                        new_tool = MCPServerTool(
                            mcp_server_id=server_id,
                            tool_name=tool_name,
                            display_name=tool_data["display_name"],
                            description=tool_data["description"],
                            category=tool_data["category"],
                            is_dangerous=tool_data["is_dangerous"]
                        )
                        db.add(new_tool)
                        await db.flush()

                        # Create default organization permission (enabled unless dangerous)
                        org_perm = OrganizationToolPermission(
                            tool_id=new_tool.id,
                            enabled=not tool_data["is_dangerous"]
                        )
                        db.add(org_perm)

                    total_created += 1

        # Delete orphaned tools (tools in DB but not in filesystem)
        logger.info("\nChecking for orphaned tools in database...")

        # Get all tools from database
        all_db_tools_result = await db.execute(select(MCPServerTool))
        all_db_tools = all_db_tools_result.scalars().all()

        # Use shared function to delete orphaned tools
        total_deleted = await delete_orphaned_tools(db, all_db_tools, discovered_tools, dry_run=dry_run)

        if not dry_run:
            await db.commit()

        # Print summary
        logger.info("\n" + "="*60)
        logger.info("SUMMARY:")
        logger.info(f"  Created: {total_created} tools")
        logger.info(f"  Updated: {total_updated} tools")
        logger.info(f"  Deleted: {total_deleted} tools (orphaned)")
        logger.info(f"  Total:   {total_created + total_updated} tools in database")

        if dry_run:
            logger.info("\n⚠️  DRY RUN - No changes were made to the database")
        else:
            logger.info("\n✓ Database synchronized successfully!")

        logger.info("="*60)


async def main():
    """Main function to discover and populate tools."""
    import sys

    # Check for dry-run flag
    dry_run = "--dry-run" in sys.argv

    if dry_run:
        logger.info("Running in DRY RUN mode - no database changes will be made\n")

    logger.info("Discovering tools from filesystem...\n")

    # Discover tools
    tools_by_server = await discover_tools()

    if not tools_by_server:
        logger.warning("No tools found! Check that arka_mcp/servers/*_tools/ directories exist.")
        return

    # Show summary
    total_tools = sum(len(tools) for tools in tools_by_server.values())
    logger.info(f"\nDiscovered {total_tools} tools across {len(tools_by_server)} servers:")
    for server_id, tools in tools_by_server.items():
        logger.info(f"  {server_id}: {len(tools)} tools")

    # Populate database
    logger.info("\nPopulating database...")
    await populate_database(tools_by_server, dry_run=dry_run)


if __name__ == "__main__":
    asyncio.run(main())

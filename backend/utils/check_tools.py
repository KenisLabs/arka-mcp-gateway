"""Quick script to check what tools are in the database."""
import asyncio
from sqlalchemy import select
from database import get_db_session
from gateway.models import MCPServerTool, OrganizationToolPermission

async def main():
    async with get_db_session() as db:
        # Get all tools
        result = await db.execute(
            select(MCPServerTool).order_by(MCPServerTool.mcp_server_id, MCPServerTool.tool_name)
        )
        tools = result.scalars().all()

        print(f"\n{'='*80}")
        print(f"Total tools in database: {len(tools)}")
        print(f"{'='*80}\n")

        current_server = None
        for tool in tools:
            if tool.mcp_server_id != current_server:
                current_server = tool.mcp_server_id
                print(f"\n{current_server.upper()} ({tool.category}):")
                print("-" * 80)

            # Get org permission
            perm_result = await db.execute(
                select(OrganizationToolPermission).where(
                    OrganizationToolPermission.tool_id == tool.id
                )
            )
            perm = perm_result.scalar_one_or_none()
            enabled = perm.enabled if perm else True

            status = "✓" if enabled else "✗"
            danger = "⚠️ " if tool.is_dangerous else ""

            print(f"  {status} {danger}{tool.tool_name:30} - {tool.description}")

        print(f"\n{'='*80}\n")

if __name__ == "__main__":
    asyncio.run(main())

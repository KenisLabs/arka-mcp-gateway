"""
API endpoints for MCP server tool management.

Provides endpoints for:
- Managing tools within MCP servers (CRUD operations)
- Organization-level tool permissions
- User-level tool permission overrides
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import Optional, List
from database import get_db
from gateway.models import (
    MCPServerTool,
    OrganizationToolPermission,
    UserToolPermission,
    User,
)
from auth.rbac import require_admin
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/admin", tags=["admin-tool-management"])


# ============================================================================
# Pydantic Models
# ============================================================================


class ToolCreateRequest(BaseModel):
    """Request model for creating a new tool."""

    tool_name: str
    display_name: str
    description: Optional[str] = None
    category: Optional[str] = None
    is_dangerous: bool = False


class ToolUpdateRequest(BaseModel):
    """Request model for updating a tool."""

    display_name: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    is_dangerous: Optional[bool] = None


class BulkToggleRequest(BaseModel):
    """Request model for bulk toggling tool permissions."""

    tool_ids: List[str]
    enabled: bool


class ToolPermissionUpdate(BaseModel):
    """Single tool permission update."""

    tool_name: str
    is_enabled: bool


class BulkToolUpdateRequest(BaseModel):
    """Request model for bulk updating tool permissions for a server."""

    tools: List[ToolPermissionUpdate]


# ============================================================================
# MCP Server Tools CRUD
# ============================================================================


@router.get("/servers/{server_id}/tools")
async def list_mcp_server_tools(
    server_id: str,
    admin: dict = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """
    List all tools available for a specific MCP server.

    Returns tools with organization-level permissions and user count with overrides.

    Args:
        server_id: MCP server ID (e.g., 'github-mcp')
        admin: Current admin user (from JWT)
        db: Database session

    Returns:
        {
            "server_id": "github-mcp",
            "tools": [
                {
                    "id": "uuid",
                    "tool_name": "create_issue",
                    "display_name": "Create Issue",
                    "description": "...",
                    "category": "Issues",
                    "is_dangerous": false,
                    "org_enabled": true,
                    "user_override_count": 3
                }
            ]
        }
    """
    # Get all tools for this server
    result = await db.execute(
        select(MCPServerTool)
        .where(MCPServerTool.mcp_server_id == server_id)
        .order_by(MCPServerTool.category, MCPServerTool.display_name)
    )
    tools = result.scalars().all()

    # If no tools exist, return empty list
    if not tools:
        logger.warning(
            f"No tools found for server '{server_id}'. Run utils/populate_tools.py to discover tools."
        )
        return {"server_id": server_id, "tools": []}

    # Get organization permissions
    org_perms_result = await db.execute(select(OrganizationToolPermission))
    org_perms_map = {
        perm.tool_id: perm.enabled for perm in org_perms_result.scalars().all()
    }

    # Get user override counts per tool
    user_override_counts = {}
    for tool in tools:
        count_result = await db.execute(
            select(func.count(UserToolPermission.id)).where(
                UserToolPermission.tool_id == tool.id
            )
        )
        user_override_counts[tool.id] = count_result.scalar() or 0

    # Build response
    tools_response = []
    for tool in tools:
        tools_response.append(
            {
                "id": tool.id,
                "name": tool.tool_name,  # Use 'name' for consistency with frontend
                "display_name": tool.display_name,
                "description": tool.description,
                "category": tool.category,
                "is_dangerous": tool.is_dangerous,
                "is_enabled": org_perms_map.get(
                    tool.id, True
                ),  # Changed from org_enabled to is_enabled
                "user_override_count": user_override_counts.get(tool.id, 0),
            }
        )

    return {"server_id": server_id, "tools": tools_response}


@router.post("/servers/{server_id}/tools")
async def create_mcp_server_tool(
    server_id: str,
    tool: ToolCreateRequest,
    admin: dict = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """
    Add a new tool to an MCP server.

    Args:
        server_id: MCP server ID
        tool: Tool creation data
        admin: Current admin user (from JWT)
        db: Database session

    Returns:
        Created tool data

    Raises:
        HTTPException 400: If tool already exists
    """
    # Check if tool already exists
    result = await db.execute(
        select(MCPServerTool).where(
            MCPServerTool.mcp_server_id == server_id,
            MCPServerTool.tool_name == tool.tool_name,
        )
    )
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=400,
            detail=f"Tool '{tool.tool_name}' already exists for server '{server_id}'",
        )

    # Create tool
    new_tool = MCPServerTool(
        mcp_server_id=server_id,
        tool_name=tool.tool_name,
        display_name=tool.display_name,
        description=tool.description,
        category=tool.category,
        is_dangerous=tool.is_dangerous,
    )
    db.add(new_tool)
    await db.flush()

    # Create default organization permission (enabled unless dangerous)
    org_perm = OrganizationToolPermission(
        tool_id=new_tool.id, enabled=not tool.is_dangerous
    )
    db.add(org_perm)
    await db.flush()

    logger.info(
        f"Admin {admin.get('sub')} created tool '{tool.tool_name}' "
        f"for server '{server_id}'"
    )

    return {
        "id": new_tool.id,
        "tool_name": new_tool.tool_name,
        "display_name": new_tool.display_name,
        "description": new_tool.description,
        "category": new_tool.category,
        "is_dangerous": new_tool.is_dangerous,
        "org_enabled": not tool.is_dangerous,
    }


@router.put("/servers/{server_id}/tools/{tool_id}")
async def update_mcp_server_tool(
    server_id: str,
    tool_id: str,
    tool: ToolUpdateRequest,
    admin: dict = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """
    Update tool metadata.

    Args:
        server_id: MCP server ID
        tool_id: Tool ID to update
        tool: Tool update data
        admin: Current admin user (from JWT)
        db: Database session

    Returns:
        Updated tool data

    Raises:
        HTTPException 404: If tool not found
    """
    # Get tool
    result = await db.execute(
        select(MCPServerTool).where(
            MCPServerTool.id == tool_id, MCPServerTool.mcp_server_id == server_id
        )
    )
    existing_tool = result.scalar_one_or_none()

    if not existing_tool:
        raise HTTPException(
            status_code=404,
            detail=f"Tool '{tool_id}' not found for server '{server_id}'",
        )

    # Update fields
    if tool.display_name is not None:
        existing_tool.display_name = tool.display_name
    if tool.description is not None:
        existing_tool.description = tool.description
    if tool.category is not None:
        existing_tool.category = tool.category
    if tool.is_dangerous is not None:
        existing_tool.is_dangerous = tool.is_dangerous

    await db.flush()

    logger.info(
        f"Admin {admin.get('sub')} updated tool '{existing_tool.tool_name}' "
        f"for server '{server_id}'"
    )

    return {
        "id": existing_tool.id,
        "tool_name": existing_tool.tool_name,
        "display_name": existing_tool.display_name,
        "description": existing_tool.description,
        "category": existing_tool.category,
        "is_dangerous": existing_tool.is_dangerous,
    }


@router.delete("/servers/{server_id}/tools/{tool_id}")
async def delete_mcp_server_tool(
    server_id: str,
    tool_id: str,
    admin: dict = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """
    Delete a tool from an MCP server.

    Also deletes associated org and user permissions (CASCADE).

    Args:
        server_id: MCP server ID
        tool_id: Tool ID to delete
        admin: Current admin user (from JWT)
        db: Database session

    Returns:
        Success message

    Raises:
        HTTPException 404: If tool not found
    """
    # Get tool
    result = await db.execute(
        select(MCPServerTool).where(
            MCPServerTool.id == tool_id, MCPServerTool.mcp_server_id == server_id
        )
    )
    tool = result.scalar_one_or_none()

    if not tool:
        raise HTTPException(
            status_code=404,
            detail=f"Tool '{tool_id}' not found for server '{server_id}'",
        )

    tool_name = tool.tool_name

    # Delete org permission
    await db.execute(
        select(OrganizationToolPermission).where(
            OrganizationToolPermission.tool_id == tool_id
        )
    )
    # Delete user permissions
    await db.execute(
        select(UserToolPermission).where(UserToolPermission.tool_id == tool_id)
    )

    # Delete tool
    await db.delete(tool)
    await db.flush()

    logger.info(
        f"Admin {admin.get('sub')} deleted tool '{tool_name}' "
        f"from server '{server_id}'"
    )

    return {
        "message": f"Tool '{tool_name}' deleted successfully",
        "tool_id": tool_id,
        "server_id": server_id,
    }


# ============================================================================
# Organization Tool Permissions
# ============================================================================


@router.put("/organization/tools/{tool_id}/toggle")
async def toggle_organization_tool_permission(
    tool_id: str,
    enabled: bool,
    admin: dict = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """
    Enable or disable a specific tool at organization level.

    Args:
        tool_id: Tool ID
        enabled: True to enable, False to disable
        admin: Current admin user (from JWT)
        db: Database session

    Returns:
        Success message

    Raises:
        HTTPException 404: If tool not found
    """
    # Verify tool exists
    result = await db.execute(select(MCPServerTool).where(MCPServerTool.id == tool_id))
    tool = result.scalar_one_or_none()
    if not tool:
        raise HTTPException(status_code=404, detail=f"Tool '{tool_id}' not found")

    # Get or create org permission
    result = await db.execute(
        select(OrganizationToolPermission).where(
            OrganizationToolPermission.tool_id == tool_id
        )
    )
    org_perm = result.scalar_one_or_none()

    if org_perm:
        org_perm.enabled = enabled
    else:
        org_perm = OrganizationToolPermission(tool_id=tool_id, enabled=enabled)
        db.add(org_perm)

    await db.flush()

    logger.info(
        f"Admin {admin.get('sub')} {'enabled' if enabled else 'disabled'} "
        f"tool '{tool.tool_name}' at organization level"
    )

    return {
        "message": f"Tool {'enabled' if enabled else 'disabled'} at organization level",
        "tool_id": tool_id,
        "tool_name": tool.tool_name,
        "enabled": enabled,
    }


@router.post("/organization/tools/bulk-toggle")
async def bulk_toggle_organization_tool_permissions(
    request: BulkToggleRequest,
    admin: dict = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """
    Enable or disable multiple tools at organization level.

    Args:
        request: Bulk toggle request with tool IDs and enabled status
        admin: Current admin user (from JWT)
        db: Database session

    Returns:
        Success message with count

    Raises:
        HTTPException 404: If any tool not found
    """
    # Verify all tools exist
    result = await db.execute(
        select(MCPServerTool).where(MCPServerTool.id.in_(request.tool_ids))
    )
    tools = result.scalars().all()

    if len(tools) != len(request.tool_ids):
        raise HTTPException(status_code=404, detail="One or more tools not found")

    # Update or create permissions
    updated_count = 0
    for tool_id in request.tool_ids:
        result = await db.execute(
            select(OrganizationToolPermission).where(
                OrganizationToolPermission.tool_id == tool_id
            )
        )
        org_perm = result.scalar_one_or_none()

        if org_perm:
            org_perm.enabled = request.enabled
        else:
            org_perm = OrganizationToolPermission(
                tool_id=tool_id, enabled=request.enabled
            )
            db.add(org_perm)

        updated_count += 1

    await db.flush()

    logger.info(
        f"Admin {admin.get('sub')} bulk {'enabled' if request.enabled else 'disabled'} "
        f"{updated_count} tools at organization level"
    )

    return {
        "message": f"{updated_count} tools {'enabled' if request.enabled else 'disabled'}",
        "count": updated_count,
        "enabled": request.enabled,
    }


@router.post("/servers/{server_id}/tools/bulk-update")
async def bulk_update_server_tools(
    server_id: str,
    request: BulkToolUpdateRequest,
    db: AsyncSession = Depends(get_db),
    admin: dict = Depends(require_admin),
):
    """
    Bulk update tool permissions for a specific MCP server.

    Updates the enabled/disabled status for multiple tools at once.
    """
    try:
        updated_count = 0

        for tool_update in request.tools:
            # First, find the actual MCPServerTool by name
            result = await db.execute(
                select(MCPServerTool).where(
                    MCPServerTool.mcp_server_id == server_id,
                    MCPServerTool.tool_name == tool_update.tool_name,
                )
            )
            tool = result.scalar_one_or_none()

            if not tool:
                logger.warning(
                    f"Tool '{tool_update.tool_name}' not found for server '{server_id}', skipping"
                )
                continue

            # Get or create organization tool permission using the tool's UUID
            result = await db.execute(
                select(OrganizationToolPermission).where(
                    OrganizationToolPermission.tool_id == tool.id
                )
            )
            permission = result.scalar_one_or_none()

            if permission:
                # Update existing permission
                permission.enabled = tool_update.is_enabled
                updated_count += 1
            else:
                # Create new permission entry
                new_permission = OrganizationToolPermission(
                    tool_id=tool.id, enabled=tool_update.is_enabled
                )
                db.add(new_permission)
                updated_count += 1

        await db.commit()

        logger.info(
            f"Admin {admin.get('sub')} bulk updated {updated_count} tools for server {server_id}"
        )

        return {
            "message": f"Successfully updated {updated_count} tool permissions",
            "server_id": server_id,
            "count": updated_count,
        }

    except Exception as e:
        logger.error(f"Error bulk updating tools for server {server_id}: {e}")
        await db.rollback()
        raise HTTPException(
            status_code=500, detail=f"Failed to update tool permissions: {str(e)}"
        )

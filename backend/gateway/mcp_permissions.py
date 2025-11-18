"""
MCP Permission Service.

Implements 4-level permission hierarchy for MCP tool access:
1. Organization Server - Is the server enabled for the organization?
2. User Server - Does the user have OAuth access to the server?
3. Organization Tool - Is the tool enabled at the organization level?
4. User Tool - Is the tool enabled for this specific user?
"""
from typing import List, Set
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from gateway.models import (
    UserCredential,
    MCPServerTool,
    OrganizationToolPermission,
    UserToolPermission,
    User
)
import logging

logger = logging.getLogger(__name__)


class MCPPermissionService:
    """Service for checking MCP tool permissions with 4-level hierarchy."""

    @staticmethod
    async def get_user_allowed_tools(
        user_id: str,
        db: AsyncSession
    ) -> Set[str]:
        """
        Get all tools the user is allowed to access based on 4-level hierarchy.

        4-Level Permission Hierarchy:
        1. Organization Server: Server must be enabled for user (UserCredential.is_enabled)
        2. User Server: User must have OAuth access (UserCredential.is_authorized)
        3. Organization Tool: Tool must be enabled org-wide (OrganizationToolPermission.enabled)
        4. User Tool: Tool must be enabled for user (UserToolPermission.enabled)

        A tool is accessible ONLY if ALL 4 levels allow it.

        Args:
            user_id: User's database ID
            db: Database session

        Returns:
            Set[str]: Set of allowed tool names in format "service:tool_name"
                Example: {"github:create_issue", "jira:search_issues"}

        Example:
            >>> allowed_tools = await MCPPermissionService.get_user_allowed_tools(
            ...     user_id="user-123",
            ...     db=db_session
            ... )
            >>> print(allowed_tools)
            {'github:create_issue', 'github:list_repos', 'jira:search_issues'}
        """
        try:
            # Get user's email for UserCredential lookups
            user_result = await db.execute(
                select(User).where(User.id == user_id)
            )
            user = user_result.scalar_one_or_none()
            if not user:
                logger.warning(f"User {user_id} not found")
                return set()

            user_email = user.email

            # Step 1 & 2: Get servers where user has access
            # (is_enabled=True AND is_authorized=True)
            user_servers_result = await db.execute(
                select(UserCredential.server_id)
                .where(UserCredential.user_id == user_email)
                .where(UserCredential.is_enabled == True)
                .where(UserCredential.is_authorized == True)
            )
            authorized_servers = {row[0] for row in user_servers_result.fetchall()}

            if not authorized_servers:
                logger.info(f"User {user_email} has no authorized servers")
                return set()

            logger.debug(f"User {user_email} authorized servers: {authorized_servers}")

            # Step 3: Get all tools from authorized servers
            tools_result = await db.execute(
                select(MCPServerTool)
                .where(MCPServerTool.mcp_server_id.in_(authorized_servers))
            )
            all_tools = tools_result.scalars().all()

            # Step 4: Filter by organization-level permissions
            # Get org tool permissions (default enabled if not specified)
            org_permissions_result = await db.execute(
                select(OrganizationToolPermission)
                .where(OrganizationToolPermission.tool_id.in_([t.id for t in all_tools]))
            )
            org_permissions = {
                perm.tool_id: perm.enabled
                for perm in org_permissions_result.scalars().all()
            }

            # Step 5: Filter by user-level permissions
            # Get user tool permissions (default enabled if not specified)
            user_permissions_result = await db.execute(
                select(UserToolPermission)
                .where(UserToolPermission.user_email == user_email)
                .where(UserToolPermission.tool_id.in_([t.id for t in all_tools]))
            )
            user_permissions = {
                perm.tool_id: perm.enabled
                for perm in user_permissions_result.scalars().all()
            }

            # Combine all filters
            allowed_tools = set()
            for tool in all_tools:
                # Check org-level permission (default True if not set)
                org_enabled = org_permissions.get(tool.id, True)
                if not org_enabled:
                    logger.debug(f"Tool {tool.mcp_server_id}:{tool.tool_name} disabled at org level")
                    continue

                # Check user-level permission (default True if not set)
                user_enabled = user_permissions.get(tool.id, True)
                if not user_enabled:
                    logger.debug(f"Tool {tool.mcp_server_id}:{tool.tool_name} disabled for user {user_email}")
                    continue

                # Tool passed all checks - add to allowed list
                tool_ref = f"{tool.mcp_server_id}:{tool.tool_name}"
                allowed_tools.add(tool_ref)

            logger.info(f"User {user_email} has access to {len(allowed_tools)} tools")
            return allowed_tools

        except Exception as e:
            logger.error(f"Error getting allowed tools for user {user_id}: {e}")
            return set()

    @staticmethod
    async def check_tool_access(
        user_id: str,
        tool_name: str,
        db: AsyncSession
    ) -> bool:
        """
        Check if a user has access to a specific tool.

        Args:
            user_id: User's database ID
            tool_name: Tool name in format "service:tool_name" (e.g., "github:create_issue")
            db: Database session

        Returns:
            bool: True if user has access, False otherwise

        Example:
            >>> has_access = await MCPPermissionService.check_tool_access(
            ...     user_id="user-123",
            ...     tool_name="github:create_issue",
            ...     db=db_session
            ... )
            >>> print(has_access)
            True
        """
        allowed_tools = await MCPPermissionService.get_user_allowed_tools(user_id, db)
        return tool_name in allowed_tools

"""
User-Aware MCP Server.

Wraps the existing FastMCP server with authentication and permission filtering.
Every MCP request must include a JWT Bearer token in the Authorization header.

Uses middleware to authenticate requests and store user context for tool execution.
"""

import logging
import os
import re
import json
from typing import List, Optional
from contextvars import ContextVar
import requests
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from fastmcp import FastMCP
from arka_mcp.utils import parse_tool_file
from arka_mcp.auth_middleware import authenticate_mcp_request
from gateway.mcp_permissions import MCPPermissionService
from database import get_db_session
from config import settings

logger = logging.getLogger(__name__)

# Context variable to store authenticated user info for the current request
current_user_context: ContextVar[Optional[dict]] = ContextVar(
    "current_user", default=None
)

# Create authenticated MCP server
authenticated_mcp_server = FastMCP(
    "arka-mcp-authenticated", strict_input_validation=True
)

# Tool directories (maps server_id to directory name)
# Server IDs must match database MCPServerTool.mcp_server_id (with -mcp suffix)
TOOL_DIRS = {
    "github-mcp": "github_tools",
    "jira-mcp": "jira_tools",
    "notion-mcp": "notion_tools",
    "gmail-mcp": "gmail_tools",
    "gcal-mcp": "gcal_tools",
    "slack-mcp": "slack_tools",
    "filesystem-mcp": "filesystem_tools",
    "supabase-mcp": "supabase_tools",
    "confluence-mcp": "confluence_tools",
}
BASE_DIR = "arka_mcp/servers"
BASE_MCP_SERVER_MODULE = "arka_mcp.servers"


class AuthenticationMiddleware(BaseHTTPMiddleware):
    """
    Middleware to authenticate MCP requests and store user context.

    Extracts JWT from Authorization header, validates it, and stores user info
    in a context variable for tool handlers to access.
    """

    async def dispatch(self, request: Request, call_next):
        """Process request and authenticate user."""
        # Authenticate user for MCP requests (paths starting with /mcp or MCP-specific endpoints)
        # FastMCP creates routes like /mcp, /mcp/messages, /mcp/sse, etc.
        mcp_paths = ["/mcp", "/sse", "/messages"]
        is_mcp_request = any(request.url.path.startswith(path) for path in mcp_paths)

        if is_mcp_request:
            user_info = await authenticate_mcp_request(request)

            if not user_info:
                logger.warning(f"Unauthenticated MCP request: {request.url.path}")
                from starlette.responses import JSONResponse

                return JSONResponse(
                    status_code=401,
                    content={
                        "detail": "Authentication required. Please provide a valid Bearer token."
                    },
                )

            # Store user info in context for tool handlers
            current_user_context.set(user_info)
            logger.debug(
                f"Authenticated user {user_info['email']} for {request.url.path}"
            )

        # Continue processing request
        response = await call_next(request)
        return response


def get_current_user() -> dict:
    """
    Get authenticated user from context.

    Returns:
        dict: User information containing user_id, email, name, token_name

    Raises:
        HTTPException 401: If no authenticated user in context
    """
    user_info = current_user_context.get()
    if not user_info:
        logger.error("No authenticated user in context")
        raise HTTPException(status_code=401, detail="Authentication required")
    return user_info


async def get_user_allowed_tools_cached(user_id: str) -> set:
    """
    Get allowed tools for user from permission service.

    Args:
        user_id: User's database ID

    Returns:
        Set of allowed tool names in format "service:tool_name"
    """
    async with get_db_session() as db:
        allowed_tools = await MCPPermissionService.get_user_allowed_tools(
            user_id=user_id, db=db
        )
        return allowed_tools


@authenticated_mcp_server.tool()
async def list_tools():
    """
    Return all tools the authenticated user has access to.

    Returns tools in format service_name:tool_name, filtered by:
    1. Organization Server permissions (UserCredential.is_enabled)
    2. User Server permissions (UserCredential.is_authorized)
    3. Organization Tool permissions (OrganizationToolPermission.enabled)
    4. User Tool permissions (UserToolPermission.enabled)

    Requires: Authorization header with valid JWT Bearer token
    """
    # Get authenticated user from context
    user_info = get_current_user()
    user_id = user_info["user_id"]
    user_email = user_info["email"]

    logger.info(f"list_tools called by user: {user_email}")

    # Get all available tools (same logic as original server)
    all_available_tools = []
    for service, dir_path in TOOL_DIRS.items():
        path = os.path.join(BASE_DIR, dir_path)
        if not os.path.exists(path):
            continue
        for filename in os.listdir(path):
            if filename.endswith(".py"):
                tool_name = filename[:-3]  # remove .py extension
                all_available_tools.append(f"{service}:{tool_name}")

    logger.debug(f"All available tools: {all_available_tools}")

    # Get user's allowed tools based on 4-level permission hierarchy
    allowed_tools = await get_user_allowed_tools_cached(user_id)

    logger.debug(f"User {user_email} allowed tools: {allowed_tools}")

    # Filter available tools by user permissions
    filtered_tools = [tool for tool in all_available_tools if tool in allowed_tools]

    logger.info(
        f"Returning {len(filtered_tools)}/{len(all_available_tools)} tools "
        f"for user {user_email}"
    )

    return filtered_tools


@authenticated_mcp_server.tool()
async def get_tool_definition(tool_names: List[str]):
    """
    Return the import references and call signatures for one or more tools.

    Only returns definitions for tools the user has permission to access.

    The LLM MUST follow these rules when using the returned information:

    1. The LLM MUST generate code that imports tools EXACTLY using the `tool_ref` value
       returned in the response. Do NOT guess paths or inspect files.

    2. The LLM MUST generate a single async function named `run()` and call the selected tools inside it.

    3. The generated code MUST:
         - Only import the returned tool functions (no additional imports like inspect, os, pathlib).
         - Contain no filesystem reads, no reflection, and no dynamic inspection.
         - Not print or read any source code of the tool modules.

    4. The `run()` function MUST return or print the final result.
       The LLM MUST NOT call run(), schedule it, or wrap in a main guard.
       (No: `await run()`, `run()`, or `if __name__ == "__main__"`)

    Example of correct code the LLM MUST produce:

        from jira_tool.get_issue import get_issue

        async def run():
            result = await get_issue("TEST")
            return result

    Input:
        tool_names: List[str]
            Example:
                ["jira:get_issue"]

    Output:
        A list of dictionaries describing each tool, including:
            - function_name
            - parameters
            - description
            - tool_ref (Python import path to use)

    Requires: Authorization header with valid JWT Bearer token
    """
    # Get authenticated user from context
    user_info = get_current_user()
    user_id = user_info["user_id"]
    user_email = user_info["email"]

    logger.info(
        f"get_tool_definition called by user: {user_email} for tools: {tool_names}"
    )

    # Get user's allowed tools
    allowed_tools = await get_user_allowed_tools_cached(user_id)

    if isinstance(tool_names, str):
        tool_names = [tool_names]

    results = []

    for name in tool_names:
        # Check if user has permission for this tool
        if name not in allowed_tools:
            logger.warning(
                f"User {user_email} attempted to access unauthorized tool: {name}"
            )
            raise HTTPException(
                status_code=403,
                detail=f"Access denied: You do not have permission to access tool '{name}'",
            )

        # Parse service and tool name
        try:
            service, tool = name.split(":")
        except ValueError:
            logger.error(f"Invalid tool name format: {name}")
            raise HTTPException(
                status_code=400,
                detail=f"Invalid tool name format: '{name}'. Expected format: 'service:tool_name'",
            )

        dir_path = TOOL_DIRS.get(service)
        if not dir_path:
            logger.error(f"Unknown service: {service}")
            raise HTTPException(
                status_code=404, detail=f"Service '{service}' not found"
            )

        module_path = f"{BASE_MCP_SERVER_MODULE}.{dir_path}.{tool}"
        info = parse_tool_file(module_path, service, tool)

        if info:
            results.append(info)
        else:
            logger.error(f"Failed to parse tool: {name}")
            raise HTTPException(
                status_code=404, detail=f"Tool '{name}' not found or failed to parse"
            )

    logger.info(f"Returning definitions for {len(results)} tools to user {user_email}")
    return results


@authenticated_mcp_server.tool()
async def run_tool_code(code: str):
    """
    Execute LLM-generated Python code that calls discovered tool functions.

    Validates that the user has permission to access all tools referenced in the code
    before execution.

    STRICT RULES FOR THE LLM WHEN GENERATING CODE:

    1. The code MUST:
        - Only import the tool functions using the `tool_ref` values from get_tool_definition.
        - Define exactly one async function named `run()`.
        - Call the tool functions inside run().
        - Return or print the final result from run().

    2. The code MUST NOT:
        - Import any modules other than the approved tool imports.
        - Read or inspect files, modules, paths, or source code.
        - Use pathlib, os, open(), inspect, importlib, or any reflection utilities.
        - Attempt to modify the environment.

    3. The final submitted code MUST be directly executable as-is. Example:

        from jira_tool.get_issue import get_issue

        async def run():
            result = await get_issue("TEST")
            return result

    4. The `run()` function MUST return or print the final result.
       The LLM MUST NOT call run(), schedule it, or wrap in a main guard.
       (No: `await run()`, `run()`, or `if __name__ == "__main__"`)

    This function will execute the code and return:
        - The return value of run(), OR
        - Any printed stdout, OR
        - An error traceback.

    Requires: Authorization header with valid JWT Bearer token
    """
    # Get authenticated user from context
    user_info = get_current_user()
    user_id = user_info["user_id"]
    user_email = user_info["email"]

    logger.info(f"run_tool_code called by user: {user_email}")
    logger.debug(f"Code to execute:\n{code}")

    # Get user's allowed tools
    allowed_tools = await get_user_allowed_tools_cached(user_id)

    # Parse imports from code to validate permissions
    # Simple regex to find tool imports: from arka_mcp.servers.{service}_tools.{tool} import ...
    import_pattern = r'from\s+arka_mcp\.servers\.(\w+)_tools\.(\w+)\s+import'
    imports = re.findall(import_pattern, code)

    # Create reverse mapping: directory name -> server ID
    # e.g., "gmail_tools" -> "gmail-mcp"
    dir_to_server = {
        dir_name.replace("_tools", ""): server_id
        for server_id, dir_name in TOOL_DIRS.items()
    }

    # Validate each imported tool
    for dir_service, tool in imports:
        # Map directory name back to server ID
        # e.g., "gmail" from "gmail_tools" -> "gmail-mcp"
        server_id = dir_to_server.get(dir_service, dir_service)
        tool_name = f"{server_id}:{tool}"

        if tool_name not in allowed_tools:
            logger.warning(
                f"User {user_email} attempted to execute code with unauthorized tool: {tool_name}"
            )
            raise HTTPException(
                status_code=403,
                detail=f"Access denied: You do not have permission to use tool '{tool_name}'",
            )

    logger.info(f"Permission check passed for user {user_email}. Executing code...")

    # Create encrypted token context for worker
    from gateway.token_context import create_token_context

    async with get_db_session() as db:
        try:
            token_context = await create_token_context(
                user_id=user_id, user_email=user_email, db=db
            )
            logger.debug(f"Created encrypted token context for user {user_email}")
        except Exception as e:
            logger.error(f"Failed to create token context: {e}")
            raise HTTPException(
                status_code=500, detail=f"Failed to prepare execution context: {str(e)}"
            )

    # Execute the code using the code execution service
    try:
        result = requests.post(
            f"{settings.worker_url}/execute",
            json={"code": json.dumps(code), "token_context": token_context},
            timeout=30,
        ).json()

        logger.info(f"Code execution completed for user {user_email}")
        return result

    except requests.exceptions.RequestException as e:
        logger.error(f"Code execution failed for user {user_email}: {e}")
        raise HTTPException(
            status_code=500, detail=f"Code execution service error: {str(e)}"
        )


# Create HTTP app and add authentication middleware
authenticated_mcp_app = authenticated_mcp_server.http_app()
authenticated_mcp_app.add_middleware(AuthenticationMiddleware)

logger.info("Authenticated MCP server initialized with authentication middleware")

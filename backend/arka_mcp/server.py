import os
from typing import List
from fastmcp import FastMCP
from arka_mcp.utils import parse_tool_file
from config import settings


arka_mcp_server = FastMCP("arka-mcp-server", strict_input_validation=True)
TOOL_DIRS = {
    # "confluence": "confluence_tools",
    # "jira": "jira_tools",
    "notion": "notion_tools",
    # "supabase": "supabase_tools",
    # "filesystem": "filesystem_tools",
}
BASE_DIR = "arka_mcp/servers"
BASE_MCP_SERVER_MODULE = "arka_mcp.servers"

arka_mcp_app = arka_mcp_server.http_app()


@arka_mcp_server.tool()
async def list_tools():
    """
    Return all available tools in the format "service_name:tool_name".

    **USAGE RULES FOR LLM**:
    1. Always call this tool FIRST when starting a new task.
       - Use its output to understand which tools are available.
       - Then, call `plan_workflow` to design a high-level plan using these tools.
    2. After planning, execute each step in order using:
       - `get_tool_definition()` to discover specific tool details
       - `call_tool()` to run individual tools
       - `run_tool_code()` for any custom logic or data manipulation
    3. Never attempt to execute tools before creating a plan.
       The correct sequence is:
           list_tools → plan_workflow → get_tool_definition → call_tool/run_tool_code

    **Output Format:**
        [
            "filesystem:list_directory",
            "filesystem:read_text_file",
            "filesystem:write_file",
            ...
        ]
    """
    all_tools = []
    for service, dir_path in TOOL_DIRS.items():
        path = os.path.join(BASE_DIR, dir_path)
        if not os.path.exists(path):
            continue
        for filename in os.listdir(path):
            if filename.endswith(".py"):
                tool_name = filename[:-3]  # remove .py extension
                all_tools.append(f"{service}:{tool_name}")
    return all_tools


@arka_mcp_server.tool
async def get_tool_definition(tool_names: List[str]):
    """
        Return definitions for one or multiple tools.

        **STRICT STEPWISE USAGE RULES FOR LLM**:
        1. Only request the tool definitions for tools needed for the **current step**.
           Do **not** request tools for future steps.
        2. Generate **code for the current step only** using these tools.
        3. Only include imports and calls for the requested tools.
        4. Do **not** pre-plan or combine multiple steps.
        5. After executing this step, the LLM must call `get_tool_definition` again
           for the next step if needed.

        Example:

    <<<<<<< Updated upstream
            from confluence_tools.create_page import create_page
    =======
        2. The LLM MUST generate a single async function named `run()` and call the selected tools inside it.

        3. The generated code MUST:
             - Only import the returned tool functions (no additional imports like inspect, os, pathlib).
             - Contain no filesystem reads, no reflection, and no dynamic inspection.
             - Not print or read any source code of the tool modules.

        4. The `run()` function MUST return or print the final result.
           The LLM MUST NOT call run(), schedule it, or wrap in a main guard.
           (No: `await run()`, `run()`, or `if __name__ == "__main__"`)

        Example of correct code the LLM MUST produce:

            from arka_mcp.servers.jira_tool.get_issue import get_issue
    >>>>>>> Stashed changes

            async def run():
                page = await create_page(title="New Page", content="Hello")
                return {"page": page}

        Input:
            tool_names: List[str]
                Example:
                    ["confluence:create_page"]

        Output:
            List[dict] describing each tool: function_name, decorators, category, and import reference.
    """

    if isinstance(tool_names, str):
        tool_names = [tool_names]
    results = []

    for name in tool_names:
        service, tool = name.split(":")
        dir_path = TOOL_DIRS.get(service)
        if not dir_path:
            continue

        module_path = f"{BASE_MCP_SERVER_MODULE}.{dir_path}.{tool}"
        info = parse_tool_file(module_path, service, tool)
        if info:
            results.append(info)

    return results


@arka_mcp_server.tool
async def call_tool(tool_name: str, args: dict):
    """
        Call a single MCP tool through the local code execution service.

        This tool allows executing exactly **one atomic MCP tool call** via the
        executor backend (http://localhost:8001/execute).

        **USAGE RULES FOR LLM**:
        1. Use this to execute exactly one tool per call.
        2. `tool_name` must be in the format "service:tool" (e.g., "filesystem:list_files").
        3. Provide tool arguments as a JSON object via `args`.
        4. Do **not** combine multiple tools or logic here — chain multiple calls instead.
        5. Use `run_tool_code` for additional data processing or custom logic.

        Example:

    <<<<<<< Updated upstream
            result = await call_tool(
                tool_name="filesystem:list_files",
                args={"path": "/data"}
            )
            return {"files": result}
    =======
        3. The final submitted code MUST be directly executable as-is. Example:

            from arka_mcp.servers.jira_tool.get_issue import get_issue

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
    >>>>>>> Stashed changes
    """

    import requests
    import json

    if not isinstance(tool_name, str) or ":" not in tool_name:
        raise ValueError("tool_name must be a string like 'service:tool'")

    if not isinstance(args, dict):
        raise ValueError("args must be a dictionary of parameters")

    service, tool = tool_name.split(":")
    dir_path = TOOL_DIRS.get(service)
    if not dir_path:
        raise ValueError(f"Unknown service: {service}")

    module_path = f"{BASE_MCP_SERVER_MODULE}.{dir_path}.{tool}"

    # Safely serialize arguments into Python code
    args_str = ", ".join(f"{k}={repr(v)}" for k, v in args.items())

    code = f"""
from {module_path} import {tool}

async def run():
    result = await {tool}({args_str})
    return result
"""

    print(f"[call_tool] Executing {tool_name} with args: {args}")
    print(code)

    # Execute code using the same backend as run_tool_code
    response = requests.post(
        f"{settings.worker_url}/execute",
        json={"code": json.dumps(code)},
    )

    try:
        result = response.json()
    except Exception:
        result = {"error": "Invalid JSON from executor", "raw": response.text}

    return result


@arka_mcp_server.tool
async def run_tool_code(code: str):
    """
    Execute custom Python code generated by the LLM for data transformation,
    composition, or light post-processing between tool calls.

    **STRICT USAGE RULES FOR LLM**:
    1. Use this only for manipulating data, combining results, or light logic
       between tool calls.
    2. Do not directly call raw MCP tools here — use `call_tool` for that.
    3. The code must define an async `run()` function.
    4. Return the result of `await run()`.
    5. Each call to this endpoint corresponds to one logical "step".

    Example:

        async def run():
            data = {"a": 1, "b": 2}
            data["sum"] = data["a"] + data["b"]
            return data
    """

    import requests
    import json

    print("Executing custom code:")
    print(code)

    result = requests.post(
        f"{settings.worker_url}/execute", json={"code": json.dumps(code)}
    ).json()

    return result


# @arka_mcp_server.tool
# async def run_tool_code(code: str):
#     """
#     Execute Python code generated by the LLM that uses previously discovered tool functions.

#     **STRICT USAGE RULES FOR LLM**:
#     1. Only include code for the current step, do **not pre-plan future steps**.
#     2. The code must define an async `run()` function and any helper functions if needed.
#     3. Do **not** include imports or code unrelated to the tools discovered via `get_tool_definition`.
#     4. Return the result of `await run()` or print statements inside run().
#     5. LLM **must generate new code** for the next step only after receiving output from this step.

#     Example correct code:

#         from jira_tools.get_issue import get_issue

#         async def run():
#             issue = await get_issue(issue_id="ABC-123")
#             return {"issue": issue}

#     Runtime will execute it using:

#         result = await run()   # or via asyncio in subprocess
#     """

#     # Capture stdout
#     import requests
#     import json

#     print(code)

#     result = requests.post(
#         "http://localhost:8001/execute", json={"code": json.dumps(code)}
#     ).json()

#     return result

import importlib
import inspect


def parse_tool_file(module_name: str, service: str, tool: str):
    """
    Dynamically imports the tool function and extracts structured metadata.

    Returns None if the module or function does not exist.

    Output format:
    {
        "tool_ref": "jira_tools.search_issues",
        "function_name": "search_issues",
        "signature": "(jql: str, max_results: int = 20, fields: list[str] | None = None)",
        "docstring": "...",
        "return_type": "dict",
        "decorators": [],   # best effort
        "category": "jira"
    }
    """

    try:
        module = importlib.import_module(module_name)
        func = getattr(module, tool)
    except (ModuleNotFoundError, AttributeError):
        return None

    # Signature string
    signature = str(inspect.signature(func))

    # Docstring
    docstring = inspect.getdoc(func)

    # Return type
    sig = inspect.signature(func)
    return_type = None
    if sig.return_annotation is not inspect.Signature.empty:
        return_type = sig.return_annotation

    # Decorators (best-effort; requires `@wraps` usage to be visible)
    decorators = []
    if hasattr(func, "__wrapped__"):
        decorators.append(func.__wrapped__.__name__)

    return {
        "tool_ref": module_name,
        "function_name": func.__name__,
        "signature": signature,
        "docstring": docstring,
        "return_type": str(return_type) if return_type else None,
        "decorators": decorators,
        "category": service,
    }

"""
Permanently clears all completed tasks from a specified Google Tasks list.

Google Tasks API Reference:
https://developers.google.com/tasks/reference/rest/v1/tasklists/clear
"""
from .client import TasksAPIClient


async def clear_tasks(
    tasklist: str
) -> dict:
    """
    Permanently clears completed tasks from the given task list (destructive, idempotent).

    Args:
        tasklist: Identifier of the task list (e.g., '@default').

    Returns:
        Dict indicating status of the clear operation.

    Example:
        result = await clear_tasks('@default')
    """
    client = TasksAPIClient()
    endpoint = f"/lists/{tasklist}/clear"
    # API returns HTTP 204 with empty body on success
    response = await client.post(endpoint, json_data={})
    return {'status': 'success'}

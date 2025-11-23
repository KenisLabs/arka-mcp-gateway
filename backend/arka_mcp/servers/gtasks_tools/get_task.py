"""
Retrieves a specific Google Task by ID from a given task list.

Google Tasks API Reference:
https://developers.google.com/tasks/reference/rest/v1/tasks/get
"""
from .client import TasksAPIClient


async def get_task(
    tasklist_id: str,
    task_id: str
) -> dict:
    """
    Retrieves a specific task from a task list.

    Args:
        tasklist_id: Identifier of the task list.
        task_id: Identifier of the task to retrieve.

    Returns:
        Dict representing the task resource.

    Example:
        task = await get_task(list_id, task_id)
    """
    client = TasksAPIClient()
    endpoint = f"/lists/{tasklist_id}/tasks/{task_id}"
    return await client.get(endpoint)

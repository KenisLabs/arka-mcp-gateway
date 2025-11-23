"""
Retrieves a specific task list from the authenticated user's Google Tasks.

Google Tasks API Reference:
https://developers.google.com/tasks/reference/rest/v1/tasklists/get
"""

from .client import TasksAPIClient


async def get_task_list(tasklist_id: str) -> dict:
    """
    Retrieves a specific task list for the authenticated user.

    Args:
        tasklist_id: The unique identifier of the task list to retrieve.

    Returns:
        Dict containing the task list details as returned by the API.

    Example:
        result = await get_task_list("7f574d94-ae28-4f2e-a69a-fb37978ec62e")
    """
    client = TasksAPIClient()

    endpoint = f"/users/@me/lists/{tasklist_id}"

    return await client.get(endpoint)

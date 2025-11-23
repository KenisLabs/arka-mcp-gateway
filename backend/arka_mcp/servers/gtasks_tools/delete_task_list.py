"""
Permanently deletes an existing Google Tasks list and all its tasks.

Google Tasks API Reference:
https://developers.google.com/tasks/reference/rest/v1/tasklists/delete
"""

from .client import TasksAPIClient


async def delete_task_list(tasklist_id: str) -> dict:
    """
    Deletes a task list and all contained tasks.

    Args:
        tasklist_id: Identifier of the task list to delete.

    Returns:
        Dict indicating success of deletion.

    Example:
        success = await delete_task_list(list_id)
    """
    client = TasksAPIClient()
    endpoint = f"/users/@me/lists/{tasklist_id}"
    await client.delete(endpoint)
    return {'status': 'success'}

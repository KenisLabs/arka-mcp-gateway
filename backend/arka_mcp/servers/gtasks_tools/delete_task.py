"""
Deletes a specified task from a given task list in Google Tasks.

Google Tasks API Reference:
https://developers.google.com/tasks/reference/rest/v1/tasks/delete
"""
from .client import TasksAPIClient


async def delete_task(
    tasklist_id: str,
    task_id: str
) -> dict:
    """
    Deletes a task from the specified task list.

    Args:
        tasklist_id: Identifier of the task list.
        task_id: Identifier of the task to delete.

    Returns:
        Dict indicating success of deletion.

    Example:
        success = await delete_task(list_id, task_id)
    """
    client = TasksAPIClient()
    endpoint = f"/lists/{tasklist_id}/tasks/{task_id}"
    # HTTP 204 on success
    await client.delete(endpoint)
    return {'status': 'success'}

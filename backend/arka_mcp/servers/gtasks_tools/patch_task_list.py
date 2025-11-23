"""
Updates the title of an existing task list.

Google Tasks API Reference:
https://developers.google.com/tasks/reference/rest/v1/tasklists/patch
"""

from .client import TasksAPIClient


async def patch_task_list(tasklist_id: str, updated_title: str) -> dict:
    """
    Partially updates a task list's title.

    Args:
        tasklist_id: Identifier of the task list.
        updated_title: New title for the list.

    Returns:
        Dict representing the updated task list.

    Example:
        updated = await patch_task_list(list_id, 'New Title')
    """
    client = TasksAPIClient()
    endpoint = f"/users/@me/lists/{tasklist_id}"
    json_data = {'title': updated_title}
    return await client.patch(endpoint, json_data=json_data)

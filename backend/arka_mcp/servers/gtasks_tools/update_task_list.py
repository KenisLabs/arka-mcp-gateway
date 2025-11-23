"""
Updates a task list's title, replacing the resource.

Google Tasks API Reference:
https://developers.google.com/tasks/reference/rest/v1/tasklists/update
"""

from .client import TasksAPIClient


async def update_task_list(tasklist_id: str, title: str) -> dict:
    """
    Fully updates a task list's title.

    Args:
        tasklist_id: Identifier of the task list.
        title: New title for the list.

    Returns:
        Dict representing the updated task list.

    Example:
        updated = await update_task_list(list_id, 'New List')
    """
    client = TasksAPIClient()
    endpoint = f"/users/@me/lists/{tasklist_id}"
    json_data = {'title': title}
    # Use PATCH for full update here
    return await client.patch(endpoint, json_data=json_data)

"""
Creates a new task list with the specified title.

Google Tasks API Reference:
https://developers.google.com/tasks/reference/rest/v1/tasklists/insert
"""
from .client import TasksAPIClient


async def create_task_list(
    tasklist_title: str
) -> dict:
    """
    Creates a new Google Tasks list.

    Args:
        tasklist_title: Title for the new task list.

    Returns:
        Dict representing the created task list resource.

    Example:
        new_list = await create_task_list('Grocery Shopping')
    """
    client = TasksAPIClient()
    endpoint = "/users/@me/lists"
    json_data = {'title': tasklist_title}
    return await client.post(endpoint, json_data=json_data)

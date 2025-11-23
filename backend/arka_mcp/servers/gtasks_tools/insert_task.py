"""
Creates a new task in a specified Google Tasks list, optionally nested or ordered.

Google Tasks API Reference:
https://developers.google.com/tasks/reference/rest/v1/tasks/insert
"""
from typing import Optional, Dict, Any
from .client import TasksAPIClient


async def insert_task(
    tasklist_id: str,
    title: str,
    status: str = "needsAction",
    notes: Optional[str] = None,
    due: Optional[str] = None,
    completed: Optional[str] = None,
    task_parent: Optional[str] = None,
    task_previous: Optional[str] = None
) -> dict:
    """
    Inserts a new task into the specified task list.

    Args:
        tasklist_id: Identifier of the task list.
        title: Title of the task.
        status: Task status ('needsAction' or 'completed').
        notes: Optional task details.
        due: Optional due date (RFC3339 or human-readable).
        completed: Optional completion timestamp.
        task_parent: Optional parent task ID for subtasks.
        task_previous: Optional previous sibling task ID.

    Returns:
        Dict representing the created task resource.

    Example:
        task = await insert_task(list_id, 'Buy milk')
    """
    client = TasksAPIClient()
    endpoint = f"/lists/{tasklist_id}/tasks"
    json_data: Dict[str, Any] = {'title': title, 'status': status}
    if notes is not None:
        json_data['notes'] = notes
    if due is not None:
        json_data['due'] = due
    if completed is not None:
        json_data['completed'] = completed
    if task_parent is not None:
        json_data['parent'] = task_parent
    if task_previous is not None:
        json_data['previous'] = task_previous
    return await client.post(endpoint, json_data=json_data)

"""
Updates a task, replacing all fields if provided.

Google Tasks API Reference:
https://developers.google.com/tasks/reference/rest/v1/tasks/update
"""
from typing import Optional, Dict, Any
from .client import TasksAPIClient


async def update_task(
    tasklist_id: str,
    task_id: str,
    title: Optional[str] = None,
    notes: Optional[str] = None,
    due: Optional[str] = None,
    completed: Optional[str] = None,
    status: Optional[str] = None
) -> dict:
    """
    Fully updates a task's properties.

    Args:
        tasklist_id: Identifier of the task list.
        task_id: Identifier of the task.
        title: New title.
        notes: New notes.
        due: New due date.
        completed: New completed timestamp.
        status: New status.

    Returns:
        Dict representing the updated task.

    Example:
        result = await update_task(list_id, task_id, title='New')
    """
    client = TasksAPIClient()
    endpoint = f"/lists/{tasklist_id}/tasks/{task_id}"
    json_data: Dict[str, Any] = {}
    if title is not None:
        json_data['title'] = title
    if notes is not None:
        json_data['notes'] = notes
    if due is not None:
        json_data['due'] = due
    if completed is not None:
        json_data['completed'] = completed
    if status is not None:
        json_data['status'] = status
    # Use PATCH for full update here
    return await client.patch(endpoint, json_data=json_data)

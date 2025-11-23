"""
Partially updates an existing task's attributes.

Google Tasks API Reference:
https://developers.google.com/tasks/reference/rest/v1/tasks/patch
"""

from typing import Optional, Dict, Any
from .client import TasksAPIClient


async def patch_task(
    tasklist_id: str,
    task_id: str,
    title: Optional[str] = None,
    notes: Optional[str] = None,
    due: Optional[str] = None,
    completed: Optional[str] = None,
    status: Optional[str] = None,
) -> dict:
    """
    Partially updates fields of an existing task.

    Args:
        tasklist_id: Task list identifier.
        task_id: Task identifier.
        title: New title.
        notes: New notes.
        due: New due date.
        completed: New completed timestamp.
        status: New status ('needsAction' or 'completed').

    Returns:
        Dict representing the updated task.

    Example:
        updated = await patch_task(list_id, task_id, status='completed')
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
    return await client.patch(endpoint, json_data=json_data)

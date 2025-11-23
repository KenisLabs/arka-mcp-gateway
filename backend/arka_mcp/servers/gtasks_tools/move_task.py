"""
Moves a specified task to another position or list within Google Tasks.

Google Tasks API Reference:
https://developers.google.com/tasks/reference/rest/v1/tasks/move
"""
from typing import Optional, Dict, Any
from .client import TasksAPIClient


async def move_task(
    tasklist: str,
    task: str,
    destination_tasklist: Optional[str] = None,
    parent: Optional[str] = None,
    previous: Optional[str] = None
) -> dict:
    """
    Moves a task to a new list or position.

    Args:
        tasklist: Source task list ID.
        task: Task ID to move.
        destination_tasklist: Optional destination list ID.
        parent: Optional new parent task ID.
        previous: Optional previous sibling task ID.

    Returns:
        Dict representing the moved task resource.

    Example:
        moved = await move_task(list_id, task_id, previous=prev_id)
    """
    client = TasksAPIClient()
    endpoint = f"/lists/{tasklist}/tasks/{task}/move"
    params: Dict[str, Any] = {}
    if destination_tasklist:
        params['destination'] = destination_tasklist
    if parent:
        params['parent'] = parent
    if previous:
        params['previous'] = previous
    return await client.post(endpoint, json_data={}, params=params)

"""
Retrieves tasks from a Google Tasks list with optional filters and pagination.

Google Tasks API Reference:
https://developers.google.com/tasks/reference/rest/v1/tasks/list
"""
from typing import Optional, Dict, Any
from .client import TasksAPIClient


async def list_tasks(
    tasklist_id: str,
    max_results: int = 20,
    page_token: Optional[str] = None,
    show_completed: bool = True,
    show_deleted: bool = False,
    show_hidden: bool = False,
    updated_min: Optional[str] = None,
    due_min: Optional[str] = None,
    due_max: Optional[str] = None,
    completed_min: Optional[str] = None,
    completed_max: Optional[str] = None
) -> dict:
    """
    Retrieves tasks from the specified task list.

    Args:
        tasklist_id: Identifier of the task list (e.g., '@default').
        max_results: Maximum tasks per page.
        page_token: Pagination token.
        show_completed: Include completed tasks.
        show_deleted: Include deleted tasks.
        show_hidden: Include hidden tasks.
        updated_min: Lower bound on modification time.
        due_min: Exclude tasks due before this date.
        due_max: Exclude tasks due after this date.
        completed_min: Exclude tasks completed before this date.
        completed_max: Exclude tasks completed after this date.

    Returns:
        Dict with 'items' and 'nextPageToken'.

    Example:
        result = await list_tasks('@default', max_results=50)
    """
    client = TasksAPIClient()
    params: Dict[str, Any] = {'maxResults': max_results,
                              'showCompleted': show_completed,
                              'showDeleted': show_deleted,
                              'showHidden': show_hidden}
    if page_token:
        params['pageToken'] = page_token
    if updated_min:
        params['updatedMin'] = updated_min
    if due_min:
        params['dueMin'] = due_min
    if due_max:
        params['dueMax'] = due_max
    if completed_min:
        params['completedMin'] = completed_min
    if completed_max:
        params['completedMax'] = completed_max
    endpoint = f"/lists/{tasklist_id}/tasks"
    return await client.get(endpoint, params=params)

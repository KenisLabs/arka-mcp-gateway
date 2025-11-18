from typing import Dict, Any


async def get_user(user_id: str) -> Dict[str, Any]:
    """
    Retrieve information about a specific user in the workspace.

    This function calls the Notion API endpoint for a given user ID to look up that
    user's profile data. The user may be a person or a bot. The level of detail
    returned depends on the integration’s permissions.
    """
    pass

from typing import Dict, Any


async def list_projects() -> Dict[str, Any]:
    """
    Retrieve a list of all Supabase projects.

    This function uses the Supabase client to call the management API endpoint
    `/v1/projects` and returns a dictionary containing either the project data
    or an error message.
    """
    pass

from typing import Any

async def list_all_database_branches(ref: str) -> Any:
    """
    Lists all database branches for a specified Supabase project.

    Args:
        ref: The unique reference ID of the Supabase project.

    Returns:
        Parsed JSON response containing a list of database branch objects.

    Example:
        result = await list_all_database_branches(
            ref="projectref_0123456789abcdef"
        )
        # result might be:
        # {"data": [{"id": "br_123", "name": "main", ...}], "error": null, "successful": true}
    """
    from .client import SupabaseAPIClient

    client = SupabaseAPIClient()
    # Call Supabase management API to list branches
    return await client.get(f"/projects/{ref}/branches")

from typing import Dict, Any, Optional, List


async def create_database_item(
    database_id: str,
    properties: Dict[str, Any],
    children: Optional[List[Dict[str, Any]]] = None,
    icon: Optional[Dict[str, Any]] = None,
    cover: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Create a new page in a Notion database (data source).

    This function uses the Notion Pages API to insert a page strictly under a database.
    The `properties` argument must match the schema of the target database. Optional
    `children` can be included to populate the page with block content at creation time.
    Optional `icon` and `cover` objects can be used to customize the page appearance
    in Notion.

    Returns the newly created page object as returned by the Notion API.

    Notes:
    - This function is intended only for creating pages under a database (data source).
      Creating pages under another page or non-database parent is not supported.
    - Some database properties such as `rollup`, `created_by`, `created_time`,
      `last_edited_by`, and `last_edited_time` cannot be set via the API.
    - The integration must have permission to insert content into the specified database.
    """

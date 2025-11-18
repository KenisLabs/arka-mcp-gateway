from typing import Dict, Any, Optional, List


async def create_database(
    parent: Dict[str, Any],
    title: List[Dict[str, Any]],
    properties: Dict[str, Any],
    icon: Optional[Dict[str, Any]] = None,
    cover: Optional[Dict[str, Any]] = None,
    description: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    """
    Create a new database in Notion as a subpage under a parent page or workspace.

    This function creates a new database with an initial data source, title,
    and property schema. The parent must be either a Notion page (`page_id`)
    or the workspace. If the parent page does not exist or the integration
    lacks access, the API will return an error.

    Key points:
    - `parent`: Specifies where the database is created. Must include the type
      (`page_id` or `workspace`) and appropriate identifier.
    - `title`: The display title of the new database.
    - `properties`: Defines the initial schema of the database's data source,
      including property types such as `title`, `number`, `select`, `multi_select`,
      `relation`, `rollup`, etc. Some property types like `status` are currently
      not supported at creation.
    - Optional `icon` and `cover` can customize the database appearance.
    - Optional `description` allows adding rich-text metadata for the database.
    - The function ensures compatibility with Notion API version `2025-09-03` or later.
    - Integration must have insert content capability; otherwise, a 403 error is returned.
    - The created database includes its first table view and initial data source.
      Additional data sources can be added via the Create Data Source API.
    """

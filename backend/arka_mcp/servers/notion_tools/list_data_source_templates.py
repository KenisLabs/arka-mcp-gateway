"""
List Data Source Templates tool for Notion MCP server.

Lists available data source templates in the workspace.
"""
from typing import Dict, Any, Optional
from .client import NotionAPIClient
import logging

logger = logging.getLogger(__name__)


async def list_data_source_templates(
    page_size: Optional[int] = None,
    start_cursor: Optional[str] = None,
) -> Dict[str, Any]:
    """
    List available data source templates in the Notion workspace.

    Data source templates are predefined structures for data sources in newer
    Notion API versions (2025-09-03+). This tool attempts to list templates
    if available.

    Note: Data source templates are part of Notion API v2025-09-03. This tool
    may not work with older API versions (like 2022-06-28) and will return an
    error or empty list.

    Args:
        page_size: Optional number of templates to return per page (max 100)
                   Example: 50
        start_cursor: Optional cursor for pagination
                      Example: "7c6b1c95-de50-45ca-94e6-af1d9fd295ab"

    Returns:
        Paginated list of data source templates

    Example:
        # List all templates
        templates = await list_data_source_templates()

        # Access template information
        for template in templates.get("results", []):
            template_id = template.get("id", "")
            name = template.get("name", "")
            description = template.get("description", "")

        # List with pagination
        templates = await list_data_source_templates(
            page_size=25
        )

        # Get next page
        templates = await list_data_source_templates(
            start_cursor=templates["next_cursor"]
        )
    """
    try:
        client = NotionAPIClient()

        # Build query params
        params = {}

        if page_size:
            params["page_size"] = min(page_size, 100)

        if start_cursor:
            params["start_cursor"] = start_cursor

        # List data source templates
        # Note: This endpoint may not exist in API version 2022-06-28
        try:
            response = await client.get("/data_source_templates", params if params else None)
            return response
        except Exception as endpoint_error:
            logger.warning(f"Data source templates endpoint not available: {endpoint_error}")
            return {
                "results": [],
                "has_more": False,
                "message": "Data source templates are not available in this Notion API version. Requires API version 2025-09-03 or later."
            }

    except Exception as e:
        logger.error(f"Failed to list data source templates: {e}")
        return {
            "error": f"Failed to list data source templates: {str(e)}"
        }

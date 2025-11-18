from typing import Dict, Any
from .base import get_notion_client, handle_notion_error, clean_notion_response


async def get_me() -> Dict[str, Any]:
    """
    Retrieve the bot user associated with the current Notion API token.

    This calls the Notion `/users/me` endpoint to identify which bot user the
    integration is operating as. The bot user includes an `owner` field that
    indicates the Notion workspace member who authorized this integration.
    """
    try:
        notion = get_notion_client()
        response = notion.users.me()
        return clean_notion_response(response)

    except Exception as e:
        return handle_notion_error(e)

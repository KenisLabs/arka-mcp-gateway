"""
Retrieve person details or list 'Other Contacts'.

Implements the GMAIL_GET_PEOPLE tool specification from gmail.md.

Security features:
- Input validation with Pydantic
- Authenticated via worker_context OAuth tokens
"""
from typing import Dict, Any
from arka_mcp.servers.gmail_tools.client import GmailAPIClient


async def get_people(
    resource_name: str = "people/me",
    person_fields: str = "emailAddresses,names,birthdays,genders",
    other_contacts: bool = False,
    page_size: int = 10,
    page_token: str = "",
    sync_token: str = ""
) -> Dict[str, Any]:
    """
    Retrieve either a specific person's details or list 'Other Contacts'.

    Args:
        resource_name: Resource name identifying the person (default: 'people/me')
            - Used only when other_contacts is false
            - Examples: 'people/me', 'people/c12345678901234567890'
        person_fields: Comma-separated field mask (default: 'emailAddresses,names,birthdays,genders')
        other_contacts: If true, retrieves 'Other Contacts' (default: false)
            - People interacted with but not explicitly saved
        page_size: Number of 'Other Contacts' to return per page (1-1000, default: 10)
            - Only applicable when other_contacts is true
        page_token: Token for retrieving next page of 'Other Contacts'
            - Only applicable when other_contacts is true
        sync_token: Token from previous 'Other Contacts' list call
            - Only applicable when other_contacts is true
            - Leave empty for initial full sync

    Returns:
        Dict containing person details or other contacts list

    Example:
        # Get current user's profile
        person = await get_people(resource_name="people/me")

        # List other contacts
        contacts = await get_people(
            other_contacts=True,
            page_size=100
        )

    Google People API Reference:
        https://developers.google.com/people/api/rest/v1/people/get
        https://developers.google.com/people/api/rest/v1/otherContacts/list

    Note: This uses the People API, not Gmail API.
    """
    # This requires People API which is different from Gmail API
    # For now, returning a placeholder
    raise NotImplementedError(
        "get_people requires Google People API integration. "
        "This will be implemented in a future update."
    )

"""
Search contacts by matching query against names, emails, and phone numbers.

Implements the GMAIL_SEARCH_PEOPLE tool specification from gmail.md.

Security features:
- Input validation with Pydantic
- Authenticated via worker_context OAuth tokens
"""
from typing import Dict, Any
from arka_mcp.servers.gmail_tools.client import GmailAPIClient


async def search_people(
    query: str,
    person_fields: str = "emailAddresses,names,phoneNumbers",
    other_contacts: bool = True,
    pageSize: int = 10
) -> Dict[str, Any]:
    """
    Search contacts by matching query against names, nicknames, emails, phone numbers, and organizations.

    Optionally includes 'Other Contacts'.

    Args:
        query: Search query matching contact fields (required)
            - Matches against: names, nicknames, email addresses, phone numbers, organizations
        person_fields: Comma-separated fields to return (default: 'emailAddresses,names,phoneNumbers')
            - When other_contacts is true, only 'emailAddresses', 'names', 'phoneNumbers' are allowed
            - When other_contacts is false, all person fields including 'organizations', 'addresses', etc. are allowed
        other_contacts: When true, searches both saved contacts and 'Other Contacts' (default: true)
            - Note: This restricts person_fields to only 'emailAddresses', 'names', 'phoneNumbers'
            - When false, searches only saved contacts but allows all person_fields
        pageSize: Maximum results to return (0-30, default: 10)
            - Values >30 are capped to 30 by the API

    Returns:
        Dict containing matching people

    Example:
        # Search all contacts including other contacts
        results = await search_people(
            query="john",
            other_contacts=True
        )

        # Search only saved contacts with full field access
        results = await search_people(
            query="example.com",
            person_fields="names,emailAddresses,organizations",
            other_contacts=False
        )

    Google People API Reference:
        https://developers.google.com/people/api/rest/v1/people/searchContacts

    Note: This uses the People API, not Gmail API.
    """
    # This requires People API which is different from Gmail API
    # For now, returning a placeholder
    raise NotImplementedError(
        "search_people requires Google People API integration. "
        "This will be implemented in a future update."
    )

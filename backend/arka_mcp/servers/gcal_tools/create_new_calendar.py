"""
Creates a new, empty Google Calendar with the specified title (summary).

Google Calendar API Reference:
https://developers.google.com/calendar/api/v3/reference/calendars/insert
"""
from .client import CalendarAPIClient


async def create_new_calendar(
    summary: str
) -> dict:
    """
    Creates a new, empty Google Calendar with the specified title (summary).

    Args:
        summary: Title for the new Google Calendar to be created. Required and must be a non-empty string.

    Returns:
        Dict containing the API response

    Example:
        result = await create_new_calendar(...)
    """
    client = CalendarAPIClient()

    endpoint = "/calendars"

    request_body = {}
    if summary is not None:
        request_body["summary"] = summary

    return await client.post(endpoint, json_data=request_body)

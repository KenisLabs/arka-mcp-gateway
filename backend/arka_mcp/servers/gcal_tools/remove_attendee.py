"""
Removes an attendee from a specified event in a Google Calendar.

This requires fetching the event, removing the attendee from the list,
and patching the event back.

Google Calendar API Reference:
https://developers.google.com/calendar/api/v3/reference/events/patch
"""
from typing import Optional, Dict, Any
from .client import CalendarAPIClient


async def remove_attendee(
    event_id: str,
    attendee_email: str,
    calendar_id: str = "primary",
    sendUpdates: str = "all"
) -> Dict[str, Any]:
    """
    Removes an attendee from a specified event in a Google Calendar.

    This function:
    1. Fetches the current event
    2. Removes the specified attendee from the attendees list
    3. Patches the event with the updated attendees list

    Args:
        event_id: Unique identifier of the event
        attendee_email: Email address of the attendee to remove
        calendar_id: Calendar identifier (default: "primary")
        sendUpdates: Whether to send notifications ("all", "externalOnly", "none")

    Returns:
        Dict containing the updated event

    Example:
        result = await remove_attendee(
            event_id="event123",
            attendee_email="colleague@example.com",
            calendar_id="primary"
        )

    API Reference:
        https://developers.google.com/calendar/api/v3/reference/events/patch
    """
    client = CalendarAPIClient()

    # First, fetch the current event
    event = await client.get(f"/calendars/{calendar_id}/events/{event_id}")

    # Get current attendees list
    attendees = event.get("attendees", [])

    # Filter out the attendee to remove
    updated_attendees = [
        att for att in attendees
        if att.get("email", "").lower() != attendee_email.lower()
    ]

    # If no change, return current event
    if len(updated_attendees) == len(attendees):
        return event

    # Patch the event with updated attendees
    params = {}
    if sendUpdates:
        params["sendUpdates"] = sendUpdates

    return await client.patch(
        f"/calendars/{calendar_id}/events/{event_id}",
        json_data={"attendees": updated_attendees},
        params=params
    )

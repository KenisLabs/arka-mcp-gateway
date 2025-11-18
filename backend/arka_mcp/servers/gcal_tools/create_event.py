"""
Create a Google Calendar event.

Google Calendar API Reference:
https://developers.google.com/calendar/api/v3/reference/events/insert
"""
from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta
from .client import CalendarAPIClient


async def create_event(
    start_datetime: str,
    calendar_id: str = "primary",
    summary: Optional[str] = None,
    description: Optional[str] = None,
    location: Optional[str] = None,
    timezone: Optional[str] = None,
    event_duration_hour: int = 0,
    event_duration_minutes: int = 30,
    attendees: Optional[List[str]] = None,
    recurrence: Optional[List[str]] = None,
    transparency: str = "opaque",
    visibility: str = "default",
    guestsCanModify: bool = False,
    guestsCanInviteOthers: Optional[bool] = None,
    guestsCanSeeOtherGuests: Optional[bool] = None,
    sendUpdates: str = "all",
    conferenceData: Optional[Dict[str, Any]] = None,
    reminders: Optional[Dict[str, Any]] = None,
    colorId: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create a new event in a Google Calendar.

    Args:
        start_datetime: Start time in ISO 8601 format (e.g., "2025-01-16T13:00:00")
        calendar_id: Calendar identifier (default: "primary")
        summary: Event title/summary
        description: Event description (can contain HTML)
        location: Geographic location as free-form text
        timezone: IANA timezone (e.g., "America/New_York"). Required for all-day events.
        event_duration_hour: Duration in hours (0-24)
        event_duration_minutes: Duration in minutes (0-59)
        attendees: List of attendee email addresses
        recurrence: List of RRULE, EXRULE, RDATE, EXDATE lines for recurring events
        transparency: "opaque" (busy) or "transparent" (available)
        visibility: "default", "public", "private", or "confidential"
        guestsCanModify: Whether guests can modify the event
        guestsCanInviteOthers: Whether guests can invite others
        guestsCanSeeOtherGuests: Whether guests can see other guests
        sendUpdates: "all", "externalOnly", or "none"
        conferenceData: Conference data (e.g., Google Meet)
        reminders: Reminder overrides
        colorId: Color ID (1-11)

    Returns:
        Created event details

    Example:
        result = await create_event(
            summary="Team Meeting",
            start_datetime="2024-01-15T10:00:00",
            timezone="America/Los_Angeles",
            event_duration_hour=1,
            attendees=["colleague@example.com"]
        )

    API Reference:
        https://developers.google.com/calendar/api/v3/reference/events/insert
    """
    client = CalendarAPIClient()

    # Parse start datetime and calculate end datetime
    try:
        start_dt = datetime.fromisoformat(start_datetime.replace('Z', '+00:00'))
    except ValueError:
        # If no timezone info, treat as naive
        start_dt = datetime.fromisoformat(start_datetime)

    # Calculate end time
    duration = timedelta(hours=event_duration_hour, minutes=event_duration_minutes)
    end_dt = start_dt + duration

    # Build event body according to Google Calendar API spec
    event_body: Dict[str, Any] = {}

    # Summary
    if summary:
        event_body["summary"] = summary

    # Description
    if description:
        event_body["description"] = description

    # Location
    if location:
        event_body["location"] = location

    # Start time (required structure: {dateTime, timeZone})
    start_obj: Dict[str, str] = {
        "dateTime": start_dt.isoformat()
    }
    if timezone:
        start_obj["timeZone"] = timezone
    event_body["start"] = start_obj

    # End time (required structure: {dateTime, timeZone})
    end_obj: Dict[str, str] = {
        "dateTime": end_dt.isoformat()
    }
    if timezone:
        end_obj["timeZone"] = timezone
    event_body["end"] = end_obj

    # Attendees (must be array of objects with 'email' field)
    if attendees:
        event_body["attendees"] = [{"email": email} for email in attendees]

    # Recurrence
    if recurrence:
        event_body["recurrence"] = recurrence

    # Transparency
    event_body["transparency"] = transparency

    # Visibility
    event_body["visibility"] = visibility

    # Guest permissions (camelCase as per API)
    if guestsCanModify is not None:
        event_body["guestsCanModify"] = guestsCanModify
    if guestsCanInviteOthers is not None:
        event_body["guestsCanInviteOthers"] = guestsCanInviteOthers
    if guestsCanSeeOtherGuests is not None:
        event_body["guestsCanSeeOtherGuests"] = guestsCanSeeOtherGuests

    # Conference data
    if conferenceData:
        event_body["conferenceData"] = conferenceData

    # Reminders
    if reminders:
        event_body["reminders"] = reminders

    # Color
    if colorId:
        event_body["colorId"] = colorId

    # Query parameters
    params = {}
    if sendUpdates:
        params["sendUpdates"] = sendUpdates
    if conferenceData:
        params["conferenceDataVersion"] = 1

    return await client.post(
        f"/calendars/{calendar_id}/events",
        json_data=event_body,
        params=params
    )

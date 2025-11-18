"""
Updates an existing event by `event_id` in a Google Calendar; this is a full PUT replacement, so provide all desired fields as unspecified ones may be cleared or reset.

Google Calendar API Reference:
https://developers.google.com/calendar/api/v3/reference/events/update
"""

from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta
from .client import CalendarAPIClient


async def update_event(
    event_id: str,
    start_datetime: str,
    attendees: Optional[List[str]] = None,
    birthdayProperties: Optional[Dict[str, Any]] = None,
    calendar_id: str = "primary",
    create_meeting_room: Optional[bool] = None,
    description: Optional[str] = None,
    eventType: str = "default",
    event_duration_hour: int = 0,
    event_duration_minutes: int = 0,
    focusTimeProperties: Optional[Dict[str, Any]] = None,
    guestsCanInviteOthers: Optional[bool] = None,
    guestsCanSeeOtherGuests: Optional[bool] = None,
    guestsCanModify: bool = False,
    location: Optional[str] = None,
    outOfOfficeProperties: Optional[Dict[str, Any]] = None,
    recurrence: Optional[List[str]] = None,
    sendUpdates: str = "all",
    summary: Optional[str] = None,
    timezone: Optional[str] = None,
    transparency: str = "opaque",
    visibility: str = "default",
    workingLocationProperties: Optional[Dict[str, Any]] = None,
    colorId: Optional[str] = None,
    conferenceData: Optional[Dict[str, Any]] = None,
    reminders: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Updates an existing event by `event_id` in a Google Calendar; this is a full PUT replacement, so provide all desired fields as unspecified ones may be cleared or reset.

    Args:
        event_id: The unique identifier of the event to be updated.
        start_datetime: Event start time in ISO 8601 format (e.g., "2025-01-16T13:00:00")
        attendees: List of attendee email addresses (strings).
        birthdayProperties: Properties for birthday events.
        calendar_id: Identifier of the Google Calendar where the event resides. Default: "primary"
        create_meeting_room: If true, a Google Meet link is created and added to the event.
        description: Description of the event. Can contain HTML.
        eventType: Type of the event. Default: "default"
        event_duration_hour: Duration in hours (0-24).
        event_duration_minutes: Duration in minutes (0-59).
        focusTimeProperties: Properties for focusTime events.
        guestsCanInviteOthers: Whether attendees other than the organizer can invite others to the event.
        guestsCanSeeOtherGuests: Whether attendees other than the organizer can see who the event's attendees are.
        guestsCanModify: Whether guests can modify the event.
        location: Geographic location of the event as free-form text.
        outOfOfficeProperties: Properties for outOfOffice events.
        recurrence: List of RRULE, EXRULE, RDATE, EXDATE lines for recurring events.
        sendUpdates: Whether to send updates: "all", "externalOnly", or "none"
        summary: Summary (title) of the event.
        timezone: IANA timezone name (e.g., 'America/New_York').
        transparency: 'opaque' (busy) or 'transparent' (available).
        visibility: Event visibility: 'default', 'public', 'private', or 'confidential'.
        workingLocationProperties: Properties for workingLocation events.
        colorId: Color ID (1-11)
        conferenceData: Conference data (e.g., Google Meet)
        reminders: Reminder overrides

    Returns:
        Dict containing the API response

    Example:
        result = await update_event(
            event_id="abc123",
            start_datetime="2024-01-15T10:00:00",
            summary="Updated Meeting",
            timezone="America/Los_Angeles",
            event_duration_hour=1
        )
    """
    client = CalendarAPIClient()

    endpoint = f"/calendars/{calendar_id}/events/{event_id}"

    # Parse start datetime and calculate end datetime
    try:
        start_dt = datetime.fromisoformat(start_datetime.replace("Z", "+00:00"))
    except ValueError:
        # If no timezone info, treat as naive
        start_dt = datetime.fromisoformat(start_datetime)

    # Calculate end time
    duration = timedelta(hours=event_duration_hour, minutes=event_duration_minutes)
    end_dt = start_dt + duration

    # Build event body according to Google Calendar API spec
    request_body: Dict[str, Any] = {}

    # Summary
    if summary:
        request_body["summary"] = summary

    # Description
    if description:
        request_body["description"] = description

    # Location
    if location:
        request_body["location"] = location

    # Start time (required structure: {dateTime, timeZone})
    start_obj: Dict[str, str] = {"dateTime": start_dt.isoformat()}
    if timezone:
        start_obj["timeZone"] = timezone
    request_body["start"] = start_obj

    # End time (required structure: {dateTime, timeZone})
    end_obj: Dict[str, str] = {"dateTime": end_dt.isoformat()}
    if timezone:
        end_obj["timeZone"] = timezone
    request_body["end"] = end_obj

    # Attendees (must be array of objects with 'email' field)
    if attendees:
        request_body["attendees"] = [{"email": email} for email in attendees]

    # Recurrence
    if recurrence:
        request_body["recurrence"] = recurrence

    # Transparency
    request_body["transparency"] = transparency

    # Visibility
    request_body["visibility"] = visibility

    # Event type
    if eventType:
        request_body["eventType"] = eventType

    # Guest permissions (camelCase as per API)
    if guestsCanModify is not None:
        request_body["guestsCanModify"] = guestsCanModify
    if guestsCanInviteOthers is not None:
        request_body["guestsCanInviteOthers"] = guestsCanInviteOthers
    if guestsCanSeeOtherGuests is not None:
        request_body["guestsCanSeeOtherGuests"] = guestsCanSeeOtherGuests

    # Special event properties
    if birthdayProperties:
        request_body["birthdayProperties"] = birthdayProperties
    if focusTimeProperties:
        request_body["focusTimeProperties"] = focusTimeProperties
    if outOfOfficeProperties:
        request_body["outOfOfficeProperties"] = outOfOfficeProperties
    if workingLocationProperties:
        request_body["workingLocationProperties"] = workingLocationProperties

    # Conference data
    if conferenceData:
        request_body["conferenceData"] = conferenceData

    # Reminders
    if reminders:
        request_body["reminders"] = reminders

    # Color
    if colorId:
        request_body["colorId"] = colorId

    # Query parameters
    params = {}
    if sendUpdates:
        params["sendUpdates"] = sendUpdates
    if conferenceData:
        params["conferenceDataVersion"] = 1

    return await client.put(endpoint, json_data=request_body, params=params)

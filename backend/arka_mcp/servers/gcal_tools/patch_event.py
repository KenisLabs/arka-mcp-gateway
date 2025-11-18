"""
Update specified fields of an existing event in a Google Calendar using patch semantics (array fields like `attendees` are fully replaced if provided); ensure the `calendar_id` and `event_id` are valid and the user has write access to the calendar.

Google Calendar API Reference:
https://developers.google.com/calendar/api/v3/reference/events/patch
"""
from typing import Any, Dict, List, Optional
from .client import CalendarAPIClient


async def patch_event(
    calendar_id: str,
    event_id: str,
    attendees: Optional[List[str]] = None,
    conferenceDataVersion: Optional[int] = None,
    description: Optional[str] = None,
    end_time: Optional[str] = None,
    location: Optional[str] = None,
    maxAttendees: Optional[int] = None,
    sendUpdates: Optional[str] = None,
    start_time: Optional[str] = None,
    summary: Optional[str] = None,
    supportsAttachments: Optional[bool] = None,
    timezone: Optional[str] = None,
    transparency: Optional[str] = None,
    visibility: Optional[str] = None,
    guestsCanModify: Optional[bool] = None,
    guestsCanInviteOthers: Optional[bool] = None,
    guestsCanSeeOtherGuests: Optional[bool] = None,
    recurrence: Optional[List[str]] = None,
    colorId: Optional[str] = None
) -> dict:
    """
    Update specified fields of an existing event in a Google Calendar using patch semantics (array fields like attendees are fully replaced if provided).

    Args:
        calendar_id: Identifier of the calendar. Use 'primary' for the primary calendar.
        event_id: Identifier of the event to update.
        attendees: List of email addresses for attendees. Replaces existing attendees.
        conferenceDataVersion: API client's conference data support version. Set to 1 to manage conference details.
        description: New description for the event; can include HTML.
        end_time: New end time (RFC3339 timestamp, e.g., '2024-07-01T11:00:00-07:00'). Uses `timezone` if provided.
        location: New geographic location (physical address or virtual meeting link).
        maxAttendees: Maximum attendees in response; does not affect invited count.
        sendUpdates: Whether to send update notifications to attendees: 'all', 'externalOnly', or 'none'.
        start_time: New start time (RFC3339 timestamp, e.g., '2024-07-01T10:00:00-07:00'). Uses `timezone` if provided.
        summary: New title for the event.
        supportsAttachments: Client application supports event attachments.
        timezone: IANA Time Zone Database name for start/end times (e.g., 'America/Los_Angeles').
        transparency: 'opaque' (busy) or 'transparent' (available).
        visibility: Event visibility: 'default', 'public', 'private', or 'confidential'.
        guestsCanModify: Whether guests can modify the event.
        guestsCanInviteOthers: Whether guests can invite others.
        guestsCanSeeOtherGuests: Whether guests can see other guests.
        recurrence: List of RRULE, EXRULE, RDATE, EXDATE lines for recurring events.
        colorId: Color ID (1-11)

    Returns:
        Dict containing the API response

    Example:
        result = await patch_event(
            calendar_id="primary",
            event_id="abc123",
            summary="Updated Meeting Title",
            start_time="2024-07-01T10:00:00-07:00"
        )
    """
    client = CalendarAPIClient()

    endpoint = f"/calendars/{calendar_id}/events/{event_id}"

    # Build request body with proper API field names
    request_body: Dict[str, Any] = {}

    # Summary
    if summary is not None:
        request_body["summary"] = summary

    # Description
    if description is not None:
        request_body["description"] = description

    # Location
    if location is not None:
        request_body["location"] = location

    # Start and End times (must be proper objects with dateTime and timeZone)
    if start_time is not None:
        start_obj: Dict[str, str] = {"dateTime": start_time}
        if timezone:
            start_obj["timeZone"] = timezone
        request_body["start"] = start_obj

    if end_time is not None:
        end_obj: Dict[str, str] = {"dateTime": end_time}
        if timezone:
            end_obj["timeZone"] = timezone
        request_body["end"] = end_obj

    # Attendees (must be array of objects with 'email' field)
    if attendees is not None:
        request_body["attendees"] = [{"email": email} for email in attendees]

    # Recurrence
    if recurrence is not None:
        request_body["recurrence"] = recurrence

    # Transparency
    if transparency is not None:
        request_body["transparency"] = transparency

    # Visibility
    if visibility is not None:
        request_body["visibility"] = visibility

    # Guest permissions (camelCase as per API)
    if guestsCanModify is not None:
        request_body["guestsCanModify"] = guestsCanModify
    if guestsCanInviteOthers is not None:
        request_body["guestsCanInviteOthers"] = guestsCanInviteOthers
    if guestsCanSeeOtherGuests is not None:
        request_body["guestsCanSeeOtherGuests"] = guestsCanSeeOtherGuests

    # Color
    if colorId is not None:
        request_body["colorId"] = colorId

    # Query parameters
    params = {}
    if sendUpdates is not None:
        params["sendUpdates"] = sendUpdates
    if maxAttendees is not None:
        params["maxAttendees"] = maxAttendees
    if supportsAttachments is not None:
        params["supportsAttachments"] = supportsAttachments
    if conferenceDataVersion is not None:
        params["conferenceDataVersion"] = conferenceDataVersion

    return await client.patch(endpoint, json_data=request_body, params=params)

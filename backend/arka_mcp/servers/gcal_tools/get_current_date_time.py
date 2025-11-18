"""
Utility function to get current date and time in various formats.

This is a helper function for working with Google Calendar API timestamps.
"""
from typing import Dict, Any, Optional
from datetime import datetime, timezone
import pytz


async def get_current_date_time(
    timezone_name: Optional[str] = None,
    format_type: Optional[str] = "iso"
) -> Dict[str, Any]:
    """
    Get current date and time in specified timezone and format.

    Args:
        timezone_name: IANA timezone name (e.g., 'America/New_York'). Defaults to UTC.
        format_type: Format type: 'iso' (ISO 8601), 'rfc3339', or 'simple'. Default: 'iso'

    Returns:
        Dict containing:
        - datetime: Formatted datetime string
        - timezone: Timezone name
        - timestamp: Unix timestamp

    Example:
        result = await get_current_date_time(timezone_name="America/New_York")
        # Returns: {"datetime": "2025-01-16T10:30:00-05:00", "timezone": "America/New_York", "timestamp": 1737037800}
    """
    # Determine timezone
    if timezone_name:
        try:
            tz = pytz.timezone(timezone_name)
        except pytz.exceptions.UnknownTimeZoneError:
            tz = timezone.utc
            timezone_name = "UTC"
    else:
        tz = timezone.utc
        timezone_name = "UTC"

    # Get current time in specified timezone
    now = datetime.now(tz)

    # Format based on requested format
    if format_type == "rfc3339":
        formatted = now.strftime("%Y-%m-%dT%H:%M:%S%z")
        # Insert colon in timezone offset
        if len(formatted) > 0 and formatted[-2] != ':':
            formatted = formatted[:-2] + ':' + formatted[-2:]
    elif format_type == "simple":
        formatted = now.strftime("%Y-%m-%d %H:%M:%S")
    else:  # iso
        formatted = now.isoformat()

    return {
        "datetime": formatted,
        "timezone": timezone_name,
        "timestamp": int(now.timestamp()),
        "date": now.strftime("%Y-%m-%d"),
        "time": now.strftime("%H:%M:%S")
    }

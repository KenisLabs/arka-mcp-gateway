"""
Validators for Google Calendar tool parameters.

Provides Pydantic models for validating Calendar IDs, Event IDs, and other
Calendar-specific identifiers.
"""
from pydantic import BaseModel, Field, field_validator


class CalendarId(BaseModel):
    """Validator for Google Calendar ID"""
    calendar_id: str = Field(
        min_length=1,
        max_length=255,
        description="Calendar identifier (e.g., 'primary' or email address)"
    )

    @field_validator('calendar_id')
    @classmethod
    def validate_calendar_id(cls, v: str) -> str:
        """Validate calendar ID format"""
        if not v or not v.strip():
            raise ValueError("Calendar ID cannot be empty")
        return v.strip()


class EventId(BaseModel):
    """Validator for Google Calendar Event ID"""
    event_id: str = Field(
        min_length=1,
        max_length=1024,
        description="Event identifier"
    )

    @field_validator('event_id')
    @classmethod
    def validate_event_id(cls, v: str) -> str:
        """Validate event ID format"""
        if not v or not v.strip():
            raise ValueError("Event ID cannot be empty")
        return v.strip()


class AclRuleId(BaseModel):
    """Validator for Google Calendar ACL Rule ID"""
    rule_id: str = Field(
        min_length=1,
        max_length=255,
        description="ACL rule identifier"
    )

    @field_validator('rule_id')
    @classmethod
    def validate_rule_id(cls, v: str) -> str:
        """Validate ACL rule ID format"""
        if not v or not v.strip():
            raise ValueError("ACL rule ID cannot be empty")
        return v.strip()

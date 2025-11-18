"""
Pydantic models for Google Calendar tool requests.

This module will contain all request models for the 28 Calendar tools.
Starting with ListCalendarsRequest for initial testing.
"""
from pydantic import BaseModel, Field
from typing import Optional


class ListCalendarsRequest(BaseModel):
    """Request model for list_calendars tool"""
    max_results: int = Field(
        default=100,
        ge=1,
        le=250,
        description="Maximum number of calendars to return per page"
    )
    min_access_role: Optional[str] = Field(
        default=None,
        description="Minimum access role filter"
    )
    page_token: Optional[str] = Field(
        default=None,
        description="Token for retrieving next page of results"
    )
    show_deleted: bool = Field(
        default=False,
        description="Include deleted calendar list entries"
    )
    show_hidden: bool = Field(
        default=False,
        description="Include hidden calendars"
    )
    sync_token: Optional[str] = Field(
        default=None,
        description="Sync token from previous list request"
    )


# More models will be added here as we implement additional tools

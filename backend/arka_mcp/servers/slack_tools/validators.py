"""
Validators for Slack tool parameters.

Provides Pydantic models for validating Slack identifiers such as
Channel IDs, User IDs, Message Timestamps, and other Slack-specific fields.
"""
from pydantic import BaseModel, Field, field_validator


class ChannelId(BaseModel):
    """Validator for Slack Channel ID"""
    channel_id: str = Field(
        min_length=1,
        max_length=255,
        description="Channel identifier (e.g., 'C1234567890', 'G1234567890', 'D1234567890')"
    )

    @field_validator('channel_id')
    @classmethod
    def validate_channel_id(cls, v: str) -> str:
        """Validate channel ID format"""
        if not v or not v.strip():
            raise ValueError("Channel ID cannot be empty")
        return v.strip()


class UserId(BaseModel):
    """Validator for Slack User ID"""
    user_id: str = Field(
        min_length=1,
        max_length=255,
        description="User identifier (e.g., 'U1234567890')"
    )

    @field_validator('user_id')
    @classmethod
    def validate_user_id(cls, v: str) -> str:
        """Validate user ID format"""
        if not v or not v.strip():
            raise ValueError("User ID cannot be empty")
        return v.strip()


class MessageTimestamp(BaseModel):
    """Validator for Slack Message Timestamp"""
    timestamp: str = Field(
        min_length=1,
        max_length=255,
        description="Message timestamp (e.g., '1234567890.123456')"
    )

    @field_validator('timestamp')
    @classmethod
    def validate_timestamp(cls, v: str) -> str:
        """Validate timestamp format"""
        if not v or not v.strip():
            raise ValueError("Timestamp cannot be empty")
        # Basic format validation for Slack timestamps
        if '.' not in v:
            raise ValueError("Timestamp must be in format 'seconds.microseconds'")
        return v.strip()


class EmojiName(BaseModel):
    """Validator for Slack Emoji Name"""
    emoji_name: str = Field(
        min_length=1,
        max_length=255,
        description="Emoji name without colons (e.g., 'thumbsup', 'heart', 'fire')"
    )

    @field_validator('emoji_name')
    @classmethod
    def validate_emoji_name(cls, v: str) -> str:
        """Validate emoji name format"""
        if not v or not v.strip():
            raise ValueError("Emoji name cannot be empty")
        # Remove colons if present
        v = v.strip().strip(':')
        return v


class SearchQuery(BaseModel):
    """Validator for Slack Search Query"""
    query: str = Field(
        min_length=1,
        max_length=4000,
        description="Search query with optional operators"
    )

    @field_validator('query')
    @classmethod
    def validate_query(cls, v: str) -> str:
        """Validate search query"""
        if not v or not v.strip():
            raise ValueError("Search query cannot be empty")
        return v.strip()

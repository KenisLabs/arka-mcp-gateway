"""
Shared validators for Gmail tools.

Provides Pydantic models for validating common Gmail identifiers
to prevent security issues like SSRF attacks.

These validators are used across multiple Gmail tools to ensure
consistent validation and security.
"""
from pydantic import BaseModel, field_validator


class MessageId(BaseModel):
    """Validated Gmail message ID."""
    message_id: str

    @field_validator('message_id')
    @classmethod
    def validate_message_id(cls, v: str) -> str:
        """
        Validate message ID format to prevent SSRF attacks.

        Gmail message IDs are hex strings, typically 16 characters.
        """
        if not v:
            raise ValueError("message_id cannot be empty")
        if not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError("Invalid message_id format")
        if len(v) > 128:
            raise ValueError("message_id too long")
        return v


class LabelId(BaseModel):
    """Validated Gmail label ID."""
    label_id: str

    @field_validator('label_id')
    @classmethod
    def validate_label_id(cls, v: str) -> str:
        """
        Validate label ID format.

        System labels are uppercase with underscores (e.g., INBOX, STARRED).
        Custom labels are like Label_123.
        """
        if not v:
            raise ValueError("label_id cannot be empty")
        if not v.replace('_', '').isalnum():
            raise ValueError("Invalid label_id format")
        if len(v) > 128:
            raise ValueError("label_id too long")
        return v


class ThreadId(BaseModel):
    """Validated Gmail thread ID."""
    thread_id: str

    @field_validator('thread_id')
    @classmethod
    def validate_thread_id(cls, v: str) -> str:
        """
        Validate thread ID format to prevent SSRF attacks.

        Gmail thread IDs are hex strings similar to message IDs.
        """
        if not v:
            raise ValueError("thread_id cannot be empty")
        if not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError("Invalid thread_id format")
        if len(v) > 128:
            raise ValueError("thread_id too long")
        return v


class DraftId(BaseModel):
    """Validated Gmail draft ID."""
    draft_id: str

    @field_validator('draft_id')
    @classmethod
    def validate_draft_id(cls, v: str) -> str:
        """
        Validate draft ID format.

        Draft IDs can contain hyphens and alphanumeric characters.
        """
        if not v:
            raise ValueError("draft_id cannot be empty")
        if not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError("Invalid draft_id format")
        if len(v) > 128:
            raise ValueError("draft_id too long")
        return v


class AttachmentId(BaseModel):
    """Validated Gmail attachment ID."""
    attachment_id: str

    @field_validator('attachment_id')
    @classmethod
    def validate_attachment_id(cls, v: str) -> str:
        """
        Validate attachment ID format.

        Attachment IDs are alphanumeric with underscores and periods.
        """
        if not v:
            raise ValueError("attachment_id cannot be empty")
        if not v.replace('_', '').replace('.', '').replace('-', '').isalnum():
            raise ValueError("Invalid attachment_id format")
        if len(v) > 256:
            raise ValueError("attachment_id too long")
        return v

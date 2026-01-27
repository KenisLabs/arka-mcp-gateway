"""
Pydantic request models for Gmail tools.

Contains input validation models for all Gmail API operations.
These models ensure type safety and input validation before making API calls.

Based on gmail.md specification.
"""
from typing import List, Optional
from pydantic import BaseModel, field_validator
from arka_mcp.servers.gmail_tools.validators import MessageId, LabelId, ThreadId, DraftId


# ============================================================================
# Label Management Models
# ============================================================================

class ListLabelsRequest(BaseModel):
    """Request model for listing Gmail labels."""
    user_id: str = "me"


class CreateLabelRequest(BaseModel):
    """Request model for creating a new Gmail label."""
    label_name: str
    user_id: str = "me"
    background_color: Optional[str] = None
    text_color: Optional[str] = None
    label_list_visibility: str = "labelShow"
    message_list_visibility: str = "show"

    @field_validator('label_name')
    @classmethod
    def validate_label_name(cls, v: str) -> str:
        """Validate label name."""
        if not v or not v.strip():
            raise ValueError("label_name cannot be empty")
        if len(v) > 225:
            raise ValueError("label_name too long (max 225 characters)")
        if any(char in v for char in [',', '/', '.']):
            raise ValueError("label_name cannot contain ',', '/', or '.'")
        return v


class RemoveLabelRequest(BaseModel):
    """Request model for removing a Gmail label."""
    label_id: str
    user_id: str = "me"

    @field_validator('label_id')
    @classmethod
    def validate_label_id(cls, v: str) -> str:
        """Validate label_id format."""
        LabelId(label_id=v)
        return v


class PatchLabelRequest(BaseModel):
    """Request model for patching a Gmail label."""
    id: str
    userId: str = "me"
    name: Optional[str] = None
    color: Optional[dict] = None
    labelListVisibility: Optional[str] = None
    messageListVisibility: Optional[str] = None


class AddLabelToEmailRequest(BaseModel):
    """Request model for adding/removing labels to/from an email."""
    message_id: str
    add_label_ids: List[str] = []
    remove_label_ids: List[str] = []
    user_id: str = "me"

    @field_validator('message_id')
    @classmethod
    def validate_message_id(cls, v: str) -> str:
        """Validate message_id format to prevent SSRF."""
        MessageId(message_id=v)
        return v

    @field_validator('add_label_ids', 'remove_label_ids')
    @classmethod
    def validate_label_ids(cls, v: List[str]) -> List[str]:
        """Validate label_ids format."""
        for label_id in v:
            LabelId(label_id=label_id)
        return v


# ============================================================================
# Message Management Models
# ============================================================================

class FetchEmailsRequest(BaseModel):
    """Request model for fetching emails."""
    user_id: str = "me"
    max_results: int = 1
    label_ids: Optional[List[str]] = None
    query: Optional[str] = None
    page_token: Optional[str] = None
    include_spam_trash: bool = False
    include_payload: bool = True
    ids_only: bool = False
    verbose: bool = True


class FetchMessageByIdRequest(BaseModel):
    """Request model for fetching a message by ID."""
    message_id: str
    user_id: str = "me"
    format: str = "full"

    @field_validator('message_id')
    @classmethod
    def validate_message_id(cls, v: str) -> str:
        """Validate message_id format."""
        MessageId(message_id=v)
        return v


class BatchModifyMessagesRequest(BaseModel):
    """Request model for batch modifying messages."""
    messageIds: List[str]
    addLabelIds: Optional[List[str]] = None
    removeLabelIds: Optional[List[str]] = None
    userId: str = "me"

    @field_validator('messageIds')
    @classmethod
    def validate_message_ids(cls, v: List[str]) -> List[str]:
        """Validate all message IDs."""
        if not v:
            raise ValueError("messageIds cannot be empty")
        if len(v) > 1000:
            raise ValueError("Maximum 1000 message IDs allowed")
        for msg_id in v:
            MessageId(message_id=msg_id)
        return v


class MoveToTrashRequest(BaseModel):
    """Request model for moving a message to trash."""
    message_id: str
    user_id: str = "me"

    @field_validator('message_id')
    @classmethod
    def validate_message_id(cls, v: str) -> str:
        """Validate message_id format."""
        MessageId(message_id=v)
        return v


class BatchDeleteMessagesRequest(BaseModel):
    """Request model for batch deleting messages."""
    ids: List[str]
    userId: str = "me"

    @field_validator('ids')
    @classmethod
    def validate_ids(cls, v: List[str]) -> List[str]:
        """Validate all message IDs."""
        if not v:
            raise ValueError("ids cannot be empty")
        for msg_id in v:
            MessageId(message_id=msg_id)
        return v


class GetAttachmentRequest(BaseModel):
    """Request model for getting an attachment."""
    message_id: str
    attachment_id: str
    file_name: str
    user_id: str = "me"

    @field_validator('message_id')
    @classmethod
    def validate_message_id(cls, v: str) -> str:
        """Validate message_id format."""
        MessageId(message_id=v)
        return v


# ============================================================================
# Thread Management Models
# ============================================================================

class FetchMessagesByThreadIdRequest(BaseModel):
    """Request model for fetching messages by thread ID."""
    thread_id: str
    user_id: str = "me"
    page_token: str = ""

    @field_validator('thread_id')
    @classmethod
    def validate_thread_id(cls, v: str) -> str:
        """Validate thread_id format."""
        ThreadId(thread_id=v)
        return v


class ListThreadsRequest(BaseModel):
    """Request model for listing threads."""
    user_id: str = "me"
    max_results: int = 10
    query: str = ""
    page_token: str = ""
    verbose: bool = False


class ModifyThreadLabelsRequest(BaseModel):
    """Request model for modifying thread labels."""
    thread_id: str
    user_id: str = "me"
    add_label_ids: Optional[List[str]] = None
    remove_label_ids: Optional[List[str]] = None

    @field_validator('thread_id')
    @classmethod
    def validate_thread_id(cls, v: str) -> str:
        """Validate thread_id format."""
        ThreadId(thread_id=v)
        return v


# ============================================================================
# Draft Management Models
# ============================================================================

class ListDraftsRequest(BaseModel):
    """Request model for listing drafts."""
    user_id: str = "me"
    max_results: int = 1
    page_token: str = ""
    verbose: bool = False


class DeleteDraftRequest(BaseModel):
    """Request model for deleting a draft."""
    draft_id: str
    user_id: str = "me"

    @field_validator('draft_id')
    @classmethod
    def validate_draft_id(cls, v: str) -> str:
        """Validate draft_id format."""
        DraftId(draft_id=v)
        return v


class SendDraftRequest(BaseModel):
    """Request model for sending a draft."""
    draft_id: str
    user_id: str = "me"

    @field_validator('draft_id')
    @classmethod
    def validate_draft_id(cls, v: str) -> str:
        """Validate draft_id format."""
        DraftId(draft_id=v)
        return v


# ============================================================================
# History/Profile Models
# ============================================================================

class GetProfileRequest(BaseModel):
    """Request model for getting Gmail profile."""
    user_id: str = "me"


class HistoryListRequest(BaseModel):
    """Request model for listing history."""
    startHistoryId: str
    user_id: str = "me"
    maxResults: Optional[int] = None
    pageToken: Optional[str] = None
    labelId: Optional[str] = None
    historyTypes: Optional[List[str]] = None


# ============================================================================
# Newsletter Management Models
# ============================================================================

class FetchNewsletterSubscriptionsRequest(BaseModel):
    """Request model for fetching newsletter subscriptions."""
    user_id: str = "me"
    max_results: int = 50
    page_token: Optional[str] = None
    from_email: Optional[str] = None

    @field_validator('max_results')
    @classmethod
    def validate_max_results(cls, v: int) -> int:
        """Validate max_results range."""
        if v < 1 or v > 500:
            raise ValueError("max_results must be between 1 and 500")
        return v


class UnsubscribeFromNewsletterRequest(BaseModel):
    """Request model for unsubscribing from a newsletter."""
    message_id: str
    user_id: str = "me"

    @field_validator('message_id')
    @classmethod
    def validate_message_id(cls, v: str) -> str:
        """Validate message_id format to prevent SSRF."""
        MessageId(message_id=v)
        return v

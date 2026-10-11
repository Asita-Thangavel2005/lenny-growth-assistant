
import uuid
from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field


class SessionCreateRequest(BaseModel):
    title: str = Field(default="New conversation", max_length=200)
    user_metadata: dict[str, Any] = Field(default_factory=dict)


class SessionResponse(BaseModel):
    id: uuid.UUID
    title: str
    user_metadata: dict[str, Any]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}



class ChatRequest(BaseModel):
    session_id: uuid.UUID
    question: str = Field(min_length=1, max_length=12000)
    provider: Literal["local", "cloud"] | None = None


class SourceResponse(BaseModel):
    episode_title: str
    episode_url: str | None = None
    chunk_index: int
    content: str


class ChatResponse(BaseModel):
    session_id: str
    answer: str
    sources: list[SourceResponse]


class MessageResponse(BaseModel):
    id: uuid.UUID
    session_id: uuid.UUID
    role: Literal["user", "assistant", "system"]
    content: str
    message_metadata: dict[str, Any]
    created_at: datetime

    model_config = {"from_attributes": True}

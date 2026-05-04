from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class UploadInitRequest(BaseModel):
    filename: str = Field(..., min_length=1)
    content_type: str = Field(default="application/pdf")


class UploadInitResponse(BaseModel):
    doc_id: str
    s3_key: str
    upload_url: str
    expires_in: int
    status: str


class ProcessRequest(BaseModel):
    doc_id: str
    s3_key: str
    filename: str
    async_processing: bool = True


class ProcessResponse(BaseModel):
    doc_id: str
    status: str
    message: str


class ChatRequest(BaseModel):
    session_id: str = Field(..., min_length=1)
    question: str = Field(..., min_length=1)
    doc_ids: list[str] = Field(default_factory=list)
    top_k: int = Field(default=6, ge=1, le=12)


class SourceReference(BaseModel):
    source_id: str
    doc_id: str
    page_no: int
    chunk_index: int
    snippet: str
    score: float | None = None


class ChatResponse(BaseModel):
    session_id: str
    answer: str
    sources: list[SourceReference]


class ChatHistoryMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str
    created_at: datetime


class ChatHistoryResponse(BaseModel):
    session_id: str
    messages: list[ChatHistoryMessage]


class DocumentStatusResponse(BaseModel):
    doc_id: str
    user_id: str
    filename: str
    s3_key: str
    status: str
    created_at: datetime
    updated_at: datetime
    page_count: int | None = None
    chunk_count: int | None = None
    error: str | None = None

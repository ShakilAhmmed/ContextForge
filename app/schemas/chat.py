import uuid

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    question: str = Field(min_length=1, max_length=2000)


class Citation(BaseModel):
    document_id: uuid.UUID
    filename: str
    chunk_text: str


class ChatResponse(BaseModel):
    answer: str
    citations: list[Citation]

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class DocumentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    tenant_id: uuid.UUID
    filename: str
    content_type: str
    size_bytes: int
    status: str
    created_at: datetime


class ChunkPoint(BaseModel):
    text: str
    x: float
    y: float

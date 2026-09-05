import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base

# Ingestion pipeline states. Worker (chunk/embed/index) is future work - this
# repo only ever writes "queued" today, after a successful enqueue.
STATUS_QUEUED = "queued"
STATUS_PROCESSING = "processing"
STATUS_INDEXED = "indexed"
STATUS_FAILED = "failed"


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("tenants.id"), nullable=False)
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    content_type: Mapped[str] = mapped_column(String(127), nullable=False)
    size_bytes: Mapped[int] = mapped_column(Integer, nullable=False)
    storage_key: Mapped[str] = mapped_column(String(512), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default=STATUS_QUEUED)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.errors import bad_request, payload_too_large
from app.core.queue import QueueClient
from app.core.storage import ObjectStorage
from app.models.document import Document

ALLOWED_CONTENT_TYPES = {"application/pdf", "text/plain", "text/markdown"}


async def upload_document(
    *,
    tenant_id: uuid.UUID,
    filename: str | None,
    content_type: str | None,
    content: bytes,
    db: AsyncSession,
    storage: ObjectStorage,
    queue: QueueClient,
) -> Document:
    """Store the file, persist its record, and enqueue it for the (future)
    ingestion worker to chunk/embed/index. Storage + DB commit happen before
    the enqueue so a document row always exists for whatever it references -
    a message referencing a not-yet-committed document would be worse."""
    if content_type not in ALLOWED_CONTENT_TYPES:
        raise bad_request(f"unsupported content type: {content_type}")

    if len(content) > settings.max_upload_size_bytes:
        raise payload_too_large(f"file exceeds max upload size of {settings.max_upload_size_bytes} bytes")

    document = Document(
        tenant_id=tenant_id,
        filename=filename or "untitled",
        content_type=content_type,
        size_bytes=len(content),
        storage_key=f"{tenant_id}/{uuid.uuid4()}/{filename or 'untitled'}",
    )
    await storage.put_object(document.storage_key, content, document.content_type)

    db.add(document)
    await db.commit()
    await db.refresh(document)

    await queue.send_message(
        {
            "document_id": str(document.id),
            "tenant_id": str(tenant_id),
            "storage_key": document.storage_key,
            "content_type": document.content_type,
        }
    )
    return document

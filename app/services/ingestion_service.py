import asyncio
import logging
import uuid

from langchain_qdrant import QdrantVectorStore
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.pii import mask_pii
from app.core.storage import ObjectStorage
from app.models.document import STATUS_FAILED, STATUS_INDEXED, STATUS_PROCESSING, Document

logger = logging.getLogger(__name__)

# PDF/other binary formats are decoded as best-effort UTF-8 for now - proper
# text extraction (e.g. pypdf) is future work once a real document corpus is
# in scope; this only produces sane text for text/plain and text/markdown today.
_splitter = RecursiveCharacterTextSplitter(
    chunk_size=settings.chunk_size, chunk_overlap=settings.chunk_overlap
)


async def ingest_document(
    *,
    document_id: uuid.UUID,
    tenant_id: uuid.UUID,
    storage_key: str,
    db: AsyncSession,
    storage: ObjectStorage,
    vector_store: QdrantVectorStore,
) -> None:
    document = await db.get(Document, document_id)
    if document is None:
        logger.warning("document %s no longer exists, skipping ingestion", document_id)
        return

    document.status = STATUS_PROCESSING
    await db.commit()

    try:
        content = await storage.get_object(storage_key)
        text = content.decode("utf-8", errors="ignore")
        # CPU-bound (spaCy NER) - off the event loop so it doesn't stall other
        # in-flight work in the worker process.
        masked_text = await asyncio.to_thread(mask_pii, text)
        chunks = _splitter.split_text(masked_text)

        if chunks:
            await vector_store.aadd_texts(
                chunks,
                metadatas=[{"document_id": str(document_id), "tenant_id": str(tenant_id)} for _ in chunks],
            )

        document.status = STATUS_INDEXED
        await db.commit()
    except Exception:
        logger.exception("ingestion failed for document %s", document_id)
        document.status = STATUS_FAILED
        await db.commit()
        raise

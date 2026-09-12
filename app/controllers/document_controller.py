import asyncio
import uuid

from fastapi import APIRouter, Depends, Query, UploadFile, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.errors import not_found
from app.core.pagination import PageParams, build_meta, page_params
from app.core.queue import QueueClient, get_queue
from app.core.storage import ObjectStorage, get_storage
from app.core.vectorstore import QdrantVectorStore, get_document_chunks, get_vector_store
from app.db import get_db
from app.models.document import Document
from app.models.user import User
from app.schemas.common import PaginatedResponse, SuccessResponse
from app.schemas.document import ChunkPoint, DocumentRead
from app.services import document_service
from app.services.chunk_projection import project_to_2d

router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("", response_model=SuccessResponse[DocumentRead], status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    storage: ObjectStorage = Depends(get_storage),
    queue: QueueClient = Depends(get_queue),
) -> SuccessResponse[DocumentRead]:
    document = await document_service.upload_document(
        tenant_id=current_user.tenant_id,
        filename=file.filename,
        content_type=file.content_type,
        content=await file.read(),
        db=db,
        storage=storage,
        queue=queue,
    )
    return SuccessResponse(code=201, message="document uploaded and queued for ingestion", data=document)


@router.get("", response_model=PaginatedResponse[DocumentRead])
async def list_documents(
    params: PageParams = Depends(page_params),
    search: str | None = Query(None, description="Case-insensitive filename substring match"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> PaginatedResponse[DocumentRead]:
    scoped = select(Document).where(Document.tenant_id == current_user.tenant_id)
    if search:
        scoped = scoped.where(Document.filename.ilike(f"%{search}%"))
    total_items = await db.scalar(select(func.count()).select_from(scoped.subquery()))
    result = await db.execute(
        scoped.order_by(Document.created_at.desc()).offset(params.offset).limit(params.page_size)
    )
    return PaginatedResponse(data=list(result.scalars().all()), meta=build_meta(params, total_items or 0))


@router.get("/{document_id}", response_model=SuccessResponse[DocumentRead])
async def get_document(
    document_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SuccessResponse[DocumentRead]:
    document = await db.get(Document, document_id)
    # 404 (not 403) for another tenant's document too - the alternative would
    # confirm to an attacker that a given document id exists at all.
    if document is None or document.tenant_id != current_user.tenant_id:
        raise not_found("document not found")
    return SuccessResponse(data=document)


@router.get("/{document_id}/chunks", response_model=SuccessResponse[list[ChunkPoint]])
async def list_document_chunks(
    document_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    vector_store: QdrantVectorStore = Depends(get_vector_store),
) -> SuccessResponse[list[ChunkPoint]]:
    document = await db.get(Document, document_id)
    if document is None or document.tenant_id != current_user.tenant_id:
        raise not_found("document not found")

    chunks = await asyncio.to_thread(get_document_chunks, vector_store, document_id)
    coords = project_to_2d([vector for _text, vector in chunks])
    points = [ChunkPoint(text=text, x=x, y=y) for (text, _vector), (x, y) in zip(chunks, coords, strict=True)]
    return SuccessResponse(data=points)

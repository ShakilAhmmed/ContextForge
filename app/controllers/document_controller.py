import uuid

from fastapi import Depends, UploadFile
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.errors import not_found
from app.core.pagination import PageParams, build_meta, page_params
from app.core.queue import QueueClient, get_queue
from app.core.storage import ObjectStorage, get_storage
from app.db import get_db
from app.models.document import Document
from app.models.user import User
from app.schemas.common import PaginatedResponse, SuccessResponse
from app.schemas.document import DocumentRead
from app.services import document_service


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


async def list_documents(
    params: PageParams = Depends(page_params),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> PaginatedResponse[DocumentRead]:
    scoped = select(Document).where(Document.tenant_id == current_user.tenant_id)
    total_items = await db.scalar(select(func.count()).select_from(scoped.subquery()))
    result = await db.execute(
        scoped.order_by(Document.created_at.desc()).offset(params.offset).limit(params.page_size)
    )
    return PaginatedResponse(data=list(result.scalars().all()), meta=build_meta(params, total_items or 0))


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

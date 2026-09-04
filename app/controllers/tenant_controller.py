import uuid

from fastapi import Depends
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import conflict, not_found
from app.core.pagination import PageParams, build_meta, page_params
from app.db import get_db
from app.models.tenant import Tenant
from app.schemas.common import PaginatedResponse, SuccessResponse
from app.schemas.tenant import TenantCreate, TenantRead


async def create_tenant(
    payload: TenantCreate, db: AsyncSession = Depends(get_db)
) -> SuccessResponse[TenantRead]:
    tenant = Tenant(name=payload.name, slug=payload.slug)
    db.add(tenant)
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise conflict("slug already exists")
    await db.refresh(tenant)
    return SuccessResponse(code=201, message="tenant created successfully", data=tenant)


async def list_tenants(
    params: PageParams = Depends(page_params), db: AsyncSession = Depends(get_db)
) -> PaginatedResponse[TenantRead]:
    total_items = await db.scalar(select(func.count()).select_from(Tenant))
    result = await db.execute(
        select(Tenant).order_by(Tenant.created_at).offset(params.offset).limit(params.page_size)
    )
    return PaginatedResponse(
        data=list(result.scalars().all()), meta=build_meta(params, total_items or 0)
    )


async def get_tenant(
    tenant_id: uuid.UUID, db: AsyncSession = Depends(get_db)
) -> SuccessResponse[TenantRead]:
    tenant = await db.get(Tenant, tenant_id)
    if tenant is None:
        raise not_found("tenant not found")
    return SuccessResponse(data=tenant)

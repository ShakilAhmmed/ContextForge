import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.errors import conflict, forbidden, not_found
from app.core.pagination import PageParams, build_meta, page_params
from app.db import get_db
from app.models.tenant import Tenant
from app.models.user import User
from app.schemas.common import PaginatedResponse, SuccessResponse
from app.schemas.tenant import TenantCreate, TenantRead

router = APIRouter(prefix="/tenants", tags=["tenants"])


@router.post("", response_model=SuccessResponse[TenantRead], status_code=status.HTTP_201_CREATED)
async def create_tenant(
    payload: TenantCreate, db: AsyncSession = Depends(get_db)
) -> SuccessResponse[TenantRead]:
    # Intentionally unauthenticated: creating a tenant is how a new customer
    # bootstraps before any user (and therefore any JWT) exists for it.
    tenant = Tenant(name=payload.name, slug=payload.slug)
    db.add(tenant)
    try:
        await db.commit()
    except IntegrityError as exc:
        await db.rollback()
        raise conflict("slug already exists") from exc
    await db.refresh(tenant)
    return SuccessResponse(code=201, message="tenant created successfully", data=tenant)


@router.get("", response_model=PaginatedResponse[TenantRead])
async def list_tenants(
    params: PageParams = Depends(page_params),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> PaginatedResponse[TenantRead]:
    # No platform-admin role exists yet, so every authenticated user is
    # scoped to their own tenant only - this never returns another tenant's row.
    scoped = select(Tenant).where(Tenant.id == current_user.tenant_id)
    total_items = await db.scalar(select(func.count()).select_from(scoped.subquery()))
    result = await db.execute(
        scoped.order_by(Tenant.created_at).offset(params.offset).limit(params.page_size)
    )
    return PaginatedResponse(data=list(result.scalars().all()), meta=build_meta(params, total_items or 0))


@router.get("/{tenant_id}", response_model=SuccessResponse[TenantRead])
async def get_tenant(
    tenant_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SuccessResponse[TenantRead]:
    if tenant_id != current_user.tenant_id:
        raise forbidden("cannot access another tenant")
    tenant = await db.get(Tenant, tenant_id)
    if tenant is None:
        raise not_found("tenant not found")
    return SuccessResponse(data=tenant)

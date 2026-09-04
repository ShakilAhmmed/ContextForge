import uuid

from fastapi import Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.models.tenant import Tenant
from app.schemas.tenant import TenantCreate


async def create_tenant(payload: TenantCreate, db: AsyncSession = Depends(get_db)) -> Tenant:
    tenant = Tenant(name=payload.name, slug=payload.slug)
    db.add(tenant)
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="slug already exists")
    await db.refresh(tenant)
    return tenant


async def list_tenants(db: AsyncSession = Depends(get_db)) -> list[Tenant]:
    result = await db.execute(select(Tenant).order_by(Tenant.created_at))
    return list(result.scalars().all())


async def get_tenant(tenant_id: uuid.UUID, db: AsyncSession = Depends(get_db)) -> Tenant:
    tenant = await db.get(Tenant, tenant_id)
    if tenant is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="tenant not found")
    return tenant

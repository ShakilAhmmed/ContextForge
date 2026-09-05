from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.errors import conflict, unauthorized
from app.core.security import create_access_token, hash_password, verify_password
from app.db import get_db
from app.models.tenant import Tenant
from app.models.user import User
from app.schemas.auth import LoginRequest, RegisterRequest, TokenData, UserRead
from app.schemas.common import SuccessResponse


async def register(
    payload: RegisterRequest, db: AsyncSession = Depends(get_db)
) -> SuccessResponse[UserRead]:
    tenant = await db.get(Tenant, payload.tenant_id)
    if tenant is None:
        raise conflict("tenant does not exist")

    user = User(
        tenant_id=payload.tenant_id,
        email=payload.email,
        hashed_password=hash_password(payload.password),
    )
    db.add(user)
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise conflict("email already registered")
    await db.refresh(user)
    return SuccessResponse(code=201, message="user registered successfully", data=user)


async def login(
    payload: LoginRequest, db: AsyncSession = Depends(get_db)
) -> SuccessResponse[TokenData]:
    result = await db.execute(select(User).where(User.email == payload.email))
    user = result.scalar_one_or_none()
    if user is None or not verify_password(payload.password, user.hashed_password):
        raise unauthorized("invalid email or password")

    access_token, expires_in = create_access_token(user.id, user.tenant_id)
    return SuccessResponse(
        message="login successful",
        data=TokenData(access_token=access_token, expires_in=expires_in),
    )


async def me(current_user: User = Depends(get_current_user)) -> SuccessResponse[UserRead]:
    return SuccessResponse(data=current_user)

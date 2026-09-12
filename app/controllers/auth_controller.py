from fastapi import APIRouter, Depends, Response, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.cookies import clear_auth_cookies, set_auth_cookies
from app.core.errors import conflict, unauthorized
from app.core.rate_limit import rate_limit
from app.core.security import create_access_token, hash_password, verify_password
from app.db import get_db
from app.models.tenant import Tenant
from app.models.user import User
from app.schemas.auth import LoginRequest, RegisterRequest, TokenData, UserRead
from app.schemas.common import SuccessResponse

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=SuccessResponse[UserRead], status_code=status.HTTP_201_CREATED)
async def register(payload: RegisterRequest, db: AsyncSession = Depends(get_db)) -> SuccessResponse[UserRead]:
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
    except IntegrityError as exc:
        await db.rollback()
        raise conflict("email already registered") from exc
    await db.refresh(user)
    return SuccessResponse(code=201, message="user registered successfully", data=user)


@router.post(
    "/login",
    response_model=SuccessResponse[TokenData],
    dependencies=[Depends(rate_limit("login", "rate_limit_login", "rate_limit_login_window_seconds"))],
)
async def login(
    payload: LoginRequest, response: Response, db: AsyncSession = Depends(get_db)
) -> SuccessResponse[TokenData]:
    result = await db.execute(select(User).where(User.email == payload.email))
    user = result.scalar_one_or_none()
    if user is None or not verify_password(payload.password, user.hashed_password):
        raise unauthorized("invalid email or password")

    access_token, expires_in = create_access_token(user.id, user.tenant_id)
    # Browser clients: httpOnly+CSRF cookies (set below), never see the raw
    # token. Header-based clients (tests, API/CLI use): the body still
    # carries it, since there's no browser-XSS threat model to protect there.
    set_auth_cookies(response, access_token, expires_in)
    return SuccessResponse(
        message="login successful",
        data=TokenData(access_token=access_token, expires_in=expires_in),
    )


@router.post("/logout", response_model=SuccessResponse[None])
async def logout(response: Response) -> SuccessResponse[None]:
    clear_auth_cookies(response)
    return SuccessResponse(message="logged out", data=None)


@router.get("/me", response_model=SuccessResponse[UserRead])
async def me(current_user: User = Depends(get_current_user)) -> SuccessResponse[UserRead]:
    return SuccessResponse(data=current_user)

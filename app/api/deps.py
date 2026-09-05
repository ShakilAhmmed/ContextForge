import uuid

import jwt
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import unauthorized
from app.core.security import decode_access_token
from app.db import get_db
from app.models.user import User

bearer_scheme = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    if credentials is None:
        raise unauthorized("missing bearer token")

    try:
        payload = decode_access_token(credentials.credentials)
    except jwt.ExpiredSignatureError:
        raise unauthorized("token expired")
    except jwt.InvalidTokenError:
        raise unauthorized("invalid token")

    user = await db.get(User, uuid.UUID(payload["sub"]))
    if user is None:
        raise unauthorized("user not found")
    return user

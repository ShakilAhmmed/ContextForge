import uuid

import jwt
from fastapi import Depends, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.errors import forbidden, unauthorized
from app.core.security import decode_access_token
from app.db import get_db
from app.models.user import User

bearer_scheme = HTTPBearer(auto_error=False)

_SAFE_METHODS = {"GET", "HEAD", "OPTIONS"}


async def get_current_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    if credentials is not None:
        token = credentials.credentials
    else:
        token = request.cookies.get(settings.access_token_cookie_name)
        if token is not None and request.method not in _SAFE_METHODS:
            _verify_csrf(request)

    if token is None:
        raise unauthorized("missing bearer token")

    try:
        payload = decode_access_token(token)
    except jwt.ExpiredSignatureError as exc:
        raise unauthorized("token expired") from exc
    except jwt.InvalidTokenError as exc:
        raise unauthorized("invalid token") from exc

    user = await db.get(User, uuid.UUID(payload["sub"]))
    if user is None:
        raise unauthorized("user not found")
    return user


def _verify_csrf(request: Request) -> None:
    """CSRF check for cookie-authenticated, state-changing requests: the
    SameSite=None cookie is sent automatically by the browser even
    cross-site, so a plain HTML-form CSRF attack (which cannot set custom
    headers) is blocked by requiring this header's presence, and a
    JS-driven cross-site attack is blocked by CORS before it ever reaches
    here (the attacker's origin isn't in cors_allowed_origins, so the
    browser refuses to attach custom headers to that credentialed request
    at all). No shared-secret value to check - the header's mere presence
    is only reachable through an allowed origin's own JS in the first place."""
    if not request.headers.get(settings.csrf_header_name):
        raise forbidden("missing CSRF header")

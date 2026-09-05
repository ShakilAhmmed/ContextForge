import uuid
from datetime import UTC, datetime, timedelta

import bcrypt
import jwt

from app.core.config import settings


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed_password.encode())


def create_access_token(user_id: uuid.UUID, tenant_id: uuid.UUID) -> tuple[str, int]:
    expires_in = settings.jwt_expire_minutes * 60
    expire = datetime.now(UTC) + timedelta(seconds=expires_in)
    payload = {"sub": str(user_id), "tenant_id": str(tenant_id), "exp": expire}
    token = jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)
    return token, expires_in


def decode_access_token(token: str) -> dict:
    return jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])

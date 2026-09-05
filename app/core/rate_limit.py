from fastapi import Depends, Request
from redis.asyncio import Redis

from app.core.config import settings
from app.core.errors import rate_limited
from app.core.redis import get_redis


def _client_ip(request: Request) -> str:
    return request.client.host if request.client else "unknown"


def rate_limit(key_prefix: str, limit_attr: str, window_attr: str):
    """Reads limit/window from `settings` at call time (not at router-definition
    time), so they can be tuned live and are straightforward to override in tests."""

    async def dependency(request: Request, redis: Redis = Depends(get_redis)) -> None:
        limit = getattr(settings, limit_attr)
        window_seconds = getattr(settings, window_attr)
        key = f"ratelimit:{key_prefix}:{_client_ip(request)}"

        async with redis.pipeline(transaction=True) as pipe:
            count, ttl = await pipe.incr(key).ttl(key).execute()

        if ttl < 0:
            await redis.expire(key, window_seconds)
            ttl = window_seconds

        if count > limit:
            raise rate_limited("too many requests, please try again later", ttl)

    return dependency

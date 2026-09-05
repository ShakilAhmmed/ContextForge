import fakeredis
import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.core.redis import get_redis
from app.db import Base, get_db
from app.main import app


@pytest.fixture
async def client():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    session_maker = async_sessionmaker(engine, expire_on_commit=False)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async def override_get_db():
        async with session_maker() as session:
            yield session

    fake_redis = fakeredis.FakeAsyncRedis(decode_responses=True)

    async def override_get_redis():
        return fake_redis

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_redis] = override_get_redis

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()
    await engine.dispose()
    await fake_redis.aclose()

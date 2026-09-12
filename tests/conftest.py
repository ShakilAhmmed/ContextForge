import fakeredis
import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.core.queue import get_queue
from app.core.redis import get_redis
from app.core.storage import get_storage
from app.core.vectorstore import get_vector_store
from app.db import Base, get_db
from app.main import app
from tests.fakes import FakeObjectStorage, FakeQueueClient, FakeVectorStore


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
    fake_storage = FakeObjectStorage()
    fake_queue = FakeQueueClient()
    fake_vector_store = FakeVectorStore()

    async def override_get_redis():
        return fake_redis

    async def override_get_storage():
        return fake_storage

    async def override_get_queue():
        return fake_queue

    def override_get_vector_store():
        return fake_vector_store

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_redis] = override_get_redis
    app.dependency_overrides[get_storage] = override_get_storage
    app.dependency_overrides[get_queue] = override_get_queue
    app.dependency_overrides[get_vector_store] = override_get_vector_store

    transport = ASGITransport(app=app)
    # https, not http - real deployment always serves over TLS, and the auth
    # cookies are Secure-flagged, so httpx's cookie jar won't store/send them
    # over a plain-http base_url.
    async with AsyncClient(transport=transport, base_url="https://test") as ac:
        ac.fake_storage = fake_storage
        ac.fake_queue = fake_queue
        ac.fake_vector_store = fake_vector_store
        yield ac

    app.dependency_overrides.clear()
    await engine.dispose()
    await fake_redis.aclose()

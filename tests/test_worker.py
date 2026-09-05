from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

import app.worker as worker
from app.core.queue import QueueMessage
from app.db import Base
from app.models.tenant import Tenant
from tests.fakes import FakeObjectStorage, FakeVectorStore
from tests.test_ingestion_service import _make_document


async def _setup(monkeypatch):
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    session_maker = async_sessionmaker(engine, expire_on_commit=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    storage = FakeObjectStorage()
    vector_store = FakeVectorStore()

    monkeypatch.setattr(worker, "SessionLocal", session_maker)
    monkeypatch.setattr(worker, "get_storage", lambda: _async_return(storage))
    monkeypatch.setattr(worker, "get_vector_store", lambda: vector_store)

    return engine, session_maker, storage, vector_store


async def _async_return(value):
    return value


async def test_handle_success_returns_true_and_indexes(monkeypatch):
    engine, session_maker, storage, vector_store = await _setup(monkeypatch)
    async with session_maker() as db:
        document = await _make_document(db)
    storage.objects[document.storage_key] = b"some ingestible text content here"

    message = QueueMessage(
        body={
            "document_id": str(document.id),
            "tenant_id": str(document.tenant_id),
            "storage_key": document.storage_key,
        },
        receipt_handle="rh-1",
    )

    handled = await worker._handle(message)

    assert handled is True
    assert len(vector_store.added) >= 1
    await engine.dispose()


async def test_handle_malformed_message_returns_true_to_drop_it(monkeypatch):
    await _setup(monkeypatch)

    message = QueueMessage(body={"not": "valid"}, receipt_handle="rh-2")

    handled = await worker._handle(message)

    assert handled is True


async def test_handle_missing_document_is_a_noop_not_a_retry(monkeypatch):
    engine, session_maker, storage, vector_store = await _setup(monkeypatch)
    async with session_maker() as db:
        tenant = Tenant(name="Acme", slug="acme")
        db.add(tenant)
        await db.flush()
        await db.commit()

    message = QueueMessage(
        body={
            "document_id": "00000000-0000-0000-0000-000000000000",
            "tenant_id": str(tenant.id),
            "storage_key": "missing",
        },
        receipt_handle="rh-3",
    )

    # document_id doesn't exist -> ingest_document logs + returns (no-op),
    # which _handle treats as handled (True), not a failure to retry.
    handled = await worker._handle(message)

    assert handled is True
    await engine.dispose()


async def test_handle_ingestion_failure_returns_false_to_retry(monkeypatch):
    engine, session_maker, storage, vector_store = await _setup(monkeypatch)
    async with session_maker() as db:
        document = await _make_document(db)
    # storage_key never registered in the fake -> get_object raises KeyError
    # inside ingest_document, which _handle must treat as a retryable failure.

    message = QueueMessage(
        body={
            "document_id": str(document.id),
            "tenant_id": str(document.tenant_id),
            "storage_key": document.storage_key,
        },
        receipt_handle="rh-4",
    )

    handled = await worker._handle(message)

    assert handled is False
    await engine.dispose()

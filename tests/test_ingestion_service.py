import uuid

import pytest
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.db import Base
from app.models.document import STATUS_FAILED, STATUS_INDEXED, Document
from app.models.tenant import Tenant
from app.services.ingestion_service import ingest_document
from tests.fakes import FakeObjectStorage, FakeVectorStore


@pytest.fixture
async def db_session():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    session_maker = async_sessionmaker(engine, expire_on_commit=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async with session_maker() as session:
        yield session
    await engine.dispose()


async def _make_document(db, content: bytes = b"hello world, this is a test document.") -> Document:
    tenant = Tenant(name="Acme", slug="acme")
    db.add(tenant)
    await db.flush()
    document = Document(
        tenant_id=tenant.id,
        filename="notes.txt",
        content_type="text/plain",
        size_bytes=len(content),
        storage_key="tenant/doc/notes.txt",
    )
    db.add(document)
    await db.commit()
    await db.refresh(document)
    return document


async def test_ingest_document_indexes_chunks_and_updates_status(db_session):
    document = await _make_document(db_session)
    storage = FakeObjectStorage()
    storage.objects[document.storage_key] = b"hello world, this is a test document."
    vector_store = FakeVectorStore()

    await ingest_document(
        document_id=document.id,
        tenant_id=document.tenant_id,
        storage_key=document.storage_key,
        db=db_session,
        storage=storage,
        vector_store=vector_store,
    )

    await db_session.refresh(document)
    assert document.status == STATUS_INDEXED
    assert len(vector_store.added) >= 1
    _text, metadata = vector_store.added[0]
    assert metadata["document_id"] == str(document.id)
    assert metadata["tenant_id"] == str(document.tenant_id)


async def test_ingest_document_masks_pii_before_indexing(db_session):
    document = await _make_document(db_session)
    storage = FakeObjectStorage()
    storage.objects[document.storage_key] = b"Contact Jane Doe at jane.doe@example.com for questions."
    vector_store = FakeVectorStore()

    await ingest_document(
        document_id=document.id,
        tenant_id=document.tenant_id,
        storage_key=document.storage_key,
        db=db_session,
        storage=storage,
        vector_store=vector_store,
    )

    await db_session.refresh(document)
    assert document.status == STATUS_INDEXED
    assert len(vector_store.added) >= 1
    indexed_text = " ".join(text for text, _meta in vector_store.added)
    assert "jane.doe@example.com" not in indexed_text
    assert "<EMAIL_ADDRESS>" in indexed_text


async def test_ingest_document_missing_document_is_noop(db_session):
    storage = FakeObjectStorage()
    vector_store = FakeVectorStore()

    await ingest_document(
        document_id=uuid.uuid4(),
        tenant_id=uuid.uuid4(),
        storage_key="whatever",
        db=db_session,
        storage=storage,
        vector_store=vector_store,
    )

    assert vector_store.added == []


async def test_ingest_document_storage_failure_marks_failed_and_raises(db_session):
    document = await _make_document(db_session)
    storage = FakeObjectStorage()  # nothing registered under storage_key -> get_object raises
    vector_store = FakeVectorStore()

    with pytest.raises(KeyError):
        await ingest_document(
            document_id=document.id,
            tenant_id=document.tenant_id,
            storage_key=document.storage_key,
            db=db_session,
            storage=storage,
            vector_store=vector_store,
        )

    await db_session.refresh(document)
    assert document.status == STATUS_FAILED

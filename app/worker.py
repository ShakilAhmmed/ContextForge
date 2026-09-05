"""Ingestion worker - consumes app/core/queue.py's document-ingestion queue and
runs app/services/ingestion_service.py for each message. Runs as its own
process/container (ops/docker/docker-compose.yml's `worker` service), separate
from the FastAPI api process, per docs/arch.md's Ingestion Workers design.

Run: python -m app.worker
"""

import asyncio
import logging
import uuid

from app.core.queue import QueueMessage, get_queue
from app.core.storage import get_storage
from app.core.vectorstore import get_vector_store
from app.db import SessionLocal
from app.services.ingestion_service import ingest_document

logger = logging.getLogger(__name__)

POLL_MAX_MESSAGES = 5
POLL_WAIT_SECONDS = 10


async def _handle(message: QueueMessage) -> bool:
    """Returns True if the message should be deleted from the queue (handled
    or permanently unrecoverable), False to leave it for redelivery/DLQ."""
    storage = await get_storage()
    vector_store = get_vector_store()

    try:
        document_id = uuid.UUID(message.body["document_id"])
        tenant_id = uuid.UUID(message.body["tenant_id"])
        storage_key = message.body["storage_key"]
    except (KeyError, ValueError):
        logger.exception("malformed ingestion message, dropping: %s", message.body)
        return True

    async with SessionLocal() as db:
        try:
            await ingest_document(
                document_id=document_id,
                tenant_id=tenant_id,
                storage_key=storage_key,
                db=db,
                storage=storage,
                vector_store=vector_store,
            )
            return True
        except Exception:
            # ingest_document already logged + marked the document failed;
            # leave the message so ElasticMQ/SQS's redrive policy retries it
            # up to maxReceiveCount before routing to the dead-letter queue.
            return False


async def run() -> None:
    queue = await get_queue()
    logger.info("ingestion worker started, polling for messages")
    while True:
        messages = await queue.receive_messages(POLL_MAX_MESSAGES, POLL_WAIT_SECONDS)
        for message in messages:
            if await _handle(message):
                await queue.delete_message(message.receipt_handle)
        if not messages:
            await asyncio.sleep(1)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(run())

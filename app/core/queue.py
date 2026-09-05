import json
from dataclasses import dataclass
from typing import Protocol

import aioboto3

from app.core.config import settings


@dataclass
class QueueMessage:
    body: dict
    receipt_handle: str


class QueueClient(Protocol):
    async def send_message(self, body: dict) -> None: ...

    async def receive_messages(self, max_messages: int, wait_seconds: int) -> list[QueueMessage]: ...

    async def delete_message(self, receipt_handle: str) -> None: ...


class SQSQueueClient:
    """SQS-compatible queue client - targets ElasticMQ in dev/docker-compose,
    real AWS SQS in production (same API, only endpoint/credentials change)."""

    def __init__(self) -> None:
        self._session = aioboto3.Session()

    def _client(self):
        return self._session.client(
            "sqs",
            endpoint_url=settings.sqs_endpoint_url,
            aws_access_key_id=settings.sqs_access_key,
            aws_secret_access_key=settings.sqs_secret_key,
            region_name=settings.sqs_region,
        )

    async def send_message(self, body: dict) -> None:
        async with self._client() as client:
            await client.send_message(QueueUrl=settings.sqs_ingestion_queue_url, MessageBody=json.dumps(body))

    async def receive_messages(self, max_messages: int, wait_seconds: int) -> list[QueueMessage]:
        async with self._client() as client:
            response = await client.receive_message(
                QueueUrl=settings.sqs_ingestion_queue_url,
                MaxNumberOfMessages=max_messages,
                WaitTimeSeconds=wait_seconds,
            )
        return [
            QueueMessage(body=json.loads(m["Body"]), receipt_handle=m["ReceiptHandle"])
            for m in response.get("Messages", [])
        ]

    async def delete_message(self, receipt_handle: str) -> None:
        async with self._client() as client:
            await client.delete_message(
                QueueUrl=settings.sqs_ingestion_queue_url, ReceiptHandle=receipt_handle
            )


_queue = SQSQueueClient()


async def get_queue() -> QueueClient:
    return _queue

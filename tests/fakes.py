from app.core.queue import QueueMessage


class FakeObjectStorage:
    """In-memory stand-in for app.core.storage.ObjectStorage - avoids needing a
    real MinIO/S3 in the fast test suite. Exposes `.objects` for assertions."""

    def __init__(self) -> None:
        self.objects: dict[str, bytes] = {}

    async def put_object(self, key: str, content: bytes, content_type: str) -> None:
        self.objects[key] = content

    async def get_object(self, key: str) -> bytes:
        return self.objects[key]

    async def ensure_bucket(self) -> None:
        pass


class FakeQueueClient:
    """In-memory stand-in for app.core.queue.QueueClient - avoids needing a
    real ElasticMQ/SQS in the fast test suite. Exposes `.messages` for assertions
    and a `.deleted` list of receipt handles that were acknowledged."""

    def __init__(self) -> None:
        self.messages: list[dict] = []
        self._pending: list[QueueMessage] = []
        self.deleted: list[str] = []

    async def send_message(self, body: dict) -> None:
        self.messages.append(body)
        self._pending.append(QueueMessage(body=body, receipt_handle=f"rh-{len(self.messages)}"))

    async def receive_messages(self, max_messages: int, wait_seconds: int) -> list[QueueMessage]:
        batch, self._pending = self._pending[:max_messages], self._pending[max_messages:]
        return batch

    async def delete_message(self, receipt_handle: str) -> None:
        self.deleted.append(receipt_handle)


class FakeVectorStore:
    """In-memory stand-in for langchain_qdrant.QdrantVectorStore - avoids needing
    a real Qdrant in the fast test suite. Exposes `.added` for assertions."""

    def __init__(self) -> None:
        self.added: list[tuple[str, dict]] = []

    async def aadd_texts(self, texts, metadatas=None) -> list[str]:
        metadatas = metadatas or [{} for _ in texts]
        self.added.extend(zip(texts, metadatas, strict=True))
        return [str(i) for i in range(len(self.added))]

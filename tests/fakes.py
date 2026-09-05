class FakeObjectStorage:
    """In-memory stand-in for app.core.storage.ObjectStorage - avoids needing a
    real MinIO/S3 in the fast test suite. Exposes `.objects` for assertions."""

    def __init__(self) -> None:
        self.objects: dict[str, bytes] = {}

    async def put_object(self, key: str, content: bytes, content_type: str) -> None:
        self.objects[key] = content

    async def ensure_bucket(self) -> None:
        pass


class FakeQueueClient:
    """In-memory stand-in for app.core.queue.QueueClient - avoids needing a
    real ElasticMQ/SQS in the fast test suite. Exposes `.messages` for assertions."""

    def __init__(self) -> None:
        self.messages: list[dict] = []

    async def send_message(self, body: dict) -> None:
        self.messages.append(body)

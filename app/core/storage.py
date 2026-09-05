from typing import Protocol

import aioboto3

from app.core.config import settings


class ObjectStorage(Protocol):
    async def put_object(self, key: str, content: bytes, content_type: str) -> None: ...

    async def get_object(self, key: str) -> bytes: ...

    async def ensure_bucket(self) -> None: ...


class S3ObjectStorage:
    """S3-compatible storage - targets MinIO in dev/docker-compose, real AWS S3 in
    production (same API, only endpoint/credentials change)."""

    def __init__(self) -> None:
        self._session = aioboto3.Session()

    def _client(self):
        return self._session.client(
            "s3",
            endpoint_url=settings.s3_endpoint_url,
            aws_access_key_id=settings.s3_access_key,
            aws_secret_access_key=settings.s3_secret_key,
            region_name=settings.s3_region,
        )

    async def put_object(self, key: str, content: bytes, content_type: str) -> None:
        async with self._client() as client:
            await client.put_object(
                Bucket=settings.s3_bucket, Key=key, Body=content, ContentType=content_type
            )

    async def get_object(self, key: str) -> bytes:
        async with self._client() as client:
            response = await client.get_object(Bucket=settings.s3_bucket, Key=key)
            async with response["Body"] as stream:
                return await stream.read()

    async def ensure_bucket(self) -> None:
        async with self._client() as client:
            try:
                await client.head_bucket(Bucket=settings.s3_bucket)
            except Exception:
                await client.create_bucket(Bucket=settings.s3_bucket)


_storage = S3ObjectStorage()


async def get_storage() -> ObjectStorage:
    return _storage

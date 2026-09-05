from functools import lru_cache

from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams

from app.core.config import settings
from app.core.embeddings import get_embeddings


@lru_cache
def get_vector_store() -> QdrantVectorStore:
    client = QdrantClient(url=settings.qdrant_url)
    if not client.collection_exists(settings.qdrant_collection):
        client.create_collection(
            collection_name=settings.qdrant_collection,
            vectors_config=VectorParams(size=settings.embedding_dimensions, distance=Distance.COSINE),
        )
    return QdrantVectorStore(
        client=client, collection_name=settings.qdrant_collection, embedding=get_embeddings()
    )

import uuid
from functools import lru_cache

from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, FieldCondition, Filter, MatchValue, VectorParams

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


def get_document_chunks(
    vector_store: QdrantVectorStore, document_id: uuid.UUID
) -> list[tuple[str, list[float]]]:
    """Payload-filtered scroll, not a similarity search - there's no query
    text here, just "give me every chunk indexed for this document",
    matching how the worker tagged each point's metadata at ingestion time.
    Takes `vector_store` as a parameter (rather than calling get_vector_store()
    itself) so callers can inject a fake in tests - see Depends(get_vector_store)
    in app/controllers/document_controller.py. Returns (text, vector) pairs -
    the vector is needed for the 2D projection shown in the chunk viewer."""
    points, _next_offset = vector_store.client.scroll(
        collection_name=settings.qdrant_collection,
        scroll_filter=Filter(
            must=[FieldCondition(key="metadata.document_id", match=MatchValue(value=str(document_id)))]
        ),
        with_payload=True,
        with_vectors=True,
        limit=1000,
    )
    return [(point.payload["page_content"], point.vector) for point in points if point.payload]

import asyncio
import uuid

from langchain_qdrant import QdrantVectorStore
from qdrant_client.http.models import FieldCondition, Filter, MatchValue
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.embeddings import get_embeddings
from app.core.llm import LLMProvider
from app.models.document import Document
from app.schemas.chat import ChatResponse, Citation


async def answer_question(
    *,
    question: str,
    tenant_id: uuid.UUID,
    db: AsyncSession,
    vector_store: QdrantVectorStore,
    llm: LLMProvider,
) -> ChatResponse:
    """Retrieval -> context -> LLM, tenant-filtered at the vector search
    itself (not just at citation time) - per docs/arch.md's "vector search
    mandatory tenant filter", a tenant must never even retrieve another
    tenant's chunks, regardless of what happens with them afterward."""
    embeddings = get_embeddings()
    query_vector = await asyncio.to_thread(embeddings.embed_query, question)

    results = await vector_store.asimilarity_search_by_vector(
        query_vector,
        k=settings.chat_top_k,
        filter=Filter(
            must=[FieldCondition(key="metadata.tenant_id", match=MatchValue(value=str(tenant_id)))]
        ),
    )

    context = "\n\n".join(result.page_content for result in results)
    answer = await llm.generate(question, context)

    citations: list[Citation] = []
    seen_document_ids: set[str] = set()
    for result in results:
        document_id = result.metadata.get("document_id")
        if not document_id or document_id in seen_document_ids:
            continue
        seen_document_ids.add(document_id)
        document = await db.get(Document, uuid.UUID(document_id))
        # Defensive, on top of the tenant-filtered search above: never cite a
        # document this lookup can't independently confirm belongs to the
        # asker's tenant (e.g. deleted since indexing).
        if document is not None and document.tenant_id == tenant_id:
            citations.append(
                Citation(document_id=document.id, filename=document.filename, chunk_text=result.page_content)
            )

    return ChatResponse(answer=answer, citations=citations)

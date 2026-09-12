from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.llm import LLMProvider, get_llm_provider
from app.core.rate_limit import rate_limit
from app.core.vectorstore import QdrantVectorStore, get_vector_store
from app.db import get_db
from app.models.user import User
from app.schemas.chat import ChatRequest, ChatResponse
from app.schemas.common import SuccessResponse
from app.services.chat_service import answer_question

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post(
    "/query",
    response_model=SuccessResponse[ChatResponse],
    dependencies=[Depends(rate_limit("chat", "rate_limit_chat", "rate_limit_chat_window_seconds"))],
)
async def query(
    payload: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    vector_store: QdrantVectorStore = Depends(get_vector_store),
    llm: LLMProvider = Depends(get_llm_provider),
) -> SuccessResponse[ChatResponse]:
    result = await answer_question(
        question=payload.question,
        tenant_id=current_user.tenant_id,
        db=db,
        vector_store=vector_store,
        llm=llm,
    )
    return SuccessResponse(data=result)

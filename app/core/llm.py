from functools import lru_cache
from typing import Protocol

from app.core.config import settings


class LLMProvider(Protocol):
    async def generate(self, question: str, context: str) -> str: ...


class MockLLMProvider:
    """Deterministic canned response, not a real model call - real
    Bedrock/Claude is deferred alongside real embeddings (see
    app/core/embeddings.py) pending the langchain-aws/aioboto3 botocore
    conflict. Exists so the retrieval -> context -> answer pipeline shape is
    real and testable now, with only this piece swapped in later."""

    async def generate(self, question: str, context: str) -> str:
        if not context.strip():
            return "I couldn't find anything in your documents relevant to that question."
        return (
            f"[mock answer - no real LLM wired up yet] Based on the retrieved passages, "
            f'here is the context relevant to "{question}":\n\n{context[:800]}'
        )


@lru_cache
def get_llm_provider() -> LLMProvider:
    if settings.llm_provider == "mock":
        return MockLLMProvider()

    if settings.llm_provider == "bedrock":
        raise NotImplementedError(
            "bedrock LLM provider not wired up yet - see app/core/embeddings.py's "
            "matching NotImplementedError for the langchain-aws/aioboto3 dependency conflict"
        )

    raise ValueError(f"unknown llm provider: {settings.llm_provider}")

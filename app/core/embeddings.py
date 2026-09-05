from functools import lru_cache

from langchain_core.embeddings import Embeddings

from app.core.config import settings


@lru_cache
def get_embeddings() -> Embeddings:
    """Provider is swappable via EMBEDDING_PROVIDER without touching calling
    code - both the worker and any future retrieval path just depend on
    Embeddings (langchain_core), not on a specific provider."""
    if settings.embedding_provider == "mock":
        from langchain_community.embeddings import FakeEmbeddings

        return FakeEmbeddings(size=settings.embedding_dimensions)

    if settings.embedding_provider == "bedrock":
        # Deferred: requires `langchain-aws` (not installed - it pins a newer
        # botocore than aiobotocore tolerates, see pyproject.toml) plus real
        # AWS credentials/region. Swap in when ready:
        #   from langchain_aws import BedrockEmbeddings
        #   return BedrockEmbeddings(model_id=settings.bedrock_embedding_model)
        raise NotImplementedError(
            "bedrock embedding provider not wired up yet - install langchain-aws "
            "(resolve its botocore version against aioboto3 first) and implement here"
        )

    raise ValueError(f"unknown embedding provider: {settings.embedding_provider}")

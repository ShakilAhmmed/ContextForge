from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    env: str = "local"
    database_url: str = "postgresql+asyncpg://contextforge:contextforge@postgres:5432/contextforge"

    jwt_secret: str = "dev-secret-change-me-32-bytes-minimum"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60

    redis_url: str = "redis://redis:6379/0"

    s3_endpoint_url: str = "http://minio:9000"
    s3_access_key: str = "minioadmin"
    s3_secret_key: str = "minioadmin"
    s3_bucket: str = "contextforge-documents"
    s3_region: str = "us-east-1"
    max_upload_size_bytes: int = 20 * 1024 * 1024

    sqs_endpoint_url: str = "http://elasticmq:9324"
    sqs_access_key: str = "x"
    sqs_secret_key: str = "x"
    sqs_region: str = "us-east-1"
    sqs_ingestion_queue_url: str = "http://elasticmq:9324/000000000000/document-ingestion"

    # "mock" (langchain_community.embeddings.FakeEmbeddings, no AWS needed) or
    # "bedrock" (langchain_aws.BedrockEmbeddings - requires that package added
    # and real AWS credentials; not wired up yet, see app/core/embeddings.py).
    embedding_provider: str = "mock"
    embedding_dimensions: int = 384
    bedrock_embedding_model: str = "amazon.titan-embed-text-v2:0"

    qdrant_url: str = "http://qdrant:6333"
    qdrant_collection: str = "documents"

    chunk_size: int = 1000
    chunk_overlap: int = 200

    # "mock" (canned response referencing retrieved context, no AWS needed) or
    # "bedrock" (Claude via Bedrock - not wired up yet, same blocker as
    # embedding_provider: langchain-aws's botocore pin conflicts with
    # aioboto3's, see app/core/embeddings.py). See app/core/llm.py.
    llm_provider: str = "mock"
    chat_top_k: int = 5

    rate_limit_default: int = 100
    rate_limit_default_window_seconds: int = 60
    rate_limit_login: int = 5
    rate_limit_login_window_seconds: int = 60
    rate_limit_chat: int = 20
    rate_limit_chat_window_seconds: int = 60

    # Comma-separated, not a JSON list, to keep the env var trivial to set.
    # Frontend is a separate origin (its own Docker setup, not this compose
    # stack) so the browser calls the API cross-origin - needs CORS.
    cors_allowed_origins: str = "http://localhost:5173,http://localhost:3000,http://localhost:8082"

    @property
    def cors_allowed_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_allowed_origins.split(",") if origin.strip()]

    # Browser auth: JWT in an httpOnly cookie (immune to XSS reading it via
    # localStorage/JS). SameSite=None cross-site cookies are sent
    # automatically by the browser, so a plain httpOnly cookie alone is
    # forgeable via CSRF - mitigated by requiring csrf_header_name present on
    # unsafe methods (see app/api/deps.py). A double-submit *cookie* value
    # doesn't work here: frontend and backend are different domains, so the
    # frontend's JS cannot read a cookie the backend's domain set at all
    # (document.cookie is same-origin only) - presence of a custom header is
    # itself the defense, since CORS already blocks a disallowed origin's
    # browser from attaching custom headers to a credentialed request in the
    # first place. Header-based Bearer auth still works unchanged for
    # tests/API clients and skips this check (no ambient cookie involved).
    access_token_cookie_name: str = "access_token"
    csrf_header_name: str = "X-CSRF-Token"
    cookie_secure: bool = True


settings = Settings()

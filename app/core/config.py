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

    rate_limit_default: int = 100
    rate_limit_default_window_seconds: int = 60
    rate_limit_login: int = 5
    rate_limit_login_window_seconds: int = 60


settings = Settings()

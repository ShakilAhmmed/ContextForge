from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    env: str = "local"
    database_url: str = "postgresql+asyncpg://contextforge:contextforge@postgres:5432/contextforge"

    jwt_secret: str = "dev-secret-change-me-32-bytes-minimum"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60

    redis_url: str = "redis://redis:6379/0"
    rate_limit_default: int = 100
    rate_limit_default_window_seconds: int = 60
    rate_limit_login: int = 5
    rate_limit_login_window_seconds: int = 60


settings = Settings()

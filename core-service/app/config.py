from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Centralised env-driven config. Defaults match docker-compose service names
    so the same code runs unmodified in Docker and against `localhost` overrides
    in a local .env during development."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+psycopg://shortener:shortener@localhost:5432/shortener"
    redis_url: str = "redis://localhost:6379/0"
    rabbitmq_url: str = "amqp://guest:guest@localhost:5672/"

    base_host: str = "http://localhost:8000"
    short_code_length: int = 7
    short_code_max_attempts: int = 5

    analytics_service_url: str = "http://localhost:8081"
    analytics_request_timeout_seconds: float = 2.0

    # Comma-separated list; the frontend runs on a different origin
    # (Vite dev server / its own static host) so the browser enforces CORS.
    cors_allowed_origins: str = "http://localhost:5173"


settings = Settings()

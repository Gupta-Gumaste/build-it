"""Application configuration, loaded from environment variables."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Settings read from the environment or a `.env` file."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Supabase client credentials. All database access goes through the
    # Supabase client library, never a direct Postgres connection.
    supabase_url: str
    supabase_publishable_key: str
    supabase_secret_key: str
    supabase_jwks_url: str

    # Redis connection, used by the background job workers.
    redis_url: str = "redis://localhost:6379/0"

    # Which AI provider app.services.llm routes calls to: "anthropic" or "gemini".
    ai_provider: str = "gemini"
    anthropic_api_key: str = ""
    anthropic_model: str = "claude-sonnet-5"
    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.5-pro"

    # Comma-separated list of origins allowed to call this API.
    cors_origins: str = "http://localhost:3000"

    @property
    def cors_origins_list(self) -> list[str]:
        """Return `cors_origins` split into a list of individual origins."""
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


settings = Settings()

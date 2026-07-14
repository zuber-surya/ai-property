"""Application settings. The ONLY place env vars are read."""

from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """All configuration. Secrets come from the environment — never hardcoded."""

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    environment: Literal["local", "staging", "production"] = "local"
    log_level: str = "INFO"

    # Database — SQLAlchemy talks to Postgres directly (ADR-0005).
    # asyncpg, not psycopg2: a sync driver blocks the event loop on every query.
    supabase_postgres_url: str = (
        "postgresql+asyncpg://postgres:password@localhost:5432/propvista"
    )

    # Supabase — Auth and Storage ONLY. Never data access.
    supabase_url: str = ""
    supabase_anon_key: str = ""
    # Bypasses RLS. Migrations and admin tooling only; must never reach the
    # frontend or a request path serving a tenant user.
    supabase_service_key: str = ""

    # Bedrock. ⚠️ The region is blocked on gap I1 — see docs/GAPS.md.
    aws_region: str = "ap-south-1"
    aws_access_key_id: str = ""
    aws_secret_access_key: str = ""
    bedrock_model_id: str = ""
    bedrock_embedding_model_id: str = "amazon.titan-embed-text-v2:0"


@lru_cache
def get_settings() -> Settings:
    """Cached so the env is read once per process."""
    return Settings()

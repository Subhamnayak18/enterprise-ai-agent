from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Enterprise AI Knowledge & Workflow Agent"
    app_version: str = "1.0.0"
    environment: Literal["development", "test", "production"] = "development"
    log_level: str = "INFO"

    database_url: str = "sqlite:///./data/local.db"
    database_connect_timeout_seconds: int = 3
    database_pool_size: int = 5
    database_max_overflow: int = 10
    sql_query_timeout_ms: int = 5000
    sql_row_limit: int = 100

    llm_provider: str = "openai"
    openai_api_key: str | None = None
    openai_chat_model: str = "gpt-4.1-mini"
    openai_embedding_model: str = "text-embedding-3-small"
    llm_temperature: float = 0.0

    chroma_path: Path = Path("./data/processed/chroma")
    documents_path: Path = Path("./data/documents")
    upload_max_mb: int = 5
    retrieval_top_k: int = 4
    retrieval_score_threshold: float = 0.25

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()

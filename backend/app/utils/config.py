from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = "development"
    app_name: str = "DocuChat Copilot"
    api_v1_prefix: str = "/"
    cors_origins: list[str] = Field(default_factory=lambda: ["http://localhost:5173"])

    gemini_api_key: str = ""
    gemini_chat_model: str = "gemini-2.5-flash"
    gemini_embedding_model: str = "gemini-embedding-001"

    local_storage_path: str = "./app/data/uploads"

    chroma_persist_directory: str = "./app/data/chroma"
    chroma_collection_name: str = "docuchat_chunks"

    redis_url: str | None = None
    chat_memory_window: int = 10

    jwt_secret_key: str | None = None
    jwt_algorithm: str = "HS256"

    chunk_size_tokens: int = 800
    chunk_overlap_tokens: int = 100
    embedding_batch_size: int = 32
    retrieval_top_k: int = 6

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()

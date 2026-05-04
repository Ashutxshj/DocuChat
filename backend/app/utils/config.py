from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = "development"
    app_name: str = "DocuChat Copilot"
    api_v1_prefix: str = "/"
    cors_origins: list[str] = Field(default_factory=lambda: ["http://localhost:5173"])

    openai_api_key: str = ""
    openai_chat_model: str = "gpt-4.1-mini"
    openai_embedding_model: str = "text-embedding-3-small"

    aws_region: str = "us-east-1"
    aws_access_key_id: str = ""
    aws_secret_access_key: str = ""
    s3_bucket_name: str = ""
    s3_key_prefix: str = "documents"
    presigned_url_expiry_seconds: int = 900

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

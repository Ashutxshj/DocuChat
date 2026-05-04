from __future__ import annotations

from openai import AsyncOpenAI

from app.utils.config import get_settings


class EmbeddingService:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.client: AsyncOpenAI | None = None

    def _get_client(self) -> AsyncOpenAI:
        if not self.settings.openai_api_key:
            raise ValueError("OPENAI_API_KEY is not configured")
        if self.client is None:
            self.client = AsyncOpenAI(api_key=self.settings.openai_api_key)
        return self.client

    async def embed_texts(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []

        client = self._get_client()
        results: list[list[float]] = []
        batch_size = self.settings.embedding_batch_size

        for index in range(0, len(texts), batch_size):
            batch = texts[index : index + batch_size]
            response = await client.embeddings.create(
                model=self.settings.openai_embedding_model,
                input=batch,
            )
            results.extend(item.embedding for item in response.data)

        return results


embedding_service = EmbeddingService()

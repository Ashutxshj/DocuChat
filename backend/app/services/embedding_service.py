from __future__ import annotations

import asyncio

from google import genai
from google.genai import types

from app.utils.config import get_settings


class EmbeddingService:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.client: genai.Client | None = None

    def _get_client(self) -> genai.Client:
        if not self.settings.gemini_api_key:
            raise ValueError("GEMINI_API_KEY is not configured")
        if self.client is None:
            self.client = genai.Client(api_key=self.settings.gemini_api_key)
        return self.client

    async def embed_texts(self, texts: list[str], task_type: str = "RETRIEVAL_DOCUMENT") -> list[list[float]]:
        if not texts:
            return []

        client = self._get_client()
        results: list[list[float]] = []
        batch_size = self.settings.embedding_batch_size

        for index in range(0, len(texts), batch_size):
            batch = texts[index : index + batch_size]
            response = await asyncio.to_thread(
                client.models.embed_content,
                model=self.settings.gemini_embedding_model,
                contents=batch,
                config=types.EmbedContentConfig(task_type=task_type),
            )
            results.extend(item.values for item in response.embeddings)

        return results


embedding_service = EmbeddingService()

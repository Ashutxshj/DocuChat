from __future__ import annotations

import asyncio
from typing import Any

import chromadb

from app.utils.config import get_settings


class VectorStoreService:
    def __init__(self) -> None:
        settings = get_settings()
        self.client = chromadb.PersistentClient(path=settings.chroma_persist_directory)
        self.collection = self.client.get_or_create_collection(name=settings.chroma_collection_name)

    async def upsert_chunks(
        self,
        ids: list[str],
        documents: list[str],
        embeddings: list[list[float]],
        metadatas: list[dict[str, Any]],
    ) -> None:
        await asyncio.to_thread(
            self.collection.upsert,
            ids=ids,
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas,
        )

    async def delete_document(self, user_id: str, doc_id: str) -> None:
        await asyncio.to_thread(
            self.collection.delete,
            where={"$and": [{"user_id": user_id}, {"doc_id": doc_id}]},
        )

    async def query(
        self,
        query_embedding: list[float],
        user_id: str,
        doc_ids: list[str],
        top_k: int,
    ) -> list[dict[str, Any]]:
        where: dict[str, Any] = {"user_id": user_id}
        if doc_ids:
            where = {"$and": [{"user_id": user_id}, {"doc_id": {"$in": doc_ids}}]}

        result = await asyncio.to_thread(
            self.collection.query,
            query_embeddings=[query_embedding],
            n_results=top_k,
            where=where,
        )

        ids = result.get("ids", [[]])[0]
        documents = result.get("documents", [[]])[0]
        metadatas = result.get("metadatas", [[]])[0]
        distances = result.get("distances", [[]])[0] if result.get("distances") else []

        matches: list[dict[str, Any]] = []
        for index, chunk_id in enumerate(ids):
            matches.append(
                {
                    "id": chunk_id,
                    "document": documents[index],
                    "metadata": metadatas[index],
                    "distance": distances[index] if index < len(distances) else None,
                }
            )
        return matches


vector_store_service = VectorStoreService()

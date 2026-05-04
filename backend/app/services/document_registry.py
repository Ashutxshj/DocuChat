from __future__ import annotations

import asyncio
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class DocumentRegistry:
    def __init__(self) -> None:
        self.path = Path(__file__).resolve().parents[1] / "data" / "documents.json"
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self.path.write_text("{}", encoding="utf-8")
        self.lock = asyncio.Lock()

    async def _read(self) -> dict[str, Any]:
        return json.loads(self.path.read_text(encoding="utf-8"))

    async def _write(self, payload: dict[str, Any]) -> None:
        self.path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    async def create_document(self, doc_id: str, user_id: str, filename: str, file_path: str, status: str) -> dict[str, Any]:
        async with self.lock:
            documents = await self._read()
            timestamp = datetime.now(timezone.utc).isoformat()
            documents[doc_id] = {
                "doc_id": doc_id,
                "user_id": user_id,
                "filename": filename,
                "file_path": file_path,
                "status": status,
                "created_at": timestamp,
                "updated_at": timestamp,
                "page_count": None,
                "chunk_count": None,
                "error": None,
            }
            await self._write(documents)
            return documents[doc_id]

    async def update_document(self, doc_id: str, **updates: Any) -> dict[str, Any] | None:
        async with self.lock:
            documents = await self._read()
            document = documents.get(doc_id)
            if not document:
                return None
            document.update(updates)
            document["updated_at"] = datetime.now(timezone.utc).isoformat()
            documents[doc_id] = document
            await self._write(documents)
            return document

    async def get_document(self, doc_id: str) -> dict[str, Any] | None:
        async with self.lock:
            documents = await self._read()
            return documents.get(doc_id)


document_registry = DocumentRegistry()

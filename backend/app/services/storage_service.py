from __future__ import annotations

import asyncio
from pathlib import Path

from fastapi import UploadFile

from app.utils.config import get_settings


class StorageService:
    def __init__(self) -> None:
        settings = get_settings()
        self.base_path = Path(settings.local_storage_path)
        self.base_path.mkdir(parents=True, exist_ok=True)

    async def save_upload(self, user_id: str, doc_id: str, file: UploadFile) -> str:
        filename = file.filename or "document.pdf"
        user_dir = self.base_path / user_id / doc_id
        user_dir.mkdir(parents=True, exist_ok=True)
        target = user_dir / filename.replace(" ", "_")
        content = await file.read()
        await asyncio.to_thread(target.write_bytes, content)
        return str(target)

    async def read_file_bytes(self, file_path: str) -> bytes:
        path = Path(file_path)
        return await asyncio.to_thread(path.read_bytes)


storage_service = StorageService()

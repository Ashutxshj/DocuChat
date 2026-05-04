from __future__ import annotations

import logging
from uuid import uuid4

from fastapi import BackgroundTasks, HTTPException, UploadFile

from app.models.schemas import ProcessRequest, ProcessResponse, UploadResponse
from app.services.document_registry import document_registry
from app.services.embedding_service import embedding_service
from app.services.pdf_service import pdf_service
from app.services.storage_service import storage_service
from app.services.vector_store import vector_store_service
from app.utils.config import get_settings

logger = logging.getLogger(__name__)


class DocumentService:
    def __init__(self) -> None:
        self.settings = get_settings()

    async def upload_document(self, file: UploadFile, user_id: str) -> UploadResponse:
        if file.content_type != "application/pdf":
            raise HTTPException(status_code=400, detail="Only PDF uploads are supported")

        doc_id = str(uuid4())
        file_path = await storage_service.save_upload(user_id, doc_id, file)
        await document_registry.create_document(
            doc_id=doc_id,
            user_id=user_id,
            filename=file.filename or "document.pdf",
            file_path=file_path,
            status="uploaded",
        )
        return UploadResponse(
            doc_id=doc_id,
            file_path=file_path,
            filename=file.filename or "document.pdf",
            status="uploaded",
        )

    async def schedule_processing(
        self,
        payload: ProcessRequest,
        user_id: str,
        background_tasks: BackgroundTasks,
    ) -> ProcessResponse:
        document = await document_registry.get_document(payload.doc_id)
        if not document or document["user_id"] != user_id:
            raise HTTPException(status_code=404, detail="Document not found")

        if payload.async_processing:
            background_tasks.add_task(self.process_document, payload, user_id)
            await document_registry.update_document(payload.doc_id, status="queued", error=None)
            return ProcessResponse(
                doc_id=payload.doc_id,
                status="queued",
                message="Document processing started in background",
            )

        await self.process_document(payload, user_id, raise_on_error=True)
        return ProcessResponse(
            doc_id=payload.doc_id,
            status="completed",
            message="Document processed successfully",
        )

    async def process_document(self, payload: ProcessRequest, user_id: str, raise_on_error: bool = False) -> None:
        await document_registry.update_document(payload.doc_id, status="processing", error=None)
        try:
            await vector_store_service.delete_document(user_id=user_id, doc_id=payload.doc_id)
            pdf_bytes = await storage_service.read_file_bytes(payload.file_path)
            pages = pdf_service.extract_pages(pdf_bytes)
            chunks = pdf_service.chunk_pages(pages)

            if not chunks:
                raise ValueError("No extractable text found in PDF")

            embeddings = await embedding_service.embed_texts(
                [chunk["content"] for chunk in chunks],
                task_type="RETRIEVAL_DOCUMENT",
            )
            ids = [f"{payload.doc_id}:{chunk['page_no']}:{chunk['chunk_index']}" for chunk in chunks]
            metadatas = [
                {
                    "doc_id": payload.doc_id,
                    "user_id": user_id,
                    "filename": payload.filename,
                    "page_no": chunk["page_no"],
                    "chunk_index": chunk["chunk_index"],
                    "token_count": chunk["token_count"],
                }
                for chunk in chunks
            ]
            await vector_store_service.upsert_chunks(
                ids=ids,
                documents=[str(chunk["content"]) for chunk in chunks],
                embeddings=embeddings,
                metadatas=metadatas,
            )
            await document_registry.update_document(
                payload.doc_id,
                status="completed",
                page_count=len(pages),
                chunk_count=len(chunks),
                error=None,
            )
        except Exception as exc:
            logger.exception("Failed to process document %s", payload.doc_id)
            await document_registry.update_document(payload.doc_id, status="failed", error=str(exc))
            if raise_on_error:
                raise


document_service = DocumentService()

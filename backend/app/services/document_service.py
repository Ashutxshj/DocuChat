from __future__ import annotations

import logging
from uuid import uuid4

from fastapi import BackgroundTasks, HTTPException

from app.models.schemas import ProcessRequest, ProcessResponse, UploadInitRequest, UploadInitResponse
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

    async def initialize_upload(self, payload: UploadInitRequest, user_id: str) -> UploadInitResponse:
        if payload.content_type != "application/pdf":
            raise HTTPException(status_code=400, detail="Only PDF uploads are supported")
        if not self.settings.s3_bucket_name:
            raise HTTPException(status_code=500, detail="S3 bucket is not configured")

        doc_id = str(uuid4())
        sanitized_filename = payload.filename.replace(" ", "_")
        s3_key = f"{self.settings.s3_key_prefix}/{user_id}/{doc_id}/{sanitized_filename}"
        upload_url = await storage_service.create_upload_url(s3_key, payload.content_type)
        await document_registry.create_document(
            doc_id=doc_id,
            user_id=user_id,
            filename=payload.filename,
            s3_key=s3_key,
            status="upload_pending",
        )
        return UploadInitResponse(
            doc_id=doc_id,
            s3_key=s3_key,
            upload_url=upload_url,
            expires_in=self.settings.presigned_url_expiry_seconds,
            status="upload_pending",
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
            pdf_bytes = await storage_service.download_file_bytes(payload.s3_key)
            pages = pdf_service.extract_pages(pdf_bytes)
            chunks = pdf_service.chunk_pages(pages)

            if not chunks:
                raise ValueError("No extractable text found in PDF")

            embeddings = await embedding_service.embed_texts([chunk["content"] for chunk in chunks])
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

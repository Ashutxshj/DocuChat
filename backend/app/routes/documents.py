from fastapi import APIRouter, Depends, HTTPException

from app.models.schemas import DocumentStatusResponse
from app.services.document_registry import document_registry
from app.utils.dependencies import get_current_user_id

router = APIRouter()


@router.get("/{doc_id}", response_model=DocumentStatusResponse)
async def get_document_status(
    doc_id: str,
    user_id: str = Depends(get_current_user_id),
) -> DocumentStatusResponse:
    document = await document_registry.get_document(doc_id)
    if not document or document["user_id"] != user_id:
        raise HTTPException(status_code=404, detail="Document not found")
    return DocumentStatusResponse(**document)

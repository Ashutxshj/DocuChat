from fastapi import APIRouter, Depends, File, UploadFile

from app.models.schemas import UploadResponse
from app.services.document_service import document_service
from app.utils.dependencies import get_current_user_id

router = APIRouter()


@router.post("", response_model=UploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    user_id: str = Depends(get_current_user_id),
) -> UploadResponse:
    return await document_service.upload_document(file, user_id)

from fastapi import APIRouter, Depends

from app.models.schemas import UploadInitRequest, UploadInitResponse
from app.services.document_service import document_service
from app.utils.dependencies import get_current_user_id

router = APIRouter()


@router.post("", response_model=UploadInitResponse)
async def initialize_upload(
    payload: UploadInitRequest,
    user_id: str = Depends(get_current_user_id),
) -> UploadInitResponse:
    return await document_service.initialize_upload(payload, user_id)

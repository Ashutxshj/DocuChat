from fastapi import APIRouter, BackgroundTasks, Depends

from app.models.schemas import ProcessRequest, ProcessResponse
from app.services.document_service import document_service
from app.utils.dependencies import get_current_user_id

router = APIRouter()


@router.post("", response_model=ProcessResponse)
async def process_document(
    payload: ProcessRequest,
    background_tasks: BackgroundTasks,
    user_id: str = Depends(get_current_user_id),
) -> ProcessResponse:
    return await document_service.schedule_processing(
        payload=payload,
        user_id=user_id,
        background_tasks=background_tasks,
    )

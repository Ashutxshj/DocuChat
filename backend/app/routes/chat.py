from fastapi import APIRouter, Depends

from app.models.schemas import ChatRequest, ChatResponse
from app.services.chat_service import chat_service
from app.utils.dependencies import get_current_user_id

router = APIRouter()


@router.post("", response_model=ChatResponse)
async def chat_with_documents(
    payload: ChatRequest,
    user_id: str = Depends(get_current_user_id),
) -> ChatResponse:
    return await chat_service.answer_question(payload, user_id)

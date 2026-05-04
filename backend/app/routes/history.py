from fastapi import APIRouter, Depends, Query

from app.models.schemas import ChatHistoryResponse
from app.services.chat_memory import chat_memory_service
from app.utils.dependencies import get_current_user_id

router = APIRouter()


@router.get("", response_model=ChatHistoryResponse)
async def get_history(
    session_id: str = Query(..., min_length=1),
    limit: int = Query(20, ge=1, le=100),
    user_id: str = Depends(get_current_user_id),
) -> ChatHistoryResponse:
    messages = await chat_memory_service.get_history(user_id=user_id, session_id=session_id, limit=limit)
    return ChatHistoryResponse(session_id=session_id, messages=messages)

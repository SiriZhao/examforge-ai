from fastapi import APIRouter

from app.schemas.review import ChatRequest, ChatResponse
from app.services.chat_service import answer_review_question

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    return ChatResponse(
        reply=answer_review_question(request.message, request.review_report)
    )

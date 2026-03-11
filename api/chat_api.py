import logging

from fastapi import APIRouter, HTTPException

from ai_engine.llm_engine import call_model
from prompts.prompts import CHAT_SYSTEM
from schemas.request_schema import ChatRequest, ChatResponse

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Medical Chatbot"])


@router.post("/medical-chat", response_model=ChatResponse)
def medical_chat(request: ChatRequest):
    """
    Answers general health questions in 2-3 sentences.
    Responds in the same language the user writes in.
    """
    if not request.message.strip():
        raise HTTPException(status_code=400, detail="The 'message' field cannot be empty.")

    try:
        response_text = call_model(
            prompt=request.message.strip(),
            system_instruction=CHAT_SYSTEM,
        )
        return ChatResponse(response=response_text)
    except Exception as exc:
        logger.error("Chat response failed: %s", exc)
        raise HTTPException(
            status_code=500,
            detail="Could not process your message. Please try again later.",
        )

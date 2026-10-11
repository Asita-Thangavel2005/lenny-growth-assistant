import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.api.schemas import ChatRequest, ChatResponse
from backend.app.core.database import get_db
from backend.app.services.chat_service import chat
from backend.app.services.llm_service import LLMServiceError

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chat", tags=["Chat"])

DatabaseSession = Annotated[AsyncSession, Depends(get_db)]


@router.post("", response_model=ChatResponse)
async def send_chat_message(
    request: ChatRequest,
    db: DatabaseSession,
):
    try:
        return await chat(
            db=db,
            session_id=request.session_id,
            question=request.question,
            provider=request.provider,
        )
    except ValueError as exc:
        status_code = 404 if str(exc) == "Chat session not found." else 400
        raise HTTPException(
            status_code=status_code,
            detail=str(exc),
        ) from exc
    except LLMServiceError as exc:
        logger.error("Chat generation failed: %s", exc)
        raise HTTPException(
            status_code=502,
            detail="The language model could not generate a response.",
        ) from exc
    except Exception as exc:
        logger.exception("Unexpected chat endpoint failure")
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred while processing the message.",
        ) from exc

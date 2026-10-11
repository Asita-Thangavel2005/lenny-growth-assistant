
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from backend.app.core.database import get_db
from backend.app.api.schemas import MessageResponse, SessionCreateRequest, SessionResponse
from backend.app.services.message_service import get_session_messages
from backend.app.services.session_service import create_session, get_session, list_sessions
from backend.app.models.session import ChatSession
router = APIRouter(prefix="/sessions", tags=["Sessions"])

DatabaseSession = Annotated[AsyncSession, Depends(get_db)]


@router.get("", response_model=list[SessionResponse])
async def list_chat_sessions(
    db: DatabaseSession,
):
    from backend.app.services.session_service import list_sessions

    return await list_sessions(db)


@router.post(
    "",
    response_model=SessionResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_chat_session(
    request: SessionCreateRequest,
    db: DatabaseSession,
):
    session = await create_session(
        db=db,
        title=request.title,
        user_metadata=request.user_metadata,
    )
    return session


@router.get("/{session_id}", response_model=SessionResponse)
async def read_chat_session(
    session_id: UUID,
    db: DatabaseSession,
):
    session = await get_session(db, session_id)

    if session is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat session not found.",
        )

    return session


@router.get("/{session_id}/messages", response_model=list[MessageResponse])
async def read_chat_session_messages(
    session_id: UUID,
    db: DatabaseSession,
):
    session = await get_session(db, session_id)

    if session is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat session not found.",
        )

    return await get_session_messages(db, session_id)






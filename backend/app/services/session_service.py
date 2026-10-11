
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.session import ChatSession


async def create_session(
    db: AsyncSession,
    title: str = "New conversation",
    user_metadata: dict | None = None,
) -> ChatSession:
    session = ChatSession(
        title=title,
        user_metadata=user_metadata or {},
    )
    db.add(session)
    await db.commit()
    await db.refresh(session)
    return session


async def get_session(
    db: AsyncSession,
    session_id: uuid.UUID,
) -> ChatSession | None:
    result = await db.execute(
        select(ChatSession).where(ChatSession.id == session_id)
    )
    return result.scalar_one_or_none()

async def list_sessions(
    db: AsyncSession,
) -> list[ChatSession]:
    result = await db.execute(
        select(ChatSession).order_by(ChatSession.updated_at.desc())
    )
    return list(result.scalars().all())
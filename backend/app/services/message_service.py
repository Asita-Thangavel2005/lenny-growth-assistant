
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.message import ChatMessage


async def save_message(
    db: AsyncSession,
    session_id: uuid.UUID,
    role: str,
    content: str,
    message_metadata: dict | None = None,
) -> ChatMessage:
    if role not in {"user", "assistant", "system"}:
        raise ValueError("role must be user, assistant, or system")

    message = ChatMessage(
        session_id=session_id,
        role=role,
        content=content,
        message_metadata=message_metadata or {},
    )
    db.add(message)
    await db.commit()
    await db.refresh(message)
    return message


async def get_session_messages(
    db: AsyncSession,
    session_id: uuid.UUID,
) -> list[ChatMessage]:
    result = await db.execute(
        select(ChatMessage)
        .where(ChatMessage.session_id == session_id)
        .order_by(ChatMessage.created_at, ChatMessage.id)
    )
    return list(result.scalars().all())

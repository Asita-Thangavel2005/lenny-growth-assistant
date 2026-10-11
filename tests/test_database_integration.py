import pytest
from sqlalchemy import select

from backend.app.core.database import AsyncSessionLocal
from backend.app.models.session import ChatSession
from backend.app.models.message import ChatMessage
from backend.app.services.session_service import create_session, get_session
from backend.app.services.message_service import save_message, get_session_messages


@pytest.mark.anyio
async def test_session_and_messages_persist_in_postgres():
    session_id = None

    try:
        async with AsyncSessionLocal() as db:
            session = await create_session(
                db=db,
                title="Integration test session",
                user_metadata={"test": True, "provider": "local"},
            )
            session_id = session.id

            user_message = await save_message(
                db=db,
                session_id=session.id,
                role="user",
                content="How can I improve retention?",
                message_metadata={"test_message": True},
            )

            assistant_message = await save_message(
                db=db,
                session_id=session.id,
                role="assistant",
                content="Start by measuring activation.",
                message_metadata={"sources": [], "provider": "local"},
            )

            assert user_message.id is not None
            assert assistant_message.id is not None

        async with AsyncSessionLocal() as db:
            stored_session = await get_session(db, session_id)
            assert stored_session is not None
            assert stored_session.title == "Integration test session"
            assert stored_session.user_metadata == {
                "test": True,
                "provider": "local",
            }

            messages = await get_session_messages(db, session_id)

            assert len(messages) == 2
            assert messages[0].role == "user"
            assert messages[0].content == "How can I improve retention?"
            assert messages[0].message_metadata == {"test_message": True}
            assert messages[1].role == "assistant"
            assert messages[1].content == "Start by measuring activation."
            assert messages[1].message_metadata == {
                "sources": [],
                "provider": "local",
            }

    finally:
        if session_id is not None:
            async with AsyncSessionLocal() as db:
                await db.execute(
                    select(ChatSession).where(ChatSession.id == session_id)
                )
                await db.execute(
                    ChatMessage.__table__.delete().where(
                        ChatMessage.session_id == session_id
                    )
                )
                await db.execute(
                    ChatSession.__table__.delete().where(
                        ChatSession.id == session_id
                    )
                )
                await db.commit()

from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from backend.app.services.message_service import save_message, get_session_messages


@pytest.mark.anyio
async def test_save_message_saves_and_returns_message():
    db = MagicMock()
    db.add = MagicMock()
    db.commit = AsyncMock()
    db.refresh = AsyncMock()
    session_id = uuid4()

    message = await save_message(
        db=db,
        session_id=session_id,
        role="user",
        content="How do I improve product growth?",
    )

    db.add.assert_called_once_with(message)
    db.commit.assert_awaited_once()
    db.refresh.assert_awaited_once_with(message)

    assert message.session_id == session_id
    assert message.role == "user"
    assert message.content == "How do I improve product growth?"
    assert message.message_metadata == {}


@pytest.mark.anyio
async def test_save_message_preserves_metadata():
    db = MagicMock()
    db.add = MagicMock()
    db.commit = AsyncMock()
    db.refresh = AsyncMock()

    metadata = {"provider": "local", "sources": []}

    message = await save_message(
        db=db,
        session_id=uuid4(),
        role="assistant",
        content="Focus on customer retention.",
        message_metadata=metadata,
    )

    assert message.message_metadata == metadata


@pytest.mark.anyio
async def test_save_message_rejects_invalid_role():
    db = MagicMock()

    with pytest.raises(ValueError, match="role must be user, assistant, or system"):
        await save_message(
            db=db,
            session_id=uuid4(),
            role="admin",
            content="Invalid role",
        )

    db.add.assert_not_called()
    db.commit = AsyncMock()
    db.commit.assert_not_awaited()


@pytest.mark.anyio
async def test_get_session_messages_returns_messages():
    first_message = MagicMock()
    second_message = MagicMock()

    scalars = MagicMock()
    scalars.all.return_value = [first_message, second_message]

    result = MagicMock()
    result.scalars.return_value = scalars

    db = MagicMock()
    db.execute = AsyncMock(return_value=result)

    messages = await get_session_messages(db, uuid4())

    db.execute.assert_awaited_once()
    assert messages == [first_message, second_message]


@pytest.mark.anyio
async def test_get_session_messages_returns_empty_list():
    scalars = MagicMock()
    scalars.all.return_value = []

    result = MagicMock()
    result.scalars.return_value = scalars

    db = MagicMock()
    db.execute = AsyncMock(return_value=result)

    messages = await get_session_messages(db, uuid4())

    assert messages == []

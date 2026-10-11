
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from backend.app.services.session_service import create_session, get_session


@pytest.mark.anyio
async def test_create_session_saves_and_returns_session():
    db = MagicMock()
    db.add = MagicMock()
    db.commit = AsyncMock()
    db.refresh = AsyncMock()

    session = await create_session(
        db=db,
        title="Product growth",
        user_metadata={"provider": "local"},
    )

    db.add.assert_called_once_with(session)
    db.commit.assert_awaited_once()
    db.refresh.assert_awaited_once_with(session)

    assert session.title == "Product growth"
    assert session.user_metadata == {"provider": "local"}


@pytest.mark.anyio
async def test_get_session_returns_matching_session():
    expected_session = MagicMock()
    db = MagicMock()
    result = MagicMock()
    result.scalar_one_or_none.return_value = expected_session
    db.execute = AsyncMock(return_value=result)

    actual_session = await get_session(db, uuid4())

    db.execute.assert_awaited_once()
    assert actual_session is expected_session


@pytest.mark.anyio
async def test_get_session_returns_none_when_not_found():
    db = MagicMock()
    result = MagicMock()
    result.scalar_one_or_none.return_value = None
    db.execute = AsyncMock(return_value=result)

    actual_session = await get_session(db, uuid4())

    db.execute.assert_awaited_once()
    assert actual_session is None

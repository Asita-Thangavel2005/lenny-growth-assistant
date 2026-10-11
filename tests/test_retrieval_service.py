from unittest.mock import AsyncMock, MagicMock

import pytest

from backend.app.services import retrieval_service


@pytest.mark.anyio
async def test_retrieval_returns_chunks_above_similarity_threshold(monkeypatch):
    relevant_chunk = MagicMock()
    another_chunk = MagicMock()
    irrelevant_chunk = MagicMock()

    result = MagicMock()
    result.all.return_value = [
        (relevant_chunk, 0.15),
        (another_chunk, 0.35),
        (irrelevant_chunk, 0.65),
    ]

    db = MagicMock()
    db.execute = AsyncMock(return_value=result)

    monkeypatch.setattr(
        retrieval_service,
        "embed_text",
        lambda query: [0.1, 0.2, 0.3],
    )

    chunks = await retrieval_service.retrieve_relevant_chunks(
        db=db,
        query="How can a company improve retention?",
        top_k=3,
    )

    assert chunks == [relevant_chunk, another_chunk]
    db.execute.assert_awaited_once()


@pytest.mark.anyio
async def test_retrieval_returns_empty_list_when_no_chunks_meet_threshold(
    monkeypatch,
):
    result = MagicMock()
    result.all.return_value = [
        (MagicMock(), 0.70),
        (MagicMock(), 0.80),
    ]

    db = MagicMock()
    db.execute = AsyncMock(return_value=result)

    monkeypatch.setattr(
        retrieval_service,
        "embed_text",
        lambda query: [0.1, 0.2, 0.3],
    )

    chunks = await retrieval_service.retrieve_relevant_chunks(
        db=db,
        query="A completely unrelated question",
        top_k=2,
    )

    assert chunks == []


@pytest.mark.anyio
async def test_retrieval_rejects_empty_query():
    db = MagicMock()

    with pytest.raises(ValueError, match="Query cannot be empty."):
        await retrieval_service.retrieve_relevant_chunks(
            db=db,
            query="   ",
        )

    db.execute = AsyncMock()
    db.execute.assert_not_awaited()


@pytest.mark.anyio
async def test_retrieval_rejects_invalid_top_k():
    db = MagicMock()

    with pytest.raises(ValueError, match="top_k must be at least 1."):
        await retrieval_service.retrieve_relevant_chunks(
            db=db,
            query="Improve product retention",
            top_k=0,
        )

    db.execute = AsyncMock()
    db.execute.assert_not_awaited()


@pytest.mark.anyio
async def test_retrieval_uses_configured_top_k_when_not_provided(monkeypatch):
    result = MagicMock()
    result.all.return_value = []

    db = MagicMock()
    db.execute = AsyncMock(return_value=result)

    monkeypatch.setattr(retrieval_service, "embed_text", lambda query: [0.1])
    monkeypatch.setattr(retrieval_service.settings, "retrieval_top_k", 7)

    await retrieval_service.retrieve_relevant_chunks(
        db=db,
        query="Improve product retention",
    )

    statement = db.execute.await_args.args[0]
    assert statement._limit_clause.value == 7
